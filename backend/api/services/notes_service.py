"""Organize pasted study notes into board-review chapters."""

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from api.models import Chapter, Topic
from api.services.ai_service import _chat_completion

CHAPTER_KEYWORDS: Dict[str, List[str]] = {
    "acid-base-disorders": [
        "acid base", "acid-base", "anion gap", "abg", "bicarbonate", "hco3",
        "metabolic acidosis", "metabolic alkalosis", "respiratory acidosis",
        "winter", "mudples", "delta gap",
    ],
    "electrolytes": [
        "sodium", "hyponatremia", "hypernatremia", "potassium", "hyperkalemia",
        "hypokalemia", "calcium", "phosphate", "magnesium", "electrolyte",
    ],
    "aki": [
        "acute kidney", "aki", "prerenal", "atn", "fena", "feurea", "oliguria",
        "postrenal", "tubular necrosis", "obstructive uropathy", "retroperitoneal",
        "hydronephrosis", "lithium", "toxicity", "overdose",
    ],
    "ckd": [
        "chronic kidney", "ckd", "ckd-mbd", "hyperparathyroid", "phosphate binder",
        "egfr", "progression", "anemia ckd", "vasculitis", "pulmonary hypertension",
    ],
    "glomerular-diseases": [
        "glomerular", "nephrotic", "nephritic", "proteinuria", "hematuria",
        "iga", "fsgs", "membranous", "minimal change", "gn ", "anca", "p-anca",
        "vegf", "bevacizumab", "tma", "thrombotic microangiopathy", "podocyte",
    ],
    "dialysis": [
        "dialysis", "hemodialysis", "peritoneal", "fistula", "disequilibrium",
        "dialyzer", "ultrafiltration", "access", "whole-bowel", "whole bowel",
    ],
    "hypertension": [
        "hypertension", "htn", "blood pressure", "renovascular", "renal artery stenosis",
        "ace inhibitor", "arb", "aldosterone",
    ],
    "transplantation": [
        "transplant", "transplantation", "immunosuppression", "tacrolimus", "cyclosporine",
        "rejection", "graft", "donor", "calcineurin",
    ],
}


def normalize_note_content(text: str) -> str:
    """Normalize note text for duplicate detection."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def dedupe_note_dicts(notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate content within a single organize batch."""
    seen: set[str] = set()
    unique: List[Dict[str, Any]] = []
    for note in notes:
        key = normalize_note_content(note.get("content", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(note)
    return unique


def _strip_pearls_from_remainder(remainder: str, pearls: List[str]) -> str:
    """Remove lines already saved as separate pearl notes."""
    if not remainder or not pearls:
        return remainder.strip()
    pearl_keys = {normalize_note_content(p) for p in pearls}
    kept: List[str] = []
    for line in remainder.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        bare = re.sub(r"^(?:Pearl|Think|Mnemonic)\s*:\s*", "", stripped, flags=re.I).strip()
        if normalize_note_content(stripped) in pearl_keys:
            continue
        if normalize_note_content(bare) in pearl_keys:
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def _split_note_lines(raw_text: str) -> List[str]:
    """Legacy line split — used as final fallback."""
    text = raw_text.strip()
    if not text:
        return []
    chunks = re.split(r"\n\s*(?:[-•*]|\d+[.)])\s*", text)
    lines = [c.strip() for c in chunks if c.strip()]
    if len(lines) <= 1 and "\n" in text:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines and text.strip():
        lines = [text.strip()]
    return lines


def _infer_topic_title(block: str) -> str:
    m = re.search(r"Question\s+(\d+)", block, re.I)
    if m:
        return f"Question {m.group(1)}"
    m = re.search(
        r"(?:@ |✅ )?(?:Correct Answer|Answer)\s*:\s*([A-F])[.\s)]*\s*([^\n.]+)",
        block,
        re.I,
    )
    if m:
        return f"Q — {m.group(1)}. {m.group(2).strip()[:90]}"
    first = block.split("\n")[0].strip()
    if first and len(first) < 100:
        if "—" in first or " - " in first:
            return first.split("—")[0].split(" - ")[0].strip()[:90]
        if first.endswith(":"):
            return first[:-1].strip()[:90]
    return ""


def _extract_pearl_lines(block: str) -> tuple:
    """Pull short board pearls out of a block; return (pearls, remainder)."""
    pearls: List[str] = []
    remainder = block

    for m in re.finditer(
        r"Board Pearls?\s*[:\n]?\s*(.*?)(?=\n(?:Why not|Key clues|Mechanism|Workup|Question|A \d{1,3}-year|✅|@ Correct)|\Z)",
        block,
        re.I | re.S,
    ):
        section = m.group(1).strip()
        for line in section.split("\n"):
            line = re.sub(r"^[•\-*]\s*", "", line.strip())
            line = re.sub(r"^[A-F][.)]\s*", "", line)
            if line and len(line) <= 280:
                pearls.append(line)

    remainder = re.sub(
        r"Board Pearls?\s*[:\n]?\s*.*?(?=\n(?:Why not|Key clues|Mechanism|Workup|Question|✅|@ Correct)|\Z)",
        "",
        remainder,
        flags=re.I | re.S,
    )

    for line in block.split("\n"):
        stripped = line.strip()
        m = re.match(r"^(?:Pearl|Think|Mnemonic)\s*:\s*(.+)", stripped, re.I)
        if m and len(m.group(1)) <= 280:
            pearls.append(m.group(1).strip())

    seen = set()
    unique_pearls = []
    for p in pearls:
        key = normalize_note_content(p)
        if key not in seen:
            seen.add(key)
            unique_pearls.append(p)

    remainder = _strip_pearls_from_remainder(remainder, unique_pearls)
    return unique_pearls, remainder.strip()


def _split_into_blocks(text: str) -> List[str]:
    text = re.sub(r"\r\n?", "\n", text.strip())
    if not text:
        return []

    parts = re.split(r"(?=Question\s+\d+)", text, flags=re.I)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    parts = re.split(
        r"(?=@\s*Correct Answer:)|(?=\nA \d{1,3}-year-old )",
        text,
        flags=re.I,
    )
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    parts = re.split(r"\n\n+(?=(?:Board Pearl|Key clues|Workup|Mechanism)\b)", text, flags=re.I)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    return _split_note_lines(text)


def _split_study_items(raw_text: str) -> List[Dict[str, str]]:
    """Split pasted board-review text into learnable study units."""
    items: List[Dict[str, str]] = []
    for block in _split_into_blocks(raw_text):
        block = block.strip()
        if not block:
            continue
        topic = _infer_topic_title(block)
        pearl_lines, remainder = _extract_pearl_lines(block)
        for pearl in pearl_lines:
            items.append({
                "content": pearl,
                "topic_title": topic or pearl[:60],
            })
        if remainder:
            items.append({
                "content": remainder,
                "topic_title": topic,
            })
    return dedupe_note_dicts(items)

def _chapter_catalog() -> List[Dict[str, Any]]:
    catalog = []
    for chapter in Chapter.objects.prefetch_related("topics").order_by("order_index"):
        catalog.append({
            "slug": chapter.slug,
            "title": chapter.title,
            "topics": [t.title for t in chapter.topics.all()],
        })
    return catalog


def _score_chapter_slug(line: str, slug: str) -> int:
    lower = line.lower()
    score = 0
    for keyword in CHAPTER_KEYWORDS.get(slug, []):
        if keyword in lower:
            score += 2
    title = slug.replace("-", " ")
    if title in lower:
        score += 3
    return score


def _keyword_classify(line: str, chapters: List[Chapter]) -> Optional[Chapter]:
    best_chapter = None
    best_score = 0
    for chapter in chapters:
        score = _score_chapter_slug(line, chapter.slug)
        title_words = chapter.title.lower()
        if title_words in line.lower():
            score += 4
        if score > best_score:
            best_score = score
            best_chapter = chapter
    return best_chapter if best_score >= 2 else None


def _guess_topic(line: str, chapter: Optional[Chapter]) -> str:
    if not chapter:
        return ""
    lower = line.lower()
    for topic in chapter.topics.all():
        if topic.title.lower() in lower:
            return topic.title
        if topic.slug.replace("-", " ") in lower:
            return topic.title
    return ""


def organize_notes_with_keywords(raw_text: str) -> List[Dict[str, Any]]:
    chapters = list(Chapter.objects.prefetch_related("topics").order_by("order_index"))
    organized: List[Dict[str, Any]] = []
    items = _split_study_items(raw_text)
    if not items:
        items = [{"content": ln, "topic_title": ""} for ln in _split_note_lines(raw_text)]
    for item in items:
        line = item["content"]
        chapter = _keyword_classify(line, chapters)
        topic_hint = item.get("topic_title") or ""
        topic = topic_hint or _guess_topic(line, chapter)
        organized.append({
            "chapter_slug": chapter.slug if chapter else None,
            "chapter_title": chapter.title if chapter else None,
            "topic_title": topic[:150],
            "content": line,
        })
    return dedupe_note_dicts(organized)


def organize_notes_with_ai(raw_text: str) -> Optional[List[Dict[str, Any]]]:
    catalog = _chapter_catalog()
    if not catalog:
        return None

    prompt = (
        "You are a nephrology board-review tutor. The user pasted MCQ explanations or study notes. "
        "Split them into learnable study units and assign each to the best chapter.\n\n"
        "Rules:\n"
        "- One MCQ or topic per note.\n"
        "- Put the question number or diagnosis in topic_title (e.g. 'Question 210 — Obstructive uropathy').\n"
        "- Extract Board Pearls as separate short notes (under 200 chars).\n"
        "- Keep case explanations structured with: Correct Answer, Key clues, Why not others, Mechanism.\n"
        "- Use chapter_slug exactly from the catalog below.\n\n"
        f"Available chapters:\n{json.dumps(catalog, indent=2)}\n\n"
        "User notes:\n"
        f"{raw_text}\n\n"
        "Return ONLY valid JSON:\n"
        '{"notes":[{"chapter_slug":"slug-or-null","topic_title":"short title","content":"study content"}]}'
    )

    content = _chat_completion(
        [
            {"role": "system", "content": "Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.3,
        json_mode=True,
    )
    if not content:
        return None

    try:
        data = json.loads(content)
        notes = data.get("notes", [])
        if not isinstance(notes, list):
            return None
        slug_map = {c.slug: c for c in Chapter.objects.all()}
        result = []
        for item in notes:
            if not isinstance(item, dict) or not item.get("content"):
                continue
            slug = item.get("chapter_slug")
            chapter = slug_map.get(slug) if slug else None
            result.append({
                "chapter_slug": chapter.slug if chapter else None,
                "chapter_title": chapter.title if chapter else None,
                "topic_title": str(item.get("topic_title", ""))[:150],
                "content": str(item["content"]).strip(),
            })
        return dedupe_note_dicts(result) if result else None
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def organize_pasted_notes(raw_text: str) -> Dict[str, Any]:
    """Classify pasted notes by chapter. AI first, keyword rules as fallback."""
    organized = organize_notes_with_ai(raw_text)
    method = "ai"
    if not organized:
        organized = organize_notes_with_keywords(raw_text)
        method = "keywords"
    return {
        "batch_id": str(uuid.uuid4()),
        "method": method,
        "notes": organized,
        "total": len(organized),
    }
