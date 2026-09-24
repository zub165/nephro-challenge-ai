"""RAG-style learning: store verified corrections and inject into Ollama prompts over time."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db.models import F, Q
from django.utils import timezone

logger = logging.getLogger(__name__)

LEARNING_SNAPSHOT = Path(__file__).resolve().parent.parent / "data" / "ai_learned_context.json"


def learning_enabled() -> bool:
    return getattr(settings, "AI_LEARNING_ENABLED", True)


def _normalize_topic(topic: str) -> str:
    return (topic or "").strip()[:150]


def _dedupe_key(lesson_rule: str) -> str:
    return re.sub(r"\s+", " ", (lesson_rule or "").strip().lower())[:200]


def get_approved_lessons(*, topic: str = "", limit: int | None = None) -> list[dict[str, Any]]:
    """Fetch approved lessons for prompt injection (topic match + global rules)."""
    if not learning_enabled():
        return []

    from api.models import AIKnowledgeEntry

    max_items = limit or getattr(settings, "AI_LEARNING_MAX_CONTEXT", 8)
    topic_norm = _normalize_topic(topic).lower()
    qs = AIKnowledgeEntry.objects.filter(status=AIKnowledgeEntry.Status.APPROVED)

    if topic_norm:
        qs = qs.filter(Q(topic__iexact=topic) | Q(topic="") | Q(content_type=AIKnowledgeEntry.ContentType.RULE))
    else:
        qs = qs.filter(content_type=AIKnowledgeEntry.ContentType.RULE)

    entries = list(
        qs.order_by("-use_count", "-approved_at", "-created_at")[: max_items * 2]
    )

    # Prefer topic-specific, then general rules
    if topic_norm:
        entries.sort(
            key=lambda e: (
                0 if e.topic.lower() == topic_norm else 1,
                -e.use_count,
            )
        )

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for entry in entries:
        key = _dedupe_key(entry.lesson_rule)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "id": entry.id,
                "topic": entry.topic,
                "lesson_rule": entry.lesson_rule,
                "corrected_text": entry.corrected_text,
                "reference": entry.reference,
            }
        )
        if len(out) >= max_items:
            break

    if out:
        ids = [item["id"] for item in out]
        AIKnowledgeEntry.objects.filter(id__in=ids).update(use_count=F("use_count") + 1)

    return out


def build_learning_prompt_block(*, topic: str = "") -> str:
    """Text block appended to system prompts."""
    lessons = get_approved_lessons(topic=topic)
    if not lessons:
        return ""
    lines = ["\n\nLearned nephrology rules (apply these; do not contradict KDIGO/KDOQI):"]
    for i, lesson in enumerate(lessons, 1):
        ref = f" ({lesson['reference']})" if lesson.get("reference") else ""
        lines.append(f"{i}. {lesson['lesson_rule']}{ref}")
    return "\n".join(lines)


def augment_system_prompt(base: str, *, topic: str = "") -> str:
    return base + build_learning_prompt_block(topic=topic)


def record_lesson(
    *,
    topic: str,
    lesson_rule: str,
    content_type: str = "rule",
    original_text: str = "",
    corrected_text: str = "",
    reference: str = "",
    source: str = "rule_check",
    status: str = "pending",
    confidence: str = "medium",
) -> int | None:
    """Store a learning entry; skip duplicates. Returns entry id or None."""
    if not learning_enabled():
        return None

    from api.models import AIKnowledgeEntry

    rule = (lesson_rule or "").strip()
    if len(rule) < 12:
        return None

    topic = _normalize_topic(topic)
    key = _dedupe_key(rule)
    existing = AIKnowledgeEntry.objects.filter(
        status__in=[AIKnowledgeEntry.Status.APPROVED, AIKnowledgeEntry.Status.PENDING],
    )
    for entry in existing.iterator():
        if _dedupe_key(entry.lesson_rule) == key:
            return entry.id

    entry = AIKnowledgeEntry.objects.create(
        topic=topic,
        content_type=content_type,
        original_text=(original_text or "")[:4000],
        corrected_text=(corrected_text or "")[:4000],
        lesson_rule=rule[:2000],
        reference=(reference or "")[:500],
        source=source,
        status=status,
        confidence=confidence,
        approved_at=timezone.now() if status == AIKnowledgeEntry.Status.APPROVED else None,
    )
    return entry.id


def record_rule_issues(topic: str, statement: str, issues: list[str]) -> int:
    """Auto-approve rule-based findings (high trust)."""
    count = 0
    for issue in issues:
        if record_lesson(
            topic=topic,
            lesson_rule=issue,
            content_type="rule",
            original_text=statement,
            source="rule_check",
            status="approved",
            confidence="high",
        ):
            count += 1
    return count


def record_verification_result(
    *,
    topic: str,
    statement: str,
    verification: dict[str, Any],
    content_type: str = "pearl",
    reference: str = "",
) -> int | None:
    """
    After LLM/rule verification, store corrections for future prompts.
    Rule issues → auto-approved. LLM corrections → pending unless high confidence.
    """
    if not learning_enabled():
        return None

    issues = verification.get("issues") or []
    if issues:
        record_rule_issues(topic, statement, issues)

    correction = (
        verification.get("suggested_correction")
        or verification.get("corrected_text")
        or ""
    ).strip()
    verified = verification.get("verified")
    if verified is None:
        verified = verification.get("is_accurate")

    if verified is True and not correction:
        return None

    lesson_parts = [i for i in issues if i]
    if correction:
        lesson_parts.append(f"Preferred wording: {correction[:400]}")
    if not lesson_parts:
        return None

    lesson_rule = " ".join(lesson_parts)[:2000]
    confidence = verification.get("confidence") or "medium"
    status = "pending"
    if confidence == "high" and correction and verified is False:
        status = "approved"

    return record_lesson(
        topic=topic,
        lesson_rule=lesson_rule,
        content_type=content_type,
        original_text=statement,
        corrected_text=correction,
        reference=reference or verification.get("reference", ""),
        source="verification" if verification.get("method") == "llm" else "llama_audit",
        status=status,
        confidence=str(confidence),
    )


def approve_entry(entry_id: int, user=None) -> bool:
    from api.models import AIKnowledgeEntry

    updated = AIKnowledgeEntry.objects.filter(
        id=entry_id,
        status=AIKnowledgeEntry.Status.PENDING,
    ).update(
        status=AIKnowledgeEntry.Status.APPROVED,
        approved_by=user,
        approved_at=timezone.now(),
    )
    return updated > 0


def reject_entry(entry_id: int) -> bool:
    from api.models import AIKnowledgeEntry

    updated = AIKnowledgeEntry.objects.filter(id=entry_id).update(
        status=AIKnowledgeEntry.Status.REJECTED,
    )
    return updated > 0


def export_learning_snapshot() -> dict[str, Any]:
    """Write approved lessons to JSON for backup / offline review."""
    from api.models import AIKnowledgeEntry

    entries = AIKnowledgeEntry.objects.filter(status=AIKnowledgeEntry.Status.APPROVED).order_by("topic")
    payload = {
        "exported_at": timezone.now().isoformat(),
        "model": getattr(settings, "LLAMA_MODEL", ""),
        "count": entries.count(),
        "lessons": [
            {
                "topic": e.topic,
                "lesson_rule": e.lesson_rule,
                "corrected_text": e.corrected_text,
                "reference": e.reference,
                "source": e.source,
                "use_count": e.use_count,
            }
            for e in entries
        ],
    }
    LEARNING_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    LEARNING_SNAPSHOT.write_text(json.dumps(payload, indent=2))
    return payload


def maybe_export_learning():
    """Auto-export learning snapshot after audits when enabled."""
    if not learning_enabled():
        return
    if getattr(settings, "AI_LEARNING_AUTO_EXPORT", True):
        export_learning_snapshot()


def learning_stats() -> dict[str, int]:
    from api.models import AIKnowledgeEntry

    return {
        "approved": AIKnowledgeEntry.objects.filter(status=AIKnowledgeEntry.Status.APPROVED).count(),
        "pending": AIKnowledgeEntry.objects.filter(status=AIKnowledgeEntry.Status.PENDING).count(),
        "rejected": AIKnowledgeEntry.objects.filter(status=AIKnowledgeEntry.Status.REJECTED).count(),
    }


def seed_baseline_rules() -> int:
    """One-time bootstrap from built-in nephrology rule checks."""
    samples = [
        (
            "Hyponatremia",
            "Chronic hyponatremia: correct Na+ up to 15 mEq/L per 24 h safely.",
            ["Hyponatremia correction >10-12 mEq/L per 24h risks osmotic demyelination (per Verbalis/KDIGO)."],
        ),
        (
            "Hyperkalemia",
            "With ECG changes from hyperkalemia, start hemodialysis before IV calcium.",
            ["With ECG changes, IV calcium should be mentioned first for membrane stabilization."],
        ),
        (
            "Prerenal AKI",
            "FENa <1% confirms prerenal AKI even if the patient is on furosemide.",
            ["On diuretics, FEUrea is preferred over FENa for prerenal vs intrinsic differentiation."],
        ),
        (
            "Winter's Formula",
            "Expected PCO2 = (1.5 × HCO3) + 8. Measured PCO2 interpretation.",
            ["Winter's formula uses (1.5 × HCO3) + 8 ± 2."],
        ),
    ]
    added = 0
    for topic, text, issues in samples:
        added += record_rule_issues(topic, text, issues)
    return added
