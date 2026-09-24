"""Sync literature references from seed files into Question rows."""

from __future__ import annotations

from typing import Any, Iterator

from api.data.chapter_seed import CHAPTERS
from api.data.sample_questions import SAMPLE_QUESTIONS
from api.models import Question


def iter_seed_mcqs() -> Iterator[dict[str, Any]]:
    """Yield normalized MCQ dicts from chapter_seed + SAMPLE_QUESTIONS."""
    for ch in CHAPTERS:
        for topic in ch.get("topics", []):
            for mcq in topic.get("mcqs", []):
                yield {
                    "question_text": mcq["question_text"],
                    "explanation": mcq["explanation"],
                    "clinical_pearl": mcq.get("clinical_pearl", ""),
                    "reference": mcq.get("reference", ""),
                    "source": "chapter_seed",
                }
    for mcq in SAMPLE_QUESTIONS:
        yield {
            "question_text": mcq["question_text"],
            "explanation": mcq["explanation"],
            "clinical_pearl": mcq.get("clinical_pearl", ""),
            "reference": mcq.get("reference", ""),
            "source": "sample_questions",
        }


def sync_question_references() -> dict[str, int]:
    """Update explanation, clinical_pearl, and reference for matching DB questions."""
    updated = 0
    matched = 0
    for mcq in iter_seed_mcqs():
        qs = Question.objects.filter(question_text=mcq["question_text"])
        if not qs.exists():
            continue
        matched += qs.count()
        n = qs.update(
            explanation=mcq["explanation"],
            clinical_pearl=mcq["clinical_pearl"],
            reference=mcq["reference"],
        )
        updated += n
    seed_items = sum(1 for _ in iter_seed_mcqs())
    return {"updated": updated, "matched": matched, "seed_items": seed_items}
