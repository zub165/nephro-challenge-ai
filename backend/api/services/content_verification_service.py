"""LLaMA/OpenAI-backed verification of pearls and MCQ medical content."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from api.data.medical_references import (
    MEDICAL_REFERENCES,
    enrich_pearl,
    reference_ids_to_storage,
    resolve_references,
)
from api.services.ai_service import _chat_completion
from api.services.ai_learning_service import (
    augment_system_prompt,
    record_rule_issues,
    record_verification_result,
)

logger = logging.getLogger(__name__)

VERIFICATION_PROMPT = """You are a nephrology board-review fact checker. Review the clinical statement below.

STATEMENT:
{statement}

TOPIC: {topic}

AUTHORITATIVE REFERENCES (use these to verify):
{references}

Respond with ONLY valid JSON:
{{
  "verified": true or false,
  "confidence": "high" | "medium" | "low",
  "issues": ["list any factual errors, outdated thresholds, or missing nuance"],
  "suggested_correction": "corrected statement if needed, or empty string",
  "suggested_reference_ids": ["ids from provided references that best support the statement"],
  "rationale": "one paragraph"
}}

Be strict about numeric thresholds (Na correction rate, FENa cutoffs, BP targets, K+ treatment order).
If the statement is accurate, set verified=true and suggested_correction="".
"""


def _format_refs_for_prompt(ref_ids: list[str]) -> str:
    lines = []
    for rid in ref_ids:
        ref = MEDICAL_REFERENCES.get(rid)
        if ref:
            lines.append(f"- [{rid}] {ref.get('citation', ref.get('title', ''))}")
    return "\n".join(lines) if lines else "(No references supplied)"


def verify_statement(
    statement: str,
    *,
    topic: str = "",
    reference_ids: list[str] | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Verify a pearl or MCQ explanation against literature citations.
    Falls back to rule-based checks when LLM unavailable.
    """
    statement = (statement or "").strip()
    ref_ids = reference_ids or []
    refs = resolve_references(ref_ids)

    result: dict[str, Any] = {
        "statement": statement,
        "topic": topic,
        "reference_ids": ref_ids,
        "references": refs,
        "verified": None,
        "confidence": "low",
        "issues": [],
        "suggested_correction": "",
        "suggested_reference_ids": ref_ids,
        "rationale": "",
        "method": "rules",
    }

    rule_issues = _rule_based_checks(statement, topic)
    if rule_issues:
        result["issues"].extend(rule_issues)
        record_rule_issues(topic, statement, rule_issues)

    if not use_llm:
        result["verified"] = len(result["issues"]) == 0
        result["confidence"] = "medium" if result["verified"] else "low"
        result["rationale"] = "Rule-based check only (LLM unavailable)."
        return result

    content = _chat_completion(
        [
            {
                "role": "system",
                "content": augment_system_prompt(
                    "You are a precise nephrology educator. Output valid JSON only.",
                    topic=topic,
                ),
            },
            {
                "role": "user",
                "content": VERIFICATION_PROMPT.format(
                    statement=statement,
                    topic=topic or "General nephrology",
                    references=_format_refs_for_prompt(ref_ids),
                ),
            },
        ],
        max_tokens=600,
        temperature=0.2,
        json_mode=True,
    )

    if not content:
        result["verified"] = len(result["issues"]) == 0
        result["confidence"] = "low"
        result["rationale"] = "LLM unavailable; used rule-based checks only."
        return result

    try:
        parsed = json.loads(content)
        result["method"] = "llm"
        result["verified"] = bool(parsed.get("verified"))
        result["confidence"] = parsed.get("confidence", "medium")
        llm_issues = parsed.get("issues") or []
        if isinstance(llm_issues, list):
            result["issues"] = list(dict.fromkeys(result["issues"] + llm_issues))
        result["suggested_correction"] = (parsed.get("suggested_correction") or "").strip()
        suggested_ids = parsed.get("suggested_reference_ids") or ref_ids
        if isinstance(suggested_ids, list):
            result["suggested_reference_ids"] = [str(i) for i in suggested_ids if i in MEDICAL_REFERENCES]
        result["rationale"] = parsed.get("rationale", "")
        if result["issues"] and result["verified"]:
            result["verified"] = False
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning("Failed to parse LLM verification response: %s", exc)
        result["verified"] = len(result["issues"]) == 0
        result["rationale"] = "LLM response parse failed."

    if use_llm:
        record_verification_result(
            topic=topic,
            statement=statement,
            verification=result,
            content_type="pearl" if topic and topic != "MCQ" else "mcq",
            reference=_format_refs_for_prompt(ref_ids)[:500],
        )

    return result


def verify_pearl(pearl: dict[str, Any], *, use_llm: bool = True) -> dict[str, Any]:
    enriched = enrich_pearl(pearl)
    ref_ids = pearl.get("reference_ids") or [r["id"] for r in enriched.get("references", []) if r.get("id") != "legacy"]
    verification = verify_statement(
        pearl.get("pearl", ""),
        topic=pearl.get("topic", ""),
        reference_ids=ref_ids,
        use_llm=use_llm,
    )
    return {"pearl": enriched, "verification": verification}


def verify_mcq(
    *,
    question_text: str,
    explanation: str,
    clinical_pearl: str = "",
    reference_ids: list[str] | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    combined = f"Q: {question_text}\n\nExplanation: {explanation}"
    if clinical_pearl:
        combined += f"\n\nPearl: {clinical_pearl}"
    verification = verify_statement(
        combined,
        topic="MCQ",
        reference_ids=reference_ids or [],
        use_llm=use_llm,
    )
    return {
        "question_text": question_text,
        "verification": verification,
    }


def apply_pearl_correction(pearl: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    """Return updated pearl dict if correction suggested."""
    updated = dict(pearl)
    correction = (verification.get("suggested_correction") or "").strip()
    if correction and not verification.get("verified"):
        updated["pearl"] = correction
        updated["_original_pearl"] = pearl.get("pearl")
    suggested_ids = verification.get("suggested_reference_ids")
    if suggested_ids:
        updated["reference_ids"] = suggested_ids
    return updated


def apply_mcq_correction(
    mcq: dict[str, Any],
    verification: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(mcq)
    correction = (verification.get("suggested_correction") or "").strip()
    if correction and not verification.get("verified"):
        if "Pearl:" in correction:
            parts = correction.split("Pearl:", 1)
            if len(parts) == 2:
                updated["explanation"] = parts[0].replace("Explanation:", "").strip()
                updated["clinical_pearl"] = parts[1].strip()
        else:
            updated["explanation"] = correction
    suggested_ids = verification.get("suggested_reference_ids")
    if suggested_ids:
        updated["reference_ids"] = suggested_ids
        updated["reference"] = reference_ids_to_storage(suggested_ids)
    return updated


def verify_all_board_pearls(pearls: list[dict], *, use_llm: bool = True) -> list[dict]:
    return [verify_pearl(p, use_llm=use_llm) for p in pearls]


def _rule_based_checks(statement: str, topic: str) -> list[str]:
    """Fast local checks for common errors."""
    issues: list[str] = []
    lower = statement.lower()

    # Hyponatremia correction rate
    if "hyponatremia" in lower or "hyponatremia" in topic.lower():
        if re.search(r"1[2-9]\s*m?eq/l\s*per\s*24", lower) or re.search(r"1[2-9]\s*m?eq/l/24", lower):
            issues.append("Hyponatremia correction >10-12 mEq/L per 24h risks osmotic demyelination (per Verbalis/KDIGO).")

    # Hyperkalemia — calcium not first
    if "hyperkalemia" in lower and "ecg" in lower:
        if "dialysis" in lower.split(".")[0] and "calcium" not in lower[:120]:
            issues.append("With ECG changes, IV calcium should be mentioned first for membrane stabilization.")

    # FENa on diuretics
    if "fena" in lower and "diuretic" in lower:
        if "feurea" not in lower and "urea" not in lower:
            issues.append("On diuretics, FEUrea is preferred over FENa for prerenal vs intrinsic differentiation.")

    # Winter's formula typo check
    if "winter" in lower or "pco2" in lower:
        if "1.5" not in lower and "hco3" in lower:
            issues.append("Winter's formula uses (1.5 × HCO3) + 8 ± 2.")

    return issues
