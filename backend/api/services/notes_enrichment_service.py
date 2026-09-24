"""Clean, reference-tag, and verify user study notes (My Book pearls)."""

from __future__ import annotations

import json
import re
from typing import Any

from api.data.medical_references import (
    reference_ids_to_storage,
    references_for_topic,
    resolve_reference_field,
)
from api.models import StudyNote
from api.services.content_verification_service import verify_statement

_DASH_RUN = re.compile(r"[—–\-]{2,}")
_MULTI_SPACE = re.compile(r"\s+")


def clean_note_content(text: str) -> str:
    """Remove stray dashes and normalize whitespace."""
    text = (text or "").strip()
    text = _DASH_RUN.sub("", text)
    text = _MULTI_SPACE.sub(" ", text)
    return text.strip()


def infer_reference_ids(topic: str, chapter_slug: str | None) -> list[str]:
    refs = references_for_topic(topic or "Pearl", chapter_slug)
    return [r["id"] for r in refs if r.get("id") and r["id"] not in ("legacy",)]


def reference_ids_from_note(note: StudyNote) -> list[str]:
    if note.reference and note.reference.strip().startswith("["):
        try:
            ids = json.loads(note.reference)
            if isinstance(ids, list):
                return [str(i) for i in ids]
        except json.JSONDecodeError:
            pass
    slug = note.chapter.slug if note.chapter_id else None
    return infer_reference_ids(note.topic_title or "Pearl", slug)


def references_for_study_note(note: StudyNote) -> list[dict[str, Any]]:
    refs = resolve_reference_field(note.reference or "")
    if not refs:
        slug = note.chapter.slug if note.chapter_id else None
        refs = references_for_topic(note.topic_title or "Pearl", slug)
    return refs


def enrich_note_payload(
    *,
    topic: str,
    content: str,
    chapter_slug: str | None,
) -> dict[str, Any]:
    cleaned = clean_note_content(content)
    ref_ids = infer_reference_ids(topic, chapter_slug)
    return {
        "content": cleaned,
        "reference": reference_ids_to_storage(ref_ids) if ref_ids else "",
        "reference_ids": ref_ids,
    }


def enrich_study_note(
    note: StudyNote,
    *,
    use_llm: bool = False,
    apply_correction: bool = False,
) -> dict[str, Any]:
    """
    Clean text, attach references, optionally LLM-verify.
    Persists changes on the note model.
    """
    slug = note.chapter.slug if note.chapter_id else None
    topic = note.topic_title or "Pearl"
    payload = enrich_note_payload(topic=topic, content=note.content, chapter_slug=slug)

    update_fields: list[str] = []
    if payload["content"] != note.content:
        note.content = payload["content"]
        update_fields.append("content")
    if payload["reference"] != (note.reference or ""):
        note.reference = payload["reference"]
        update_fields.append("reference")

    ref_ids = payload["reference_ids"] or reference_ids_from_note(note)
    verification = verify_statement(
        note.content,
        topic=topic,
        reference_ids=ref_ids,
        use_llm=use_llm,
    )

    if apply_correction and not verification.get("verified"):
        correction = (verification.get("suggested_correction") or "").strip()
        if correction:
            note.content = correction
            if "content" not in update_fields:
                update_fields.append("content")

    suggested_ids = verification.get("suggested_reference_ids") or []
    if suggested_ids and isinstance(suggested_ids, list):
        storage = reference_ids_to_storage(suggested_ids)
        if storage != (note.reference or ""):
            note.reference = storage
            if "reference" not in update_fields:
                update_fields.append("reference")

    note.verified = verification.get("verified")
    note.verification_confidence = verification.get("confidence") or ""
    note.verification_issues = verification.get("issues") or []
    update_fields.extend(["verified", "verification_confidence", "verification_issues"])

    if update_fields:
        note.save(update_fields=list(dict.fromkeys(update_fields)))

    return {
        "note_id": note.id,
        "content": note.content,
        "references": references_for_study_note(note),
        "verified": note.verified,
        "verification_confidence": note.verification_confidence,
        "verification_issues": note.verification_issues,
        "verification": verification,
    }


def enrich_study_notes_queryset(
    notes,
    *,
    use_llm: bool = False,
    apply_correction: bool = False,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    verified_ok = 0
    verified_fail = 0
    for note in notes.select_related("chapter"):
        item = enrich_study_note(note, use_llm=use_llm, apply_correction=apply_correction)
        if item.get("verified"):
            verified_ok += 1
        elif item.get("verified") is False:
            verified_fail += 1
        results.append(item)
    return {
        "enriched": len(results),
        "verified_ok": verified_ok,
        "verified_fail": verified_fail,
        "use_llm": use_llm,
        "notes": results,
    }
