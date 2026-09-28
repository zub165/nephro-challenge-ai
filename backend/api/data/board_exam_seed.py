"""Board exam seed configuration plus pre-publication content validation.

The exam is defined as data so that `seed_board_exam` stays declarative and
`verify_medical_content` and the test-suite can assert the same invariants.
`validate_board_seed()` is the single gate that must pass before a seeded exam
may be published, and it fails on taxonomy drift, content defects, or an
under-sized question pool.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

from api.data.chapter_seed import ANIMATION_BASE, CHAPTERS, MEDICAL_ASSET_BASE
from api.data.medical_references import MEDICAL_REFERENCES

BOARD_EXAM_SLUG = "nephrology-board-exam"
BOARD_EXAM_TITLE = "Nephrology Board Review Exam"
BOARD_EXAM_DESCRIPTION = (
    "Weighted 50-question nephrology board practice exam built from the ten-chapter "
    "review taxonomy. Each chapter contributes a fixed quota of questions."
)
BOARD_EXAM_QUESTION_COUNT = 50
BOARD_EXAM_DURATION_MINUTES = 60
BOARD_EXAM_CHAPTER_QUOTA_PER_CHAPTER = 5

EXPECTED_CHAPTER_ORDER: list[tuple[str, str]] = [
    ("acid-base-disorders", "Acid-Base Disorders"),
    ("electrolytes", "Electrolytes"),
    ("acute-kidney-injury-icu", "Acute Kidney Injury & ICU"),
    ("chronic-kidney-disease", "Chronic Kidney Disease"),
    ("hypertension", "Hypertension"),
    ("dialysis", "Dialysis"),
    ("tubulointerstitial-cystic", "Tubulointerstitial & Cystic Disorders"),
    ("glomerular-vascular", "Glomerular & Vascular Disorders"),
    ("transplantation", "Transplantation"),
    ("nephrology-pharmacology", "Nephrology Pharmacology"),
]

CHAPTER_QUOTA: dict[str, int] = {slug: BOARD_EXAM_CHAPTER_QUOTA_PER_CHAPTER for slug, _ in EXPECTED_CHAPTER_ORDER}

MIN_CHOICES = 2
MAX_CHOICES = 6
MIN_POOL_QUESTIONS = 60
MIN_QUESTIONS_PER_CHAPTER = 6
REQUIRED_CHOICE_KEYS = ("A", "B", "C", "D", "E", "F")

SEED_REVIEW_STATUS = "needs_review"
SEED_REVIEW_NOTE = (
    "Original teaching content generated for this repository. Requires review by a "
    "qualified nephrologist or ABIM-certified clinician before clinical release."
)
SEED_AUTHOR = "Nephro Challenge AI content team"

ANIMATION_ASSET_DIR = Path(__file__).resolve().parents[3] / "web" / "public" / "animations"
MEDICAL_ASSET_DIR = Path(__file__).resolve().parents[3] / "web" / "public" / "medical"
MEDICAL_URL_FIELDS = ("image_url", "thumbnail_url", "interactive_url")

VALID_DIFFICULTIES = ("easy", "medium", "hard", "board")
VALID_LESSON_TYPES = ("animation", "article", "video")


class BoardSeedValidationError(Exception):
    """Raised when seeded board content fails validation."""

    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        detail = "\n".join(f"  - {error}" for error in self.errors)
        super().__init__(f"Board exam seed validation failed:\n{detail}")


def normalize_stem(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "").lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def iter_seed_mcqs():
    """Yield (chapter, topic, mcq) for every seeded question."""
    for chapter in CHAPTERS:
        for topic in chapter.get("topics", []):
            for mcq in topic.get("mcqs", []):
                yield chapter, topic, mcq


def iter_seed_lessons():
    for chapter in CHAPTERS:
        for topic in chapter.get("topics", []):
            for lesson in topic.get("lessons", []):
                yield chapter, topic, lesson


def _validate_chapter_taxonomy(errors: list[str]) -> None:
    if len(CHAPTERS) != len(EXPECTED_CHAPTER_ORDER):
        errors.append(
            f"expected {len(EXPECTED_CHAPTER_ORDER)} chapters, found {len(CHAPTERS)}"
        )
    seen_slugs: set[str] = set()
    for position, (expected_slug, expected_title) in enumerate(EXPECTED_CHAPTER_ORDER, start=1):
        if position > len(CHAPTERS):
            errors.append(f"missing chapter at position {position}: {expected_title}")
            continue
        chapter = CHAPTERS[position - 1]
        slug = chapter.get("slug", "")
        if slug != expected_slug:
            errors.append(
                f"chapter {position} slug is {slug!r}, expected {expected_slug!r}"
            )
        if chapter.get("title") != expected_title:
            errors.append(
                f"chapter {position} title is {chapter.get('title')!r}, expected {expected_title!r}"
            )
        if chapter.get("order_index") != position:
            errors.append(
                f"chapter {slug} order_index is {chapter.get('order_index')}, expected {position}"
            )
        if not chapter.get("category_slug"):
            errors.append(f"chapter {slug} has no category_slug")
        if not chapter.get("description"):
            errors.append(f"chapter {slug} has no description")
        if slug in seen_slugs:
            errors.append(f"duplicate chapter slug {slug!r}")
        seen_slugs.add(slug)
        topic_slugs: set[str] = set()
        for topic in chapter.get("topics", []):
            topic_slug = topic.get("slug", "")
            if not topic_slug:
                errors.append(f"chapter {slug} has a topic without a slug")
            if topic_slug in topic_slugs:
                errors.append(f"chapter {slug} has duplicate topic slug {topic_slug!r}")
            topic_slugs.add(topic_slug)


def _validate_lessons(
    errors: list[str],
    warnings: list[str],
    animation_files: set[str],
    medical_files: set[str],
) -> tuple[set[str], set[str]]:
    referenced_animations: set[str] = set()
    referenced_medical: set[str] = set()
    seen_slugs: set[str] = set()
    for chapter, topic, lesson in iter_seed_lessons():
        where = f"{chapter.get('slug')}/{topic.get('slug')}"
        title = (lesson.get("title") or "").strip()
        lesson_slug = (lesson.get("lesson_slug") or "").strip()
        if not title:
            errors.append(f"{where}: lesson has no title")
        if not lesson_slug:
            errors.append(f"{where}: lesson {title!r} has no lesson_slug")
        elif lesson_slug in seen_slugs:
            errors.append(f"{where}: duplicate lesson_slug {lesson_slug!r}")
        else:
            seen_slugs.add(lesson_slug)

        lesson_type = lesson.get("lesson_type")
        if lesson_type not in VALID_LESSON_TYPES:
            errors.append(f"{where}/{lesson_slug}: invalid lesson_type {lesson_type!r}")
        if lesson_type == "animation":
            url = (lesson.get("animation_url") or "").strip()
            if not url:
                errors.append(f"{where}/{lesson_slug}: animation lesson has no animation_url")
            elif not url.startswith(f"{ANIMATION_BASE}/"):
                errors.append(
                    f"{where}/{lesson_slug}: animation_url {url!r} is not under {ANIMATION_BASE}"
                )
            else:
                filename = url.rsplit("/", 1)[-1]
                referenced_animations.add(filename)
                if animation_files and filename not in animation_files:
                    errors.append(f"{where}/{lesson_slug}: animation file {filename} is missing")
        elif not (lesson.get("content_md") or "").strip():
            errors.append(f"{where}/{lesson_slug}: article lesson has no content_md")

        for field_name in MEDICAL_URL_FIELDS:
            url = (lesson.get(field_name) or "").strip()
            if not url:
                continue
            if not url.startswith(f"{MEDICAL_ASSET_BASE}/"):
                errors.append(
                    f"{where}/{lesson_slug}: {field_name} {url!r} is not under {MEDICAL_ASSET_BASE}"
                )
                continue
            relative_path = url[len(MEDICAL_ASSET_BASE) + 1 :]
            referenced_medical.add(relative_path)
            if medical_files and not (MEDICAL_ASSET_DIR / relative_path).is_file():
                errors.append(f"{where}/{lesson_slug}: {field_name} file {relative_path} is missing")

        if not (lesson.get("summary") or "").strip():
            errors.append(f"{where}/{lesson_slug}: lesson has no summary")
        if int(lesson.get("duration_seconds") or 0) <= 0:
            errors.append(f"{where}/{lesson_slug}: lesson duration_seconds must be positive")
        reference_ids = lesson.get("reference_ids") or []
        if not reference_ids:
            errors.append(f"{where}/{lesson_slug}: lesson has no reference_ids")
        for reference_id in reference_ids:
            if reference_id not in MEDICAL_REFERENCES:
                errors.append(f"{where}/{lesson_slug}: unknown reference id {reference_id!r}")

    if animation_files:
        for filename in sorted(animation_files - referenced_animations):
            errors.append(f"animation asset {filename} is not referenced by any lesson")
    else:
        warnings.append(
            "animation asset directory is unavailable; skipped animation file checks"
        )

    if medical_files:
        for relative_path in sorted(medical_files - referenced_medical):
            warnings.append(f"medical asset {relative_path} is not referenced by any lesson")
    else:
        warnings.append("medical asset directory is unavailable; skipped medical asset checks")

    return referenced_animations, referenced_medical


def _validate_questions(errors: list[str]) -> dict[str, int]:
    per_chapter: dict[str, int] = {}
    per_topic: dict[str, int] = {}
    seen_stems: dict[str, str] = {}
    for chapter, topic, mcq in iter_seed_mcqs():
        chapter_slug = chapter.get("slug", "")
        topic_slug = topic.get("slug", "")
        where = f"{chapter_slug}/{topic_slug}"
        per_chapter[chapter_slug] = per_chapter.get(chapter_slug, 0) + 1
        per_topic[where] = per_topic.get(where, 0) + 1

        stem = normalize_stem(mcq.get("question_text", ""))
        if not stem:
            errors.append(f"{where}: question has no question_text")
        elif stem in seen_stems:
            errors.append(
                f"{where}: duplicate question stem, also used in {seen_stems[stem]}: "
                f"{(mcq.get('question_text') or '')[:60]!r}"
            )
        else:
            seen_stems[stem] = where

        if (mcq.get("difficulty") or "") not in VALID_DIFFICULTIES:
            errors.append(f"{where}: invalid difficulty {mcq.get('difficulty')!r}")
        if not (mcq.get("case_text") or "").strip():
            errors.append(f"{where}: question has no case_text")
        if mcq.get("labs") is not None and not isinstance(mcq.get("labs"), dict):
            errors.append(f"{where}: labs must be a mapping")
        if not (mcq.get("explanation") or "").strip():
            errors.append(f"{where}: question has no explanation")
        if not (mcq.get("clinical_pearl") or "").strip():
            errors.append(f"{where}: question has no clinical_pearl")

        reference_ids = mcq.get("reference_ids") or []
        if not reference_ids:
            errors.append(f"{where}: question has no reference_ids")
        for reference_id in reference_ids:
            if reference_id not in MEDICAL_REFERENCES:
                errors.append(f"{where}: unknown reference id {reference_id!r}")

        lesson_slug = (mcq.get("lesson_slug") or "").strip()
        if not lesson_slug:
            errors.append(f"{where}: question has no lesson_slug")
        else:
            topic_lesson_slugs = {
                (lesson.get("lesson_slug") or "") for lesson in topic.get("lessons", [])
            }
            if lesson_slug not in topic_lesson_slugs:
                errors.append(
                    f"{where}: question lesson_slug {lesson_slug!r} is not a lesson of this topic"
                )

        choices = mcq.get("choices") or []
        if not MIN_CHOICES <= len(choices) <= MAX_CHOICES:
            errors.append(
                f"{where}: question has {len(choices)} choices, expected {MIN_CHOICES}-{MAX_CHOICES}"
            )
        keys = [choice[0] for choice in choices]
        if keys != list(REQUIRED_CHOICE_KEYS[: len(choices)]):
            errors.append(
                f"{where}: choice keys {keys} must be sequential letters starting at A"
            )
        correct = [choice for choice in choices if choice[2]]
        if len(correct) != 1:
            errors.append(f"{where}: question has {len(correct)} correct choices, expected 1")
        for key, text, is_correct, why_wrong in choices:
            if not (text or "").strip():
                errors.append(f"{where}: choice {key} has no text")
            if not is_correct and not (why_wrong or "").strip():
                errors.append(f"{where}: incorrect choice {key} has no why_wrong text")

    return per_chapter


def _validate_quota(errors: list[str], per_chapter: dict[str, int]) -> None:
    chapter_slugs = [chapter.get("slug", "") for chapter in CHAPTERS]
    if set(CHAPTER_QUOTA) != set(chapter_slugs):
        missing = sorted(set(chapter_slugs) - set(CHAPTER_QUOTA))
        unknown = sorted(set(CHAPTER_QUOTA) - set(chapter_slugs))
        errors.append(f"chapter_quota mismatch: missing={missing} unknown={unknown}")
    total_quota = sum(CHAPTER_QUOTA.values())
    if total_quota != BOARD_EXAM_QUESTION_COUNT:
        errors.append(
            f"chapter_quota sums to {total_quota}, expected question_count {BOARD_EXAM_QUESTION_COUNT}"
        )
    if sum(per_chapter.values()) < MIN_POOL_QUESTIONS:
        errors.append(
            f"question pool has {sum(per_chapter.values())} questions, "
            f"minimum is {MIN_POOL_QUESTIONS}"
        )
    for chapter_slug, quota in CHAPTER_QUOTA.items():
        available = per_chapter.get(chapter_slug, 0)
        if available < quota:
            errors.append(
                f"chapter {chapter_slug} has {available} questions but quota is {quota}"
            )
        if available < MIN_QUESTIONS_PER_CHAPTER:
            errors.append(
                f"chapter {chapter_slug} has {available} questions, "
                f"minimum is {MIN_QUESTIONS_PER_CHAPTER}"
            )


def _animation_files() -> set[str]:
    if not ANIMATION_ASSET_DIR.is_dir():
        return set()
    return {path.name for path in ANIMATION_ASSET_DIR.glob("*.json")}


def _medical_files() -> set[str]:
    """Repo-relative paths of every served medical asset, e.g. `chapter/slug.webp`."""
    if not MEDICAL_ASSET_DIR.is_dir():
        return set()
    return {
        str(path.relative_to(MEDICAL_ASSET_DIR))
        for path in MEDICAL_ASSET_DIR.rglob("*")
        if path.is_file()
    }


def validate_board_seed() -> dict[str, Any]:
    """Validate the seeded taxonomy, questions, and exam configuration.

    Returns a report with `errors`, `warnings`, and `stats`. Publication must be
    blocked while `errors` is non-empty.
    """
    errors: list[str] = []
    warnings: list[str] = []

    _validate_chapter_taxonomy(errors)
    animation_files = _animation_files()
    medical_files = _medical_files()
    referenced_animations, referenced_medical = _validate_lessons(
        errors, warnings, animation_files, medical_files
    )
    per_chapter = _validate_questions(errors)
    _validate_quota(errors, per_chapter)

    lessons = list(iter_seed_lessons())
    stats = {
        "chapters": len(CHAPTERS),
        "topics": sum(len(chapter.get("topics", [])) for chapter in CHAPTERS),
        "lessons": len(lessons),
        "questions": sum(per_chapter.values()),
        "questions_per_chapter": per_chapter,
        "question_count": BOARD_EXAM_QUESTION_COUNT,
        "duration_minutes": BOARD_EXAM_DURATION_MINUTES,
        "chapter_quota": dict(CHAPTER_QUOTA),
        "animations_referenced": len(referenced_animations),
        "animations_present": len(animation_files),
        "medical_assets_referenced": len(referenced_medical),
        "medical_assets_present": len(medical_files),
        "review_status": SEED_REVIEW_STATUS,
    }
    return {"errors": errors, "warnings": warnings, "stats": stats}


def assert_valid_board_seed() -> dict[str, Any]:
    report = validate_board_seed()
    if report["errors"]:
        raise BoardSeedValidationError(report["errors"])
    return report
