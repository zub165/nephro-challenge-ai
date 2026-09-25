import random
import re
import unicodedata
from collections import defaultdict
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from api.models import (
    BoardExam,
    BoardExamAttempt,
    BoardExamAttemptItem,
    Question,
)

MIN_CHOICES_PER_QUESTION = 2
MAX_CHOICES_PER_QUESTION = 6
DEFAULT_QUESTION_COUNT = 50
DEFAULT_DURATION_MINUTES = 60
FORBIDDEN_ACTIVE_ITEM_KEYS = (
    "is_correct",
    "correct_choice_key",
    "correct_answer",
    "explanation",
    "clinical_pearl",
    "pearl",
    "reference",
    "references",
    "why_wrong",
)


class BoardExamError(Exception):
    status_code = 400
    default_message = "Board exam request could not be processed"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class ExamNotPublished(BoardExamError):
    status_code = 404
    default_message = "Board exam not found"


class InsufficientQuestionPool(BoardExamError):
    status_code = 409
    default_message = "Not enough eligible questions for this exam"


class AttemptFinalized(BoardExamError):
    status_code = 409
    default_message = "Board exam attempt is already finalized"


class AttemptExpired(BoardExamError):
    status_code = 410
    default_message = "Board exam attempt has expired"


class AttemptNotFound(BoardExamError):
    status_code = 404
    default_message = "Board exam attempt not found"


class AttemptInProgress(BoardExamError):
    status_code = 409
    default_message = "Board exam attempt is still in progress"


class ItemNotFound(BoardExamError):
    status_code = 404
    default_message = "Board exam question not found"


class InvalidChoice(BoardExamError):
    status_code = 400
    default_message = "selected_choice_key is not valid for this question"


def _rng() -> random.Random:
    return random.SystemRandom()


def exclude_board_exam_questions(queryset):
    return queryset.exclude(board_exams__is_published=True)


def question_in_published_board_exam(question: Question) -> bool:
    return question.board_exams.filter(is_published=True).exists()


def normalize_stem(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "").lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def chapter_quota_map(exam: BoardExam) -> dict[str, int]:
    raw = exam.chapter_quota
    entries: list[tuple[object, object]] = []
    if isinstance(raw, dict):
        entries = list(raw.items())
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                slug = item.get("chapter") or item.get("slug") or item.get("chapter_slug")
                count = item.get("count", item.get("quota"))
                entries.append((slug, count))
    quota: dict[str, int] = {}
    for slug, value in entries:
        if not isinstance(slug, str) or not slug.strip():
            continue
        try:
            count = int(value)
        except (TypeError, ValueError):
            continue
        if count > 0:
            quota[slug.strip()] = count
    return quota


def question_is_exam_eligible(question: Question) -> bool:
    choices = list(question.choices.all())
    if not MIN_CHOICES_PER_QUESTION <= len(choices) <= MAX_CHOICES_PER_QUESTION:
        return False
    if any(not (choice.choice_text or "").strip() for choice in choices):
        return False
    return sum(1 for choice in choices if choice.is_correct) == 1


def eligible_exam_questions(exam: BoardExam) -> list[Question]:
    queryset = (
        Question.objects.filter(pk__in=exam.questions.values("pk"), is_published=True)
        .select_related("category", "chapter", "topic")
        .prefetch_related("choices")
        .order_by("pk")
    )
    eligible: list[Question] = []
    seen_stems: set[str] = set()
    for question in queryset:
        if not question_is_exam_eligible(question):
            continue
        stem = normalize_stem(question.question_text)
        if not stem or stem in seen_stems:
            continue
        seen_stems.add(stem)
        eligible.append(question)
    return eligible


def exam_question_target(exam: BoardExam) -> int:
    return exam.question_count if exam.question_count and exam.question_count > 0 else DEFAULT_QUESTION_COUNT


def exam_duration_minutes(exam: BoardExam) -> int:
    return exam.duration_minutes if exam.duration_minutes and exam.duration_minutes > 0 else DEFAULT_DURATION_MINUTES


def select_exam_questions(exam: BoardExam, *, rng: random.Random | None = None) -> list[Question]:
    generator = rng or _rng()
    pool = eligible_exam_questions(exam)
    target = exam_question_target(exam)
    if len(pool) < target:
        raise InsufficientQuestionPool(
            f"Exam needs {target} questions but only {len(pool)} eligible questions are available"
        )

    by_chapter: dict[str, list[Question]] = defaultdict(list)
    for question in pool:
        by_chapter[question.chapter.slug if question.chapter_id else ""].append(question)

    selected: list[Question] = []
    selected_ids: set[int] = set()
    for slug, quota in chapter_quota_map(exam).items():
        if len(selected) >= target:
            break
        candidates = by_chapter.get(slug, [])
        if not candidates:
            continue
        needed = min(quota, target - len(selected))
        for question in generator.sample(candidates, min(needed, len(candidates))):
            if question.pk in selected_ids:
                continue
            selected.append(question)
            selected_ids.add(question.pk)

    if len(selected) < target:
        remaining = [question for question in pool if question.pk not in selected_ids]
        deficit = target - len(selected)
        for question in generator.sample(remaining, min(deficit, len(remaining))):
            if question.pk in selected_ids:
                continue
            selected.append(question)
            selected_ids.add(question.pk)

    if len(selected) < target:
        raise InsufficientQuestionPool(
            f"Exam needs {target} questions but only {len(selected)} could be assembled"
        )

    generator.shuffle(selected)
    return selected


def build_public_snapshot(question: Question) -> dict:
    return {
        "question_text": question.question_text,
        "case_text": question.case_text or "",
        "labs": question.labs or {},
        "difficulty": question.difficulty,
        "subcategory": question.subcategory or "",
        "category_name": question.category.name if question.category_id else "",
        "chapter_name": question.chapter.title if question.chapter_id else "",
        "chapter_slug": question.chapter.slug if question.chapter_id else "",
        "topic_title": question.topic.title if question.topic_id else "",
        "choices": [
            {
                "choice_key": choice.choice_key,
                "choice_text": choice.choice_text,
                "order": choice.order,
            }
            for choice in question.choices.all()
        ],
    }


def build_solution_snapshot(question: Question) -> dict:
    correct = next((choice for choice in question.choices.all() if choice.is_correct), None)
    return {
        "correct_choice_key": correct.choice_key if correct else "",
        "explanation": question.explanation or "",
        "clinical_pearl": question.clinical_pearl or "",
        "reference": question.reference or "",
        "choices": {
            choice.choice_key: {
                "choice_text": choice.choice_text,
                "why_wrong": choice.why_wrong or "",
            }
            for choice in question.choices.all()
        },
    }


def attempt_duration_seconds(attempt: BoardExamAttempt) -> int:
    if not attempt.deadline or not attempt.started_at:
        return 0
    return max(0, int((attempt.deadline - attempt.started_at).total_seconds()))


def answered_count(attempt: BoardExamAttempt) -> int:
    return attempt.items.exclude(selected_choice_key="").count()


def remaining_seconds(attempt: BoardExamAttempt, now=None) -> int:
    if not attempt.deadline:
        return 0
    now = now or timezone.now()
    return max(0, int((attempt.deadline - now).total_seconds()))


def _grade_items(items) -> tuple[int, int]:
    correct = 0
    for item in items:
        solution = item.solution_snapshot if isinstance(item.solution_snapshot, dict) else {}
        answer_key = (solution.get("correct_choice_key") or "").strip()
        selected = (item.selected_choice_key or "").strip()
        if answer_key and selected == answer_key:
            correct += 1
    return correct, len(items)


def _finalize_attempt(
    attempt: BoardExamAttempt,
    *,
    status: str,
    now,
) -> BoardExamAttempt:
    with transaction.atomic():
        locked = BoardExamAttempt.objects.select_for_update().select_related("exam").get(pk=attempt.pk)
        if locked.status != BoardExamAttempt.Status.IN_PROGRESS:
            return locked
        items = list(BoardExamAttemptItem.objects.filter(attempt=locked).order_by("position"))
        correct, total = _grade_items(items)
        elapsed = max(0, int((now - locked.started_at).total_seconds()))
        limit = attempt_duration_seconds(locked)
        if limit:
            elapsed = min(elapsed, limit)
        locked.status = status
        locked.finalized_at = now
        locked.correct_count = correct
        locked.total_questions = total
        locked.score = round((correct / total) * 100, 1) if total else 0.0
        locked.time_taken_seconds = elapsed
        locked.save(
            update_fields=[
                "status",
                "finalized_at",
                "correct_count",
                "total_questions",
                "score",
                "time_taken_seconds",
                "updated_at",
            ]
        )
    return locked


def expire_attempt_if_needed(attempt: BoardExamAttempt, *, now=None) -> bool:
    now = now or timezone.now()
    if attempt.status != BoardExamAttempt.Status.IN_PROGRESS:
        return False
    if not attempt.deadline or now < attempt.deadline:
        return False
    _finalize_attempt(attempt, status=BoardExamAttempt.Status.EXPIRED, now=now)
    return True


def get_active_attempt(user, exam: BoardExam) -> BoardExamAttempt | None:
    attempt = (
        BoardExamAttempt.objects.select_related("exam")
        .filter(user=user, exam=exam, status=BoardExamAttempt.Status.IN_PROGRESS)
        .order_by("-started_at")
        .first()
    )
    if attempt is None:
        return None
    if expire_attempt_if_needed(attempt):
        attempt.refresh_from_db()
    return attempt


def latest_attempt(user, exam: BoardExam) -> BoardExamAttempt | None:
    return (
        BoardExamAttempt.objects.select_related("exam")
        .filter(user=user, exam=exam)
        .order_by("-created_at")
        .first()
    )


def start_or_resume_attempt(user, exam: BoardExam, *, now=None) -> tuple[BoardExamAttempt, bool]:
    now = now or timezone.now()
    if not exam.is_published:
        raise ExamNotPublished()
    existing = get_active_attempt(user, exam)
    if existing is not None and existing.status == BoardExamAttempt.Status.IN_PROGRESS:
        return existing, True
    try:
        with transaction.atomic():
            questions = select_exam_questions(exam)
            attempt = BoardExamAttempt.objects.create(
                user=user,
                exam=exam,
                started_at=now,
                deadline=now + timedelta(minutes=exam_duration_minutes(exam)),
                total_questions=len(questions),
            )
            BoardExamAttemptItem.objects.bulk_create(
                [
                    BoardExamAttemptItem(
                        attempt=attempt,
                        question=question,
                        position=index,
                        public_snapshot=build_public_snapshot(question),
                        solution_snapshot=build_solution_snapshot(question),
                    )
                    for index, question in enumerate(questions, start=1)
                ]
            )
    except IntegrityError:
        resumed = get_active_attempt(user, exam)
        if resumed is None:
            raise
        return resumed, True
    return attempt, False


def record_answer(
    attempt: BoardExamAttempt,
    position: int,
    choice_key: str,
    *,
    now=None,
) -> BoardExamAttemptItem:
    now = now or timezone.now()
    if attempt.status != BoardExamAttempt.Status.IN_PROGRESS:
        if attempt.status == BoardExamAttempt.Status.EXPIRED:
            raise AttemptExpired()
        raise AttemptFinalized()
    if attempt.deadline and now >= attempt.deadline:
        _finalize_attempt(attempt, status=BoardExamAttempt.Status.EXPIRED, now=now)
        raise AttemptExpired()
    item = BoardExamAttemptItem.objects.filter(attempt=attempt, position=position).first()
    if item is None:
        raise ItemNotFound()
    selected = (choice_key or "").strip()
    if not selected:
        raise InvalidChoice("selected_choice_key is required")
    public = item.public_snapshot if isinstance(item.public_snapshot, dict) else {}
    allowed = {
        (choice or {}).get("choice_key")
        for choice in public.get("choices", [])
        if isinstance(choice, dict)
    }
    if selected not in allowed:
        raise InvalidChoice()
    item.selected_choice_key = selected
    item.answered_at = now
    item.save(update_fields=["selected_choice_key", "answered_at"])
    return item


def submit_attempt(attempt: BoardExamAttempt, *, now=None) -> BoardExamAttempt:
    now = now or timezone.now()
    if attempt.status != BoardExamAttempt.Status.IN_PROGRESS:
        return attempt
    if attempt.deadline and now >= attempt.deadline:
        return _finalize_attempt(attempt, status=BoardExamAttempt.Status.EXPIRED, now=now)
    return _finalize_attempt(attempt, status=BoardExamAttempt.Status.SUBMITTED, now=now)


def build_exam_payload(exam: BoardExam) -> dict:
    return {
        "id": str(exam.pk),
        "slug": exam.slug,
        "title": exam.title,
        "question_count": exam.question_count,
        "duration_minutes": exam.duration_minutes,
    }


def build_attempt_payload(attempt: BoardExamAttempt, *, now=None, resumed=None) -> dict:
    now = now or timezone.now()
    items = list(BoardExamAttemptItem.objects.filter(attempt=attempt).order_by("position"))
    answered = sum(1 for item in items if (item.selected_choice_key or "").strip())
    payload = {
        "attempt_id": str(attempt.pk),
        "exam": build_exam_payload(attempt.exam),
        "status": attempt.status,
        "total_questions": attempt.total_questions,
        "answered_count": answered,
        "unanswered_count": len(items) - answered,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "deadline": attempt.deadline.isoformat() if attempt.deadline else None,
        "remaining_seconds": remaining_seconds(attempt, now),
        "server_time": now.isoformat(),
        "items": [
            {
                "id": str(item.pk),
                "position": item.position,
                "question": item.public_snapshot or {},
                "selected_choice_key": item.selected_choice_key or None,
                "answered_at": item.answered_at.isoformat() if item.answered_at else None,
            }
            for item in items
        ],
    }
    if resumed is not None:
        payload["resumed"] = resumed
    return payload


def _resolve_references(public: dict, solution: dict) -> list:
    from api.data.medical_references import references_for_topic, resolve_reference_field

    refs = resolve_reference_field(solution.get("reference") or "")
    if not refs:
        topic = public.get("topic_title") or public.get("subcategory") or ""
        refs = references_for_topic(topic, public.get("chapter_slug") or None)
    return refs


def build_result_payload(attempt: BoardExamAttempt, *, now=None) -> dict:
    now = now or timezone.now()
    if attempt.status == BoardExamAttempt.Status.IN_PROGRESS:
        if expire_attempt_if_needed(attempt, now=now):
            attempt.refresh_from_db()
        if attempt.status == BoardExamAttempt.Status.IN_PROGRESS:
            raise AttemptInProgress()
    items = list(BoardExamAttemptItem.objects.filter(attempt=attempt).order_by("position"))
    correct, total = _grade_items(items)
    rows = []
    answered = 0
    for item in items:
        public = item.public_snapshot if isinstance(item.public_snapshot, dict) else {}
        solution = item.solution_snapshot if isinstance(item.solution_snapshot, dict) else {}
        selected = (item.selected_choice_key or "").strip()
        answer_key = (solution.get("correct_choice_key") or "").strip()
        is_correct = bool(selected) and selected == answer_key
        is_answered = bool(selected)
        if is_answered:
            answered += 1
        notes = solution.get("choices") or {}
        why_wrong = ""
        if is_answered and not is_correct:
            why_wrong = (notes.get(selected) or {}).get("why_wrong", "")
        rows.append(
            {
                "id": str(item.pk),
                "position": item.position,
                "question": public,
                "selected_choice_key": selected or None,
                "correct_choice_key": answer_key or None,
                "is_correct": is_correct,
                "is_answered": is_answered,
                "why_wrong": why_wrong,
                "explanation": solution.get("explanation", ""),
                "clinical_pearl": solution.get("clinical_pearl", ""),
                "references": _resolve_references(public, solution),
                "answered_at": item.answered_at.isoformat() if item.answered_at else None,
            }
        )
    percentage = round((correct / total) * 100, 1) if total else 0.0
    return {
        "attempt_id": str(attempt.pk),
        "exam": build_exam_payload(attempt.exam),
        "status": attempt.status,
        "correct_count": correct,
        "total_questions": total,
        "answered_count": answered,
        "unanswered_count": total - answered,
        "score": percentage,
        "percentage": percentage,
        "time_taken_seconds": attempt.time_taken_seconds,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "deadline": attempt.deadline.isoformat() if attempt.deadline else None,
        "finalized_at": attempt.finalized_at.isoformat() if attempt.finalized_at else None,
        "server_time": now.isoformat(),
        "items": rows,
    }


def payload_contains_answer_leakage(payload) -> list[str]:
    leaks: list[str] = []

    def walk(node, path: str):
        if isinstance(node, dict):
            for key, value in node.items():
                child = f"{path}.{key}" if path else key
                if key.lower() in FORBIDDEN_ACTIVE_ITEM_KEYS:
                    leaks.append(child)
                walk(value, child)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk(payload, "")
    return leaks
