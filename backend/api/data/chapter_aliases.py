"""Canonical 10-chapter board taxonomy plus legacy slug aliases on production."""

from api.data.board_exam_seed import EXPECTED_CHAPTER_ORDER

CANONICAL_CHAPTER_SLUGS = [slug for slug, _ in EXPECTED_CHAPTER_ORDER]

# Older seed_data used short slugs; later curriculum used ABIM-aligned slugs.
# Both rows still exist on GoDaddy and split questions vs lessons.
LEGACY_CHAPTER_SLUGS = {
    "aki": "acute-kidney-injury-icu",
    "ckd": "chronic-kidney-disease",
    "glomerular-diseases": "glomerular-vascular",
}

WEB_CHAPTER_LABELS = {
    "acid-base-disorders": "Acid-Base",
    "electrolytes": "Electrolytes",
    "acute-kidney-injury-icu": "AKI & ICU",
    "chronic-kidney-disease": "CKD",
    "hypertension": "HTN",
    "dialysis": "Dialysis",
    "tubulointerstitial-cystic": "Tubules / Cystic",
    "glomerular-vascular": "Glomerular",
    "transplantation": "Transplant",
    "nephrology-pharmacology": "Onco / Tox / Drugs",
}


def canonical_slug(slug: str | None) -> str | None:
    if not slug:
        return slug
    return LEGACY_CHAPTER_SLUGS.get(slug, slug)


def slugs_for_query(slug: str | None) -> list[str]:
    canon = canonical_slug(slug)
    if not canon:
        return []
    aliases = [old for old, new in LEGACY_CHAPTER_SLUGS.items() if new == canon]
    return [canon, *aliases]
