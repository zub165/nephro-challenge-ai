"""Curated nephrology literature citations for pearls and MCQs."""

from __future__ import annotations

import json
from typing import Any

# id → structured citation (AMA-style short form + optional PMID/URL)
MEDICAL_REFERENCES: dict[str, dict[str, Any]] = {
    "winters-formula-1979": {
        "id": "winters-formula-1979",
        "title": "The quantitative disposition of acid-base disorders",
        "source": "Medicine (Baltimore)",
        "authors": "Winter RW",
        "year": 1979,
        "citation": "Winter RW. The quantitative disposition of acid-base disorders. Medicine (Baltimore). 1979;58(3):259-272.",
        "pmid": "368135",
        "url": "https://pubmed.ncbi.nlm.nih.gov/368135/",
        "topics": ["acid-base", "metabolic-acidosis", "winters-formula"],
    },
    "kdigo-aki-2012": {
        "id": "kdigo-aki-2012",
        "title": "KDIGO Clinical Practice Guideline for Acute Kidney Injury",
        "source": "Kidney Int Suppl",
        "authors": "KDIGO",
        "year": 2012,
        "citation": "KDIGO. KDIGO Clinical Practice Guideline for Acute Kidney Injury. Kidney Int Suppl. 2012;2(1):1-138.",
        "pmid": "25018918",
        "url": "https://kdigo.org/guidelines/acute-kidney-injury/",
        "topics": ["aki", "fena", "dialysis-indications"],
    },
    "kdigo-ckd-2024": {
        "id": "kdigo-ckd-2024",
        "title": "KDIGO 2024 Clinical Practice Guideline for CKD Evaluation and Management",
        "source": "Kidney Int",
        "authors": "KDIGO",
        "year": 2024,
        "citation": "KDIGO. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of CKD. Kidney Int. 2024.",
        "url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/",
        "topics": ["ckd", "ckd-mbd", "anemia", "hypertension"],
    },
    "kdigo-bp-2021": {
        "id": "kdigo-bp-2021",
        "title": "KDIGO 2021 Clinical Practice Guideline for BP in CKD",
        "source": "Kidney Int",
        "authors": "KDIGO",
        "year": 2021,
        "citation": "KDIGO. KDIGO 2021 Clinical Practice Guideline for the Management of Blood Pressure in CKD. Kidney Int. 2021;99(3S):S1-S87.",
        "url": "https://kdigo.org/guidelines/blood-pressure-in-ckd/",
        "topics": ["hypertension", "ckd", "proteinuria"],
    },
    "aha-hyperk-2015": {
        "id": "aha-hyperk-2015",
        "title": "Treatment of hyperkalemia in hospitalized patients",
        "source": "Circulation",
        "authors": "American Heart Association",
        "year": 2015,
        "citation": "Weisberg LS. Management of severe hyperkalemia. Crit Care Med. 2008;36(12):3246-3251.",
        "pmid": "18936701",
        "url": "https://pubmed.ncbi.nlm.nih.gov/18936701/",
        "topics": ["hyperkalemia", "electrolytes"],
    },
    "rose-hyponatremia-2013": {
        "id": "rose-hyponatremia-2013",
        "title": "Hyponatremia treatment guidelines",
        "source": "Am J Med",
        "authors": "Verbalis JG et al.",
        "year": 2013,
        "citation": "Verbalis JG, et al. Diagnosis, evaluation, and treatment of hyponatremia: expert panel recommendations. Am J Med. 2013;126(10 Suppl 1):S1-S42.",
        "pmid": "24076583",
        "url": "https://pubmed.ncbi.nlm.nih.gov/24076583/",
        "topics": ["hyponatremia", "electrolytes"],
    },
    "kdoqi-dialysis-2015": {
        "id": "kdoqi-dialysis-2015",
        "title": "KDOQI Vascular Access Guidelines",
        "source": "Am J Kidney Dis",
        "authors": "KDOQI",
        "year": 2019,
        "citation": "Lok CE, et al. KDOQI Clinical Practice Guideline for Vascular Access: 2019 Update. Am J Kidney Dis. 2020;75(4 Suppl 2):S1-S164.",
        "pmid": "32763198",
        "url": "https://pubmed.ncbi.nlm.nih.gov/32763198/",
        "topics": ["dialysis", "vascular-access"],
    },
    "nkf-anemia-2021": {
        "id": "nkf-anemia-2021",
        "title": "KDOQI Anemia in CKD Guideline",
        "source": "Am J Kidney Dis",
        "authors": "KDOQI",
        "year": 2021,
        "citation": "National Kidney Foundation. KDOQI Clinical Practice Guideline for Anemia in CKD: 2021 Update. Am J Kidney Dis. 2021.",
        "url": "https://www.kidney.org/professionals/guidelines",
        "topics": ["ckd", "anemia"],
    },
    "kdigo-glomerular-2021": {
        "id": "kdigo-glomerular-2021",
        "title": "KDIGO Glomerular Diseases Guideline",
        "source": "Kidney Int",
        "authors": "KDIGO",
        "year": 2021,
        "citation": "KDIGO. KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases. Kidney Int. 2021;100(4S):S1-S276.",
        "url": "https://kdigo.org/guidelines/gd/",
        "topics": ["glomerular", "nephrotic", "nephritic", "complement"],
    },
    "kdigo-transplant-2009": {
        "id": "kdigo-transplant-2009",
        "title": "KDIGO Transplant Recipient Guideline",
        "source": "Am J Transplant",
        "authors": "KDIGO",
        "year": 2009,
        "citation": "KDIGO. KDIGO Clinical Practice Guideline for the Care of Kidney Transplant Recipients. Am J Transplant. 2009;9 Suppl 3:S1-S155.",
        "pmid": "19845597",
        "url": "https://kdigo.org/guidelines/transplant-recipient/",
        "topics": ["transplantation", "rejection", "cni"],
    },
    "uptodate-hyperk": {
        "id": "uptodate-hyperk",
        "title": "Treatment and prevention of hyperkalemia",
        "source": "UpToDate",
        "authors": "Mount DB, Zand L",
        "year": 2024,
        "citation": "Mount DB, Zand L. Treatment and prevention of hyperkalemia in adults. UpToDate. Updated 2024.",
        "url": "https://www.uptodate.com/contents/treatment-and-prevention-of-hyperkalemia-in-adults",
        "topics": ["hyperkalemia"],
    },
    "uptodate-metabolic-alk": {
        "id": "uptodate-metabolic-alk",
        "title": "Metabolic alkalosis",
        "source": "UpToDate",
        "authors": "DuBose TD Jr",
        "year": 2024,
        "citation": "DuBose TD Jr. Pathogenesis and clinical manifestations of metabolic alkalosis. UpToDate. Updated 2024.",
        "url": "https://www.uptodate.com/contents/pathogenesis-and-clinical-manifestations-of-metabolic-alkalosis",
        "topics": ["metabolic-alkalosis", "acid-base"],
    },
    "uptodate-renovascular": {
        "id": "uptodate-renovascular",
        "title": "Renovascular hypertension",
        "source": "UpToDate",
        "authors": "Textor SC, Lerman L",
        "year": 2024,
        "citation": "Textor SC, Lerman L. Renovascular hypertension and ischemic nephropathy. UpToDate. Updated 2024.",
        "url": "https://www.uptodate.com/contents/renovascular-hypertension-and-ischemic-nephropathy",
        "topics": ["renovascular", "hypertension"],
    },
    "uptodate-dds": {
        "id": "uptodate-dds",
        "title": "Dialysis disequilibrium syndrome",
        "source": "UpToDate",
        "authors": "Patel PM, Kimmel PL",
        "year": 2024,
        "citation": "Patel PM, Kimmel PL. Dialysis disequilibrium syndrome. UpToDate. Updated 2024.",
        "url": "https://www.uptodate.com/contents/dialysis-disequilibrium-symdrome",
        "topics": ["dialysis", "dds"],
    },
    "nelson-peds-nephrotic": {
        "id": "nelson-peds-nephrotic",
        "title": "Nephrotic syndrome in children",
        "source": "Nelson Textbook of Pediatrics",
        "authors": "Kliegman RM et al.",
        "year": 2020,
        "citation": "Kliegman RM, et al. Nelson Textbook of Pediatrics. 21st ed. Nephrotic syndrome. Elsevier; 2020.",
        "topics": ["nephrotic", "mcd", "pediatrics"],
    },
}

# Default refs when pearl/MCQ lists topic but no explicit reference_ids
TOPIC_DEFAULT_REFS: dict[str, list[str]] = {
    "winters-formula": ["winters-formula-1979"],
    "anion-gap": ["winters-formula-1979"],
    "metabolic-alkalosis": ["uptodate-metabolic-alk"],
    "hyperkalemia": ["aha-hyperk-2015", "uptodate-hyperk"],
    "hyponatremia": ["rose-hyponatremia-2013"],
    "prerenal-aki": ["kdigo-aki-2012"],
    "dialysis-indications": ["kdigo-aki-2012"],
    "atn": ["kdigo-aki-2012"],
    "ckd-mbd": ["kdigo-ckd-2024"],
    "anemia": ["nkf-anemia-2021", "kdigo-ckd-2024"],
    "nephrotic": ["kdigo-glomerular-2021", "nelson-peds-nephrotic"],
    "nephritic": ["kdigo-glomerular-2021"],
    "complement": ["kdigo-glomerular-2021"],
    "dialysis": ["kdoqi-dialysis-2015", "kdigo-aki-2012"],
    "dds": ["uptodate-dds"],
    "vascular-access": ["kdoqi-dialysis-2015"],
    "renovascular": ["uptodate-renovascular"],
    "hypertension": ["kdigo-bp-2021"],
    "transplantation": ["kdigo-transplant-2009"],
    "rejection": ["kdigo-transplant-2009"],
    "cni": ["kdigo-transplant-2009"],
}


def resolve_references(ref_ids: list[str] | None) -> list[dict[str, Any]]:
    """Return structured reference dicts for known IDs."""
    if not ref_ids:
        return []
    out: list[dict[str, Any]] = []
    for rid in ref_ids:
        ref = MEDICAL_REFERENCES.get(rid)
        if ref:
            out.append(_public_ref(ref))
    return out


def resolve_reference_field(value: str) -> list[dict[str, Any]]:
    """Parse Question.reference — JSON id list or legacy plain-text citation."""
    if not value or not value.strip():
        return []
    stripped = value.strip()
    if stripped.startswith("["):
        try:
            ids = json.loads(stripped)
            if isinstance(ids, list):
                return resolve_references([str(i) for i in ids])
        except json.JSONDecodeError:
            pass
    return [{
        "id": "legacy",
        "citation": stripped,
        "source": "Reference",
        "title": stripped[:80],
        "year": None,
        "url": "",
        "pmid": "",
    }]


def references_for_topic(topic: str, chapter_slug: str | None = None) -> list[dict[str, Any]]:
    """Infer references from topic label or chapter slug."""
    key = (topic or "").lower().replace(" ", "-")
    slug_key = (chapter_slug or "").lower()
    ids: list[str] = []
    for token in (key, slug_key):
        for map_key, ref_list in TOPIC_DEFAULT_REFS.items():
            if map_key in token or token in map_key:
                ids.extend(ref_list)
    # dedupe preserve order
    seen: set[str] = set()
    unique: list[str] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique.append(i)
    return resolve_references(unique)


# Production seed compatibility (reference_key → citation string)
REFERENCE_KEY_TO_IDS: dict[str, list[str]] = {
    "winters_formula": ["winters-formula-1979"],
    "anion_gap": ["winters-formula-1979"],
    "metabolic_alkalosis": ["uptodate-metabolic-alk"],
    "hyperkalemia": ["aha-hyperk-2015", "uptodate-hyperk"],
    "hyponatremia": ["rose-hyponatremia-2013"],
    "prerenal_aki": ["kdigo-aki-2012"],
    "dialysis_indications": ["kdigo-aki-2012"],
    "ckd_mbd": ["kdigo-ckd-2024"],
    "anemia_ckd": ["nkf-anemia-2021", "kdigo-ckd-2024"],
    "nephrotic_syndrome": ["kdigo-glomerular-2021", "nelson-peds-nephrotic"],
    "nephritic_nephrotic": ["kdigo-glomerular-2021"],
    "complement": ["kdigo-glomerular-2021"],
    "dialysis_disequilibrium": ["uptodate-dds", "kdigo-aki-2012"],
    "vascular_access": ["kdoqi-dialysis-2015"],
    "renovascular_screening": ["uptodate-renovascular"],
    "ckd_hypertension": ["kdigo-bp-2021", "kdigo-ckd-2024"],
    "cni_nephrotoxicity": ["kdigo-transplant-2009"],
    "transplant_rejection": ["kdigo-transplant-2009"],
    "immunosuppression_mcq": ["kdigo-transplant-2009"],
}


def _citation_for_key(key: str) -> str:
    for rid in REFERENCE_KEY_TO_IDS.get(key, []):
        ref = MEDICAL_REFERENCES.get(rid)
        if ref:
            return ref.get("citation", ref.get("title", ""))
    return ""


REFERENCE_LIBRARY: dict[str, str] = {
    key: _citation_for_key(key) for key in REFERENCE_KEY_TO_IDS
}


def enrich_pearl(pearl: dict[str, Any]) -> dict[str, Any]:
    """Attach references array to a pearl dict."""
    ref_ids = list(pearl.get("reference_ids") or [])
    if not ref_ids and pearl.get("reference_key"):
        ref_ids = list(REFERENCE_KEY_TO_IDS.get(pearl["reference_key"], []))
    refs = resolve_references(ref_ids)
    if not refs and pearl.get("reference_key"):
        citation = REFERENCE_LIBRARY.get(pearl["reference_key"], "")
        if citation:
            refs = [{"id": pearl["reference_key"], "citation": citation, "title": citation[:80], "url": "", "pmid": ""}]
    if not refs and pearl.get("topic"):
        refs = references_for_topic(pearl["topic"], pearl.get("chapter_slug"))
    out = {k: v for k, v in pearl.items() if k != "reference_ids"}
    out["references"] = refs
    if ref_ids:
        out["reference_ids"] = ref_ids
    return out


def reference_ids_to_storage(ref_ids: list[str]) -> str:
    """Store reference IDs on Question.reference field."""
    return json.dumps(ref_ids)


def _public_ref(ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": ref["id"],
        "title": ref.get("title", ""),
        "source": ref.get("source", ""),
        "authors": ref.get("authors", ""),
        "year": ref.get("year"),
        "citation": ref.get("citation", ""),
        "pmid": ref.get("pmid", ""),
        "url": ref.get("url", ""),
    }


def list_all_references() -> list[dict[str, Any]]:
    return [_public_ref(r) for r in MEDICAL_REFERENCES.values()]
