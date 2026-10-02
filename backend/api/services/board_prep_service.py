"""25-day board plan: day number, question targets, review queue, last-48h sheet."""

from __future__ import annotations

from datetime import date, timedelta

from django.db.models import Q
from django.utils import timezone

from api.data.board_prep_plan import (
    BOARD_PREP_DAYS,
    DAY_OFF_QUESTION_TARGET,
    DEFAULT_WORK_WEEKDAYS,
    MORNING_QUESTION_COUNT,
    PLAN_LENGTH_DAYS,
    TARGET_MAX_QUESTIONS,
    TARGET_MIN_QUESTIONS,
    WORKDAY_QUESTION_TARGET,
    day_spec,
)
from api.models import Answer, BoardPrepSettings, Chapter, Last48HourFact, Question, Topic


def _normalize_weekdays(raw) -> list[int]:
    if not isinstance(raw, list) or not raw:
        return list(DEFAULT_WORK_WEEKDAYS)
    values = []
    for item in raw:
        try:
            day = int(item)
        except (TypeError, ValueError):
            continue
        if 1 <= day <= 7:
            values.append(day)
    return values or list(DEFAULT_WORK_WEEKDAYS)


def get_or_create_settings(user) -> BoardPrepSettings:
    settings, created = BoardPrepSettings.objects.get_or_create(
        user=user,
        defaults={"work_weekdays": list(DEFAULT_WORK_WEEKDAYS)},
    )
    if created or not settings.work_weekdays:
        settings.work_weekdays = list(DEFAULT_WORK_WEEKDAYS)
        settings.save(update_fields=["work_weekdays"])
    return settings


def save_settings(user, *, exam_date=None, work_weekdays=None) -> BoardPrepSettings:
    settings = get_or_create_settings(user)
    if exam_date:
        settings.exam_date = exam_date
        settings.start_date = exam_date - timedelta(days=PLAN_LENGTH_DAYS - 1)
    if work_weekdays is not None:
        settings.work_weekdays = _normalize_weekdays(work_weekdays)
    settings.save()
    return settings


def plan_day_number(settings: BoardPrepSettings, today: date | None = None) -> int:
    today = today or date.today()
    if settings.exam_date:
        days_left = (settings.exam_date - today).days
        if days_left < 0:
            return PLAN_LENGTH_DAYS
        day = PLAN_LENGTH_DAYS - days_left
        return max(1, min(PLAN_LENGTH_DAYS, day))
    if settings.start_date:
        elapsed = (today - settings.start_date).days + 1
        return max(1, min(PLAN_LENGTH_DAYS, elapsed))
    return 1


def is_workday(settings: BoardPrepSettings, today: date | None = None) -> bool:
    today = today or date.today()
    weekdays = _normalize_weekdays(settings.work_weekdays)
    return today.isoweekday() in weekdays


def question_target(settings: BoardPrepSettings, today: date | None = None) -> int:
    if is_workday(settings, today):
        return settings.workday_question_target or WORKDAY_QUESTION_TARGET
    return settings.day_off_question_target or DAY_OFF_QUESTION_TARGET


def _chapter_map(slugs: list[str]) -> list[dict]:
    if not slugs:
        return []
    chapters = Chapter.objects.filter(slug__in=slugs)
    by_slug = {c.slug: c for c in chapters}
    result = []
    for slug in slugs:
        chapter = by_slug.get(slug)
        if chapter:
            result.append({"id": str(chapter.id), "slug": chapter.slug, "title": chapter.title})
    return result


def serialize_day(spec: dict, settings: BoardPrepSettings, today: date | None = None) -> dict:
    chapters = _chapter_map(spec.get("chapter_slugs") or [])
    return {
        "day": spec["day"],
        "focus": spec["focus"],
        "high_yield": spec.get("high_yield") or [],
        "chapter_slugs": spec.get("chapter_slugs") or [],
        "chapters": chapters,
        "topic_slugs": spec.get("topic_slugs") or [],
        "mixed": bool(spec.get("mixed")),
        "review_only": bool(spec.get("review_only")),
        "repetition": bool(spec.get("repetition")),
        "question_target": question_target(settings, today),
        "morning_questions": MORNING_QUESTION_COUNT,
        "evening": "Review explanations + incorrect/guessed items; focused topic if not exhausted",
    }


def classification_counts(user, since: date | None = None) -> dict:
    answers = Answer.objects.filter(quiz_attempt__user=user)
    if since:
        answers = answers.filter(quiz_attempt__completed_at__date__gte=since)
    total = answers.count()
    wrong = answers.filter(is_correct=False).count()
    guessed = answers.filter(is_correct=True, confidence="guessed").count()
    know = answers.filter(is_correct=True).exclude(confidence="guessed").count()
    return {"total": total, "know": know, "guessed": guessed, "wrong": wrong}


def today_answered_count(user, today: date | None = None) -> int:
    today = today or date.today()
    return Answer.objects.filter(
        quiz_attempt__user=user,
        quiz_attempt__completed_at__date=today,
    ).count()


def plan_answered_count(user, settings: BoardPrepSettings) -> int:
    since = settings.start_date
    if settings.exam_date and not since:
        since = settings.exam_date - timedelta(days=PLAN_LENGTH_DAYS - 1)
    qs = Answer.objects.filter(quiz_attempt__user=user)
    if since:
        qs = qs.filter(quiz_attempt__completed_at__date__gte=since)
    return qs.count()


def build_plan_payload(user, today: date | None = None) -> dict:
    today = today or date.today()
    settings = get_or_create_settings(user)
    day_number = plan_day_number(settings, today)
    spec = day_spec(day_number)
    days_until_exam = None
    if settings.exam_date:
        days_until_exam = (settings.exam_date - today).days
    counts = classification_counts(user, since=settings.start_date)
    return {
        "exam_date": settings.exam_date.isoformat() if settings.exam_date else None,
        "start_date": settings.start_date.isoformat() if settings.start_date else None,
        "work_weekdays": _normalize_weekdays(settings.work_weekdays),
        "workday_question_target": settings.workday_question_target,
        "day_off_question_target": settings.day_off_question_target,
        "plan_length_days": PLAN_LENGTH_DAYS,
        "target_min": TARGET_MIN_QUESTIONS,
        "target_max": TARGET_MAX_QUESTIONS,
        "today": today.isoformat(),
        "day_number": day_number,
        "days_until_exam": days_until_exam,
        "is_workday": is_workday(settings, today),
        "today_answered": today_answered_count(user, today),
        "questions_in_plan": plan_answered_count(user, settings),
        "classification": counts,
        "today_session": serialize_day(spec, settings, today),
        "days": [serialize_day(item, settings, today) for item in BOARD_PREP_DAYS],
        "method": (
            "Classify each question Know / Guessed / Wrong. Review wrong and guessed-correct. "
            "Workdays: ~2–2.5h (AM 15–20 questions, PM review). Days off: 60–100 questions. "
            "Quality of review beats raw count."
        ),
    }


def review_queryset(user, tag: str | None = None):
    qs = Answer.objects.filter(quiz_attempt__user=user).select_related(
        "question",
        "question__chapter",
        "chosen_choice",
        "quiz_attempt",
    ).prefetch_related("question__choices")
    if tag == "wrong":
        qs = qs.filter(is_correct=False)
    elif tag == "guessed":
        qs = qs.filter(is_correct=True, confidence="guessed")
    elif tag == "know":
        qs = qs.filter(is_correct=True).exclude(confidence="guessed")
    elif tag == "review":
        qs = qs.filter(Q(is_correct=False) | Q(confidence="guessed"))
    return qs.order_by("-quiz_attempt__completed_at", "-id")


def serialize_review_item(answer: Answer) -> dict:
    question = answer.question
    correct = question.choices.filter(is_correct=True).first() if question else None
    return {
        "id": str(answer.id),
        "question_id": str(question.id) if question else "",
        "tag": answer.review_tag,
        "confidence": answer.confidence,
        "is_correct": answer.is_correct,
        "question_text": question.question_text if question else "",
        "case_text": question.case_text if question else "",
        "chosen_text": answer.chosen_choice.choice_text if answer.chosen_choice_id else "",
        "correct_text": correct.choice_text if correct else "",
        "explanation": question.explanation if question else "",
        "clinical_pearl": question.clinical_pearl if question else "",
        "chapter_slug": question.chapter.slug if question and question.chapter_id else "",
        "chapter_title": question.chapter.title if question and question.chapter_id else "",
        "answered_at": answer.quiz_attempt.completed_at.isoformat()
        if answer.quiz_attempt_id and answer.quiz_attempt.completed_at
        else None,
    }


def last48_cutoff():
    return timezone.now() - timedelta(hours=48)


def kind_for_question(question: Question) -> str:
    slug = question.chapter.slug if question.chapter_id else ""
    text = f"{question.clinical_pearl} {question.explanation}".lower()
    if "transplant" in slug or "dsa" in text or "c4d" in text:
        return Last48HourFact.Kind.TRANSPLANT
    if "dialysis" in slug or "crrt" in slug or "kt/v" in text:
        return Last48HourFact.Kind.DIALYSIS
    if "electrolyte" in slug or "hyponatremia" in text or "hyperkalemia" in text:
        return Last48HourFact.Kind.ELECTROLYTE
    if "formula" in text or "winter" in text or "anion gap" in text:
        return Last48HourFact.Kind.FORMULA
    if "biopsy" in text or "if " in text or "electron" in text:
        return Last48HourFact.Kind.BIOPSY
    if "toxicity" in text or "poison" in text or "nephrotox" in text:
        return Last48HourFact.Kind.TOXICITY
    if not question.clinical_pearl:
        return Last48HourFact.Kind.MISS
    return Last48HourFact.Kind.PEARL


def maybe_add_last48_fact(user, question: Question, *, is_correct: bool, confidence: str) -> None:
    if is_correct and confidence != "guessed":
        return
    text = (question.clinical_pearl or question.explanation or "").strip()
    if not text:
        return
    cutoff = last48_cutoff()
    exists = Last48HourFact.objects.filter(
        user=user, source_question=question, created_at__gte=cutoff
    ).exists()
    if exists:
        return
    Last48HourFact.objects.create(
        user=user,
        kind=kind_for_question(question),
        text=text[:2000],
        source_question=question,
    )


def last48_payload(user) -> dict:
    cutoff = last48_cutoff()
    facts = list(
        Last48HourFact.objects.filter(user=user, created_at__gte=cutoff).select_related(
            "source_question"
        )
    )
    return {
        "since": cutoff.isoformat(),
        "items": [
            {
                "id": str(f.id),
                "kind": f.kind,
                "text": f.text,
                "source_question_id": str(f.source_question_id) if f.source_question_id else None,
                "created_at": f.created_at.isoformat(),
            }
            for f in facts
        ],
    }


def questions_for_day(user, spec: dict, limit: int):
    from api.services.board_exam_service import exclude_board_exam_questions

    qs = exclude_board_exam_questions(
        Question.objects.filter(is_published=True, is_premium=False)
    ).prefetch_related("choices")
    if getattr(user, "role", "") in ("premium", "admin"):
        qs = exclude_board_exam_questions(
            Question.objects.filter(is_published=True)
        ).prefetch_related("choices")
    if spec.get("review_only"):
        answer_ids = list(
            review_queryset(user, tag="review")
            .values_list("question_id", flat=True)
            .distinct()[:limit]
        )
        if not answer_ids:
            return []
        return list(qs.filter(id__in=answer_ids).order_by("?"))
    slugs = spec.get("chapter_slugs") or []
    topic_slugs = spec.get("topic_slugs") or []
    if topic_slugs:
        topics = Topic.objects.filter(slug__in=topic_slugs)
        topic_qs = qs.filter(topic__in=topics)
        if topic_qs.exists():
            return list(topic_qs.order_by("?")[:limit])
    if slugs and not spec.get("mixed"):
        chapters = Chapter.objects.filter(slug__in=slugs)
        chapter_qs = qs.filter(chapter__in=chapters)
        if chapter_qs.exists():
            return list(chapter_qs.order_by("?")[:limit])
    return list(qs.order_by("?")[:limit])
