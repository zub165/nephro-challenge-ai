"""Idempotent seeding helpers for the nephrology curriculum and board exam.

Both `seed_data` and `seed_board_exam` use these helpers so a chapter, lesson,
question, or choice is created once and then updated in place. Every seeded row
records its provenance in `source_metadata` and starts in the `needs_review`
medical review state, because the content is original teaching material that
still requires clinician sign-off.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from api.data.board_exam_seed import (
    BOARD_EXAM_CHAPTER_QUOTA_PER_CHAPTER,
    BOARD_EXAM_DESCRIPTION,
    BOARD_EXAM_DURATION_MINUTES,
    BOARD_EXAM_QUESTION_COUNT,
    BOARD_EXAM_SLUG,
    BOARD_EXAM_TITLE,
    CHAPTER_QUOTA,
    SEED_AUTHOR,
    SEED_REVIEW_NOTE,
    SEED_REVIEW_STATUS,
)
from api.data.chapter_seed import CHAPTERS
from api.data.medical_references import reference_ids_to_storage, resolve_references
from api.models import (
    BoardExam,
    Category,
    Chapter,
    Choice,
    Lesson,
    Question,
    ReviewStatus,
    Topic,
)

ELIGIBLE_REVIEW_STATUSES = (
    ReviewStatus.NEEDS_REVIEW,
    ReviewStatus.IN_REVIEW,
    ReviewStatus.APPROVED,
)

PUBLISHABLE_REVIEW_STATUSES = (ReviewStatus.APPROVED,)


class BoardExamPublishBlocked(Exception):
    """Raised when publication is requested before clinician review is complete."""

    def __init__(self, deficient: dict[str, tuple[int, int]]):
        self.deficient = deficient
        detail = ", ".join(
            f"{slug} ({approved}/{quota} approved)" for slug, (approved, quota) in sorted(deficient.items())
        )
        super().__init__(f"Cannot publish: chapters below approved quota -> {detail}")

DEFAULT_CATEGORIES: list[dict[str, Any]] = [
    {
        "name": "Glomerular Diseases",
        "description": "Diseases affecting the glomeruli including nephrotic and nephritic syndromes.",
        "icon": "filter",
        "order": 1,
    },
    {
        "name": "Acute Kidney Injury",
        "description": "Sudden loss of kidney function, including prerenal, intrinsic, and postrenal causes.",
        "icon": "alert-triangle",
        "order": 2,
    },
    {
        "name": "Chronic Kidney Disease",
        "description": "Progressive loss of kidney function over months to years.",
        "icon": "clock",
        "order": 3,
    },
    {
        "name": "Electrolyte Disorders",
        "description": "Disorders of sodium, potassium, calcium, phosphate, and magnesium homeostasis.",
        "icon": "activity",
        "order": 4,
    },
    {
        "name": "Acid-Base Disorders",
        "description": "Metabolic and respiratory acid-base disturbances.",
        "icon": "thermometer",
        "order": 5,
    },
    {
        "name": "Hypertension",
        "description": "Primary and secondary hypertension, including renovascular disease.",
        "icon": "heart",
        "order": 6,
    },
    {
        "name": "Dialysis",
        "description": "Hemodialysis and peritoneal dialysis principles and complications.",
        "icon": "repeat",
        "order": 7,
    },
    {
        "name": "Transplantation",
        "description": "Kidney transplantation immunology, immunosuppression, and complications.",
        "icon": "shuffle",
        "order": 8,
    },
    {
        "name": "Tubulointerstitial Diseases",
        "description": "Diseases affecting renal tubules and interstitium, including cystic disease.",
        "icon": "box",
        "order": 9,
    },
    {
        "name": "Pharmacology",
        "description": "Drug dosing in kidney disease, nephrotoxic medications, and diuretics.",
        "icon": "pill",
        "order": 10,
    },
]


def content_fingerprint(content: dict[str, Any]) -> str:
    """Stable digest of seeded content, used to detect edits that need re-review."""
    canonical = json.dumps(content, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _review_fields(existing, fingerprint: str) -> dict[str, Any]:
    """Keep clinician sign-off only while the seeded content is unchanged.

    Any edit to the seeded content invalidates prior sign-off, so the row returns
    to `needs_review` with the reviewer attribution cleared.
    """
    previous = (existing.source_metadata or {}).get("content_fingerprint")
    if previous == fingerprint and existing.review_status != ReviewStatus.NEEDS_REVIEW:
        return {
            "review_status": existing.review_status,
            "reviewed_by": existing.reviewed_by,
            "reviewed_at": existing.reviewed_at,
        }
    return {
        "review_status": SEED_REVIEW_STATUS,
        "reviewed_by": "",
        "reviewed_at": None,
    }


# Attaching or swapping a figure changes what a reader sees on the page, but not
# what the lesson teaches, so it is tracked with its own fingerprint instead of
# invalidating clinician sign-off on the teaching content.
MEDIA_ONLY_LESSON_FIELDS = ("image_url", "thumbnail_url", "interactive_url")


def _lesson_fingerprints(lesson_data: dict[str, Any], topic_slug: str) -> tuple[str, str]:
    """Return (content_fingerprint, media_fingerprint) for a seeded lesson."""
    teaching = {
        key: value
        for key, value in lesson_data.items()
        if key not in MEDIA_ONLY_LESSON_FIELDS
    }
    media = {key: lesson_data.get(key, "") for key in MEDIA_ONLY_LESSON_FIELDS}
    return (
        content_fingerprint(
            {"kind": "lesson", "content": teaching, "topic_slug": topic_slug}
        ),
        content_fingerprint({"kind": "lesson_media", "content": media}),
    )


@dataclass
class SeedReport:
    categories_created: int = 0
    chapters_created: int = 0
    topics_created: int = 0
    lessons_created: int = 0
    lessons_updated: int = 0
    questions_created: int = 0
    questions_updated: int = 0
    choices_written: int = 0
    missing_categories: list[str] = field(default_factory=list)

    @property
    def questions_total(self) -> int:
        return self.questions_created + self.questions_updated

    def as_dict(self) -> dict[str, Any]:
        return {
            "categories_created": self.categories_created,
            "chapters_created": self.chapters_created,
            "topics_created": self.topics_created,
            "lessons_created": self.lessons_created,
            "lessons_updated": self.lessons_updated,
            "questions_created": self.questions_created,
            "questions_updated": self.questions_updated,
            "choices_written": self.choices_written,
            "questions_total": self.questions_total,
            "missing_categories": list(self.missing_categories),
        }


def seed_categories(categories: Iterable[dict[str, Any]] | None = None, *, report: SeedReport | None = None) -> SeedReport:
    report = report or SeedReport()
    for data in categories or DEFAULT_CATEGORIES:
        _, created = Category.objects.get_or_create(
            slug=slugify(data["name"]),
            defaults=data,
        )
        if created:
            report.categories_created += 1
    return report


def build_source_metadata(kind: str, *, chapter_slug: str, topic_slug: str, reference_ids: list[str], **extra: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "origin": "seed",
        "kind": kind,
        "chapter_slug": chapter_slug,
        "topic_slug": topic_slug,
        "reference_ids": list(reference_ids),
        "author": SEED_AUTHOR,
        "review_note": SEED_REVIEW_NOTE,
        "references": [
            {
                "id": ref.get("id"),
                "title": ref.get("title"),
                "source": ref.get("source"),
                "year": ref.get("year"),
                "url": ref.get("url"),
            }
            for ref in resolve_references(reference_ids)
        ],
    }
    metadata.update(extra)
    return metadata


def _upsert_lesson(
    lesson_data: dict[str, Any],
    *,
    topic: Topic,
    chapter_slug: str,
    topic_slug: str,
    order_index: int,
    report: SeedReport,
) -> Lesson:
    lesson, created = Lesson.objects.get_or_create(
        topic=topic,
        title=lesson_data["title"],
        defaults={"order_index": order_index},
    )
    reference_ids = list(lesson_data.get("reference_ids", []))
    fingerprint, media_fingerprint = _lesson_fingerprints(lesson_data, topic_slug)
    defaults = {
        "lesson_type": lesson_data.get("lesson_type", "animation"),
        "summary": lesson_data.get("summary", ""),
        "content_md": lesson_data.get("content_md", ""),
        "animation_url": lesson_data.get("animation_url", ""),
        "image_url": lesson_data.get("image_url", ""),
        "interactive_url": lesson_data.get("interactive_url", ""),
        "thumbnail_url": lesson_data.get("thumbnail_url", ""),
        "duration_seconds": lesson_data.get("duration_seconds", 0),
        "order_index": order_index,
        **_review_fields(lesson, fingerprint),
        "source_metadata": build_source_metadata(
            "lesson",
            chapter_slug=chapter_slug,
            topic_slug=topic_slug,
            reference_ids=reference_ids,
            lesson_slug=lesson_data.get("lesson_slug", ""),
            content_fingerprint=fingerprint,
            media_fingerprint=media_fingerprint,
        ),
    }
    changed = created
    for field_name, value in defaults.items():
        if getattr(lesson, field_name) != value:
            setattr(lesson, field_name, value)
            changed = True
    if changed:
        lesson.save()
    if created:
        report.lessons_created += 1
    else:
        report.lessons_updated += 1
    return lesson


def _upsert_question(
    mcq_data: dict[str, Any],
    *,
    category: Category,
    chapter: Chapter,
    topic: Topic,
    lesson: Lesson | None,
    report: SeedReport,
) -> Question | None:
    reference_ids = list(mcq_data.get("reference_ids", []))
    question, created = Question.objects.get_or_create(
        question_text=mcq_data["question_text"],
        chapter=chapter,
        defaults={"category": category, "topic": topic},
    )
    question.category = category
    question.topic = topic
    question.lesson = lesson
    question.difficulty = mcq_data.get("difficulty", "medium")
    question.case_text = mcq_data.get("case_text", "")
    question.labs = mcq_data.get("labs", {}) or {}
    question.explanation = mcq_data.get("explanation", "")
    question.clinical_pearl = mcq_data.get("clinical_pearl", "")
    question.reference = reference_ids_to_storage(reference_ids)
    question.subcategory = topic.title
    fingerprint = content_fingerprint(
        {"kind": "question", "content": mcq_data, "topic_slug": topic.slug}
    )
    for field_name, value in _review_fields(question, fingerprint).items():
        setattr(question, field_name, value)
    question.source_metadata = build_source_metadata(
        "question",
        chapter_slug=chapter.slug,
        topic_slug=topic.slug,
        reference_ids=reference_ids,
        lesson_slug=mcq_data.get("lesson_slug", ""),
        difficulty=mcq_data.get("difficulty", "medium"),
        content_fingerprint=fingerprint,
    )
    question.save()

    if created:
        report.questions_created += 1
    else:
        report.questions_updated += 1

    choices = mcq_data.get("choices", [])
    existing = {choice.choice_key: choice for choice in question.choices.all()}
    for index, (key, text, is_correct, why_wrong) in enumerate(choices, start=1):
        choice = existing.get(key)
        if choice is None:
            choice = Choice(question=question, choice_key=key)
        choice.choice_text = text
        choice.is_correct = bool(is_correct)
        choice.why_wrong = why_wrong or ""
        choice.order = index
        choice.save()
        report.choices_written += 1
    for key, choice in existing.items():
        if key not in {c[0] for c in choices}:
            choice.delete()
    return question


@transaction.atomic
def seed_curriculum(
    chapters: list[dict[str, Any]] | None = None,
    *,
    categories: Iterable[dict[str, Any]] | None = None,
    publish_questions: bool = True,
) -> SeedReport:
    """Create or update categories, chapters, topics, lessons, questions, choices."""
    report = SeedReport()
    seed_categories(categories, report=report)
    for chapter_data in chapters or CHAPTERS:
        category = Category.objects.filter(slug=chapter_data.get("category_slug")).first()
        if category is None:
            report.missing_categories.append(str(chapter_data.get("category_slug")))
            continue
        chapter, created = Chapter.objects.update_or_create(
            slug=chapter_data["slug"],
            defaults={
                "title": chapter_data["title"],
                "order_index": chapter_data["order_index"],
                "description": chapter_data["description"],
                "icon": chapter_data.get("icon", "BookOpenIcon"),
                "category": category,
            },
        )
        if created:
            report.chapters_created += 1

        for topic_index, topic_data in enumerate(chapter_data.get("topics", []), start=1):
            topic, topic_created = Topic.objects.update_or_create(
                chapter=chapter,
                slug=topic_data["slug"],
                defaults={
                    "title": topic_data["title"],
                    "order_index": topic_index,
                    "description": topic_data.get("description", ""),
                },
            )
            if topic_created:
                report.topics_created += 1

            lessons_by_slug: dict[str, Lesson] = {}
            for lesson_index, lesson_data in enumerate(topic_data.get("lessons", []), start=1):
                lesson = _upsert_lesson(
                    lesson_data,
                    topic=topic,
                    chapter_slug=chapter.slug,
                    topic_slug=topic.slug,
                    order_index=lesson_index,
                    report=report,
                )
                lessons_by_slug[lesson_data.get("lesson_slug", "")] = lesson

            for mcq_data in topic_data.get("mcqs", []):
                _upsert_question(
                    mcq_data,
                    category=category,
                    chapter=chapter,
                    topic=topic,
                    lesson=lessons_by_slug.get(mcq_data.get("lesson_slug", "")),
                    report=report,
                )
                if publish_questions:
                    question = Question.objects.filter(
                        question_text=mcq_data["question_text"], chapter=chapter
                    ).first()
                    if question is not None and not question.is_published:
                        question.is_published = True
                        question.save(update_fields=["is_published"])
    return report


@transaction.atomic
def seed_board_exam(
    *,
    publish: bool = False,
    chapters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create or update the weighted board exam, unpublished unless `publish`.

    Seeding never publishes questions on its own: content stays out of the live
    practice pool and out of the exam until a clinician approves it and
    `publish=True` is requested.
    """
    report = seed_curriculum(chapters, publish_questions=False)
    chapter_data = chapters or CHAPTERS
    question_ids: list[int] = []
    pool_per_chapter: dict[str, int] = {}
    approved_per_chapter: dict[str, int] = {}
    publishable_ids: list[int] = []
    for chapter in chapter_data:
        slug = chapter["slug"]
        pool = Question.objects.filter(
            chapter__slug=slug,
            review_status__in=ELIGIBLE_REVIEW_STATUSES,
            # Only questions this seed owns. Older `seed_data` content can sit in a
            # seeded chapter without a chapter_slug in source_metadata, so without
            # this filter the exam silently pools two generations of content.
            source_metadata__chapter_slug=slug,
        )
        pool_per_chapter[slug] = pool.count()
        question_ids.extend(pool.values_list("pk", flat=True))
        approved = pool.filter(review_status__in=PUBLISHABLE_REVIEW_STATUSES)
        approved_per_chapter[slug] = approved.count()
        publishable_ids.extend(approved.values_list("pk", flat=True))

    exam, _ = BoardExam.objects.update_or_create(
        slug=BOARD_EXAM_SLUG,
        defaults={
            "title": BOARD_EXAM_TITLE,
            "description": BOARD_EXAM_DESCRIPTION,
            "question_count": BOARD_EXAM_QUESTION_COUNT,
            "duration_minutes": BOARD_EXAM_DURATION_MINUTES,
            "chapter_quota": dict(CHAPTER_QUOTA),
        },
    )
    exam.questions.set(question_ids)
    published_questions = 0
    if publish:
        deficient = {
            slug: (approved_per_chapter.get(slug, 0), quota)
            for slug, quota in CHAPTER_QUOTA.items()
            if approved_per_chapter.get(slug, 0) < quota
        }
        if deficient:
            raise BoardExamPublishBlocked(deficient)
        published_questions = Question.objects.filter(
            pk__in=publishable_ids,
            is_published=False,
        ).update(is_published=True)
        if not exam.is_published:
            exam.is_published = True
            exam.save(update_fields=["is_published", "updated_at"])
    elif exam.is_published:
        exam.is_published = False
        exam.save(update_fields=["is_published", "updated_at"])

    return {
        "exam": exam,
        "curriculum": report.as_dict(),
        "questions_attached": len(question_ids),
        "questions_per_chapter": pool_per_chapter,
        "approved_per_chapter": approved_per_chapter,
        "published_questions": published_questions,
        "quota_per_chapter": BOARD_EXAM_CHAPTER_QUOTA_PER_CHAPTER,
        "is_published": exam.is_published,
        "review_status": SEED_REVIEW_STATUS,
        "review_note": SEED_REVIEW_NOTE,
        "seeded_at": timezone.now().isoformat(),
    }
