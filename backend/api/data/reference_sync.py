"""Sync literature reference IDs from seed modules into Question rows."""

from __future__ import annotations

from api.data.chapter_seed import CHAPTERS
from api.data.medical_references import reference_ids_to_storage
from api.models import Question


def iter_seed_question_refs():
    """Yield question_text, optional chapter_slug, and reference_ids from seed data."""
    from api.management.commands.seed_data import SAMPLE_QUESTIONS

    for ch in CHAPTERS:
        for topic in ch.get("topics", []):
            for mcq in topic.get("mcqs", []):
                yield {
                    "question_text": mcq["question_text"],
                    "chapter_slug": ch["slug"],
                    "reference_ids": mcq.get("reference_ids", []),
                }
    for q in SAMPLE_QUESTIONS:
        yield {
            "question_text": q["question_text"],
            "chapter_slug": None,
            "reference_ids": q.get("reference_ids", []),
        }


def sync_question_references_from_seed() -> dict[str, int]:
    """
    Write reference JSON from chapter_seed + SAMPLE_QUESTIONS onto matching DB questions.
    Matches by question_text; chapter MCQs also filter by chapter slug.
    """
    updated = 0
    unchanged = 0
    missing = 0

    for item in iter_seed_question_refs():
        ref_storage = reference_ids_to_storage(item["reference_ids"])
        qs = Question.objects.filter(question_text=item["question_text"])
        if item["chapter_slug"]:
            qs = qs.filter(chapter__slug=item["chapter_slug"])
        question = qs.first()
        if not question:
            missing += 1
            continue
        if question.reference == ref_storage:
            unchanged += 1
            continue
        question.reference = ref_storage
        question.save(update_fields=["reference"])
        updated += 1

    return {"updated": updated, "unchanged": unchanged, "missing": missing}
