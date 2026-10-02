"""25-day nephrology board calendar. Maps high-yield days onto seeded chapters."""

from __future__ import annotations

PLAN_LENGTH_DAYS = 25
TARGET_MIN_QUESTIONS = 1200
TARGET_MAX_QUESTIONS = 1500
WORKDAY_QUESTION_TARGET = 25
DAY_OFF_QUESTION_TARGET = 80
MORNING_QUESTION_COUNT = 18

# ISO weekday: Monday=1 … Sunday=7
DEFAULT_WORK_WEEKDAYS = [1, 2, 3, 4, 5]

BOARD_PREP_DAYS: list[dict] = [
    {
        "day": 1,
        "focus": "AKI + ICU nephrology",
        "high_yield": [
            "ATN vs prerenal",
            "urine sediment",
            "AIN/GN",
            "CRRT",
            "dialysis indications",
            "toxic alcohols",
        ],
        "chapter_slugs": ["acute-kidney-injury-icu"],
        "topic_slugs": ["prerenal-aki", "intrinsic-aki", "crrt", "dialysis-indications-aki"],
        "repetition": True,
    },
    {
        "day": 2,
        "focus": "AKI + ICU nephrology",
        "high_yield": ["CRRT dose", "circuit pressures", "AEIOU", "casts"],
        "chapter_slugs": ["acute-kidney-injury-icu"],
        "topic_slugs": ["crrt", "dialysis-indications-aki", "intrinsic-aki"],
        "repetition": True,
    },
    {
        "day": 3,
        "focus": "AKI + ICU nephrology",
        "high_yield": ["toxic alcohols", "sediment", "ATN vs AIN"],
        "chapter_slugs": ["acute-kidney-injury-icu", "nephrology-pharmacology"],
        "topic_slugs": ["intrinsic-aki", "crrt"],
        "repetition": True,
    },
    {
        "day": 4,
        "focus": "Electrolytes",
        "high_yield": ["hyponatremia", "SIADH", "DI", "correction limits"],
        "chapter_slugs": ["electrolytes"],
        "topic_slugs": ["hyponatremia"],
        "repetition": True,
    },
    {
        "day": 5,
        "focus": "Electrolytes",
        "high_yield": ["K disorders", "emergency hyperkalemia"],
        "chapter_slugs": ["electrolytes"],
        "topic_slugs": ["hyperkalemia"],
        "repetition": True,
    },
    {
        "day": 6,
        "focus": "Electrolytes",
        "high_yield": ["Mg", "Ca", "phosphate"],
        "chapter_slugs": ["electrolytes"],
        "topic_slugs": ["hypocalcemia-hypomagnesemia"],
        "repetition": True,
    },
    {
        "day": 7,
        "focus": "Acid–base",
        "high_yield": ["AG vs NAGMA", "Winter's formula", "mixed disorders"],
        "chapter_slugs": ["acid-base-disorders"],
        "topic_slugs": ["metabolic-acidosis", "mixed-acid-base-disorders"],
        "repetition": True,
    },
    {
        "day": 8,
        "focus": "Acid–base",
        "high_yield": ["RTA", "metabolic alkalosis", "compensation"],
        "chapter_slugs": ["acid-base-disorders"],
        "topic_slugs": ["renal-tubular-acidosis", "metabolic-alkalosis"],
        "repetition": True,
    },
    {
        "day": 9,
        "focus": "Glomerular disease",
        "high_yield": ["nephritic vs nephrotic", "complements", "serologies"],
        "chapter_slugs": ["glomerular-vascular"],
        "topic_slugs": ["nephrotic-syndrome", "nephritic-rpgn"],
        "repetition": True,
    },
    {
        "day": 10,
        "focus": "Glomerular disease",
        "high_yield": ["biopsy / IF / EM", "IgA", "ANCA"],
        "chapter_slugs": ["glomerular-vascular"],
        "topic_slugs": ["iga-nephropathy", "anca-vasculitis"],
        "repetition": True,
    },
    {
        "day": 11,
        "focus": "Glomerular disease",
        "high_yield": ["TMA", "complements", "biopsy patterns"],
        "chapter_slugs": ["glomerular-vascular"],
        "topic_slugs": ["thrombotic-microangiopathy", "nephritic-rpgn"],
        "repetition": True,
    },
    {
        "day": 12,
        "focus": "CKD",
        "high_yield": ["progression", "BP", "proteinuria therapy"],
        "chapter_slugs": ["chronic-kidney-disease"],
        "topic_slugs": ["ckd-staging-progression"],
        "repetition": False,
    },
    {
        "day": 13,
        "focus": "CKD",
        "high_yield": ["anemia", "CKD-MBD"],
        "chapter_slugs": ["chronic-kidney-disease"],
        "topic_slugs": ["anemia-of-ckd", "ckd-mbd"],
        "repetition": False,
    },
    {
        "day": 14,
        "focus": "Hemodialysis",
        "high_yield": ["prescription", "adequacy", "Kt/V"],
        "chapter_slugs": ["dialysis"],
        "topic_slugs": ["hemodialysis-principles", "dialysis-adequacy"],
        "repetition": True,
    },
    {
        "day": 15,
        "focus": "Hemodialysis",
        "high_yield": ["access", "hypotension", "water/dialysate"],
        "chapter_slugs": ["dialysis"],
        "topic_slugs": ["vascular-access", "hemodialysis-complications"],
        "repetition": True,
    },
    {
        "day": 16,
        "focus": "Hemodialysis",
        "high_yield": ["complications", "CRRT vs HD prescriptions"],
        "chapter_slugs": ["dialysis", "acute-kidney-injury-icu"],
        "topic_slugs": ["hemodialysis-complications", "crrt"],
        "repetition": True,
    },
    {
        "day": 17,
        "focus": "Peritoneal dialysis",
        "high_yield": ["prescription", "PET", "peritonitis", "UF failure"],
        "chapter_slugs": ["dialysis"],
        "topic_slugs": ["peritoneal-dialysis"],
        "repetition": False,
    },
    {
        "day": 18,
        "focus": "Transplant",
        "high_yield": ["rejection", "DSA", "C4d", "biopsy patterns"],
        "chapter_slugs": ["transplantation"],
        "topic_slugs": [],
        "repetition": True,
    },
    {
        "day": 19,
        "focus": "Transplant",
        "high_yield": ["immunosuppressants", "infections"],
        "chapter_slugs": ["transplantation", "nephrology-pharmacology"],
        "topic_slugs": [],
        "repetition": True,
    },
    {
        "day": 20,
        "focus": "Transplant",
        "high_yield": ["rejection patterns", "DSA/C4d", "pathology images"],
        "chapter_slugs": ["transplantation"],
        "topic_slugs": [],
        "repetition": True,
    },
    {
        "day": 21,
        "focus": "HTN + pregnancy",
        "high_yield": ["resistant HTN", "renovascular", "preeclampsia/HELLP"],
        "chapter_slugs": ["hypertension"],
        "topic_slugs": [
            "resistant-hypertension",
            "renovascular-hypertension",
            "secondary-hypertension",
        ],
        "repetition": False,
    },
    {
        "day": 22,
        "focus": "Stones + tubules/cystic",
        "high_yield": ["stone workup", "inherited tubular disorders", "ADPKD"],
        "chapter_slugs": ["tubulointerstitial-cystic"],
        "topic_slugs": ["adpkd", "chronic-tubulointerstitial-nephritis"],
        "repetition": False,
    },
    {
        "day": 23,
        "focus": "Onco / toxicology",
        "high_yield": ["TLS", "myeloma", "chemotherapy", "drug nephrotoxicity", "poisonings"],
        "chapter_slugs": ["nephrology-pharmacology", "acute-kidney-injury-icu"],
        "topic_slugs": [],
        "repetition": True,
    },
    {
        "day": 24,
        "focus": "Full mixed simulation",
        "high_yield": ["timed mixed questions", "remaining weak areas"],
        "chapter_slugs": [],
        "topic_slugs": [],
        "mixed": True,
        "repetition": False,
    },
    {
        "day": 25,
        "focus": "Final rapid review",
        "high_yield": [
            "incorrect questions",
            "formulas",
            "pathology images",
            "drug toxicities",
        ],
        "chapter_slugs": [],
        "topic_slugs": [],
        "review_only": True,
        "repetition": True,
    },
]


def day_spec(day_number: int) -> dict:
    if day_number < 1:
        day_number = 1
    if day_number > PLAN_LENGTH_DAYS:
        day_number = PLAN_LENGTH_DAYS
    return BOARD_PREP_DAYS[day_number - 1]
