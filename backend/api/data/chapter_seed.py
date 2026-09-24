"""Chapter-wise board MCQ seed data with bundled step animations on GitHub Pages."""

ANIMATION_BASE = "https://zub165.github.io/nephro-challenge-ai/animations"

CHAPTERS = [
    {
        "title": "Acid-Base Disorders",
        "slug": "acid-base-disorders",
        "order_index": 1,
        "description": "ABG interpretation, anion gap, metabolic and respiratory acid-base board questions.",
        "icon": "BeakerIcon",
        "category_slug": "acid-base-disorders",
        "topics": [
            {
                "title": "Metabolic Acidosis",
                "slug": "metabolic-acidosis",
                "description": "High anion gap vs normal anion gap metabolic acidosis.",
                "lessons": [
                    {
                        "title": "Anion Gap Acidosis Algorithm",
                        "lesson_type": "animation",
                        "summary": "Visual MUDPILES mnemonic and diagnostic workflow for metabolic acidosis.",
                        "animation_url": f"{ANIMATION_BASE}/anion-gap-acidosis.json",
                        "thumbnail_url": "",
                        "duration_seconds": 90,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 30-year-old woman with type 1 diabetes presents with nausea, vomiting, and Kussmaul breathing. ABG: pH 7.15, PCO2 25, HCO3 8.",
                        "labs": {"pH": "7.15", "PCO2": "25", "HCO3": "8", "Na": "138", "Cl": "100"},
                        "question_text": "What is the most appropriate interpretation of this acid-base disorder?",
                        "explanation": "Low pH indicates acidemia. Low HCO3 indicates metabolic acidosis. Winter's formula: expected PCO2 = (1.5 × 8) + 8 ± 2 = 20 ± 2. Measured PCO2 of 25 is higher than expected, suggesting concurrent respiratory acidosis or incomplete compensation.",
                        "clinical_pearl": "Winter's formula: Expected PCO2 = (1.5 × HCO3) + 8 ± 2.",
                        "reference_ids": ["winters-formula-1979"],
                        "choices": [
                            ("A", "Metabolic alkalosis with respiratory compensation", False, "pH is acidemic, not alkalemic."),
                            ("B", "Metabolic acidosis with appropriate respiratory compensation", False, "PCO2 is higher than Winter's formula predicts."),
                            ("C", "Metabolic acidosis with concurrent respiratory acidosis", True, None),
                            ("D", "Respiratory alkalosis with metabolic compensation", False, "Primary disorder is metabolic, not respiratory."),
                        ],
                    },
                ],
            },
            {
                "title": "Metabolic Alkalosis",
                "slug": "metabolic-alkalosis",
                "description": "Volume status, chloride responsiveness, and diuretic-induced alkalosis.",
                "lessons": [
                    {
                        "title": "Chloride-Responsive Alkalosis",
                        "lesson_type": "animation",
                        "summary": "Urine chloride algorithm for metabolic alkalosis workup.",
                        "animation_url": f"{ANIMATION_BASE}/metabolic-alkalosis.json",
                        "thumbnail_url": "",
                        "duration_seconds": 75,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "question_text": "A patient on loop diuretics has pH 7.48 and HCO3 32. Urine chloride is 8 mEq/L. What is the best initial treatment?",
                        "explanation": "Urine Cl < 20 mEq/L indicates chloride-responsive (saline-responsive) metabolic alkalosis, commonly from vomiting or diuretics. Treatment is volume and chloride repletion with normal saline.",
                        "clinical_pearl": "Urine Cl < 20 = chloride-responsive alkalosis. Urine Cl > 20 = chloride-resistant.",
                        "reference_ids": ["uptodate-metabolic-alk"],
                        "choices": [
                            ("A", "IV normal saline", True, None),
                            ("B", "Acetazolamide", False, "Used for chloride-resistant alkalosis."),
                            ("C", "Amiloride", False, "For mineralocorticoid excess, not diuretic-induced alkalosis."),
                            ("D", "Hydrochloric acid infusion", False, "Reserved for severe refractory cases."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Electrolytes",
        "slug": "electrolytes",
        "order_index": 2,
        "description": "Sodium, potassium, calcium, phosphate, and magnesium disorders.",
        "icon": "CircleStackIcon",
        "category_slug": "electrolyte-disorders",
        "topics": [
            {
                "title": "Hyperkalemia",
                "slug": "hyperkalemia",
                "description": "Emergency management of life-threatening hyperkalemia.",
                "lessons": [
                    {
                        "title": "Emergency Hyperkalemia Algorithm",
                        "lesson_type": "animation",
                        "summary": "Fast visual algorithm: stabilize membrane, shift K+, remove K+.",
                        "animation_url": f"{ANIMATION_BASE}/hyperkalemia-algorithm.json",
                        "thumbnail_url": "",
                        "duration_seconds": 120,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 64-year-old man on hemodialysis missed dialysis and presents with weakness. ECG shows peaked T waves. K 6.9 mEq/L.",
                        "labs": {"Na": "138", "K": "6.9", "HCO3": "18", "BUN": "82", "Cr": "9.4"},
                        "question_text": "What is the best immediate next step?",
                        "explanation": "Severe hyperkalemia with ECG changes requires immediate cardiac membrane stabilization with IV calcium before shifting or removing potassium.",
                        "clinical_pearl": "In hyperkalemia with ECG changes, give IV calcium first.",
                        "reference_ids": ["aha-hyperk-2015", "uptodate-hyperk"],
                        "choices": [
                            ("A", "Sodium polystyrene sulfonate", False, "Too slow for emergency stabilization."),
                            ("B", "IV calcium gluconate", True, None),
                            ("C", "Oral patiromer", False, "Too slow for life-threatening hyperkalemia."),
                            ("D", "Dietary potassium restriction only", False, "Inadequate for ECG changes."),
                        ],
                    },
                ],
            },
            {
                "title": "Hyponatremia",
                "slug": "hyponatremia",
                "description": "Acute vs chronic hyponatremia and osmotic demyelination risk.",
                "lessons": [
                    {
                        "title": "Hyponatremia Correction Limits",
                        "lesson_type": "animation",
                        "summary": "Safe sodium correction rates and ODS prevention.",
                        "animation_url": f"{ANIMATION_BASE}/hyponatremia-correction.json",
                        "thumbnail_url": "",
                        "duration_seconds": 100,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "question_text": "A patient with chronic hyponatremia (Na 118) is being treated. What is the maximum recommended sodium correction in the first 24 hours?",
                        "explanation": "In chronic hyponatremia, sodium should not rise more than 8-10 mEq/L in 24 hours to prevent osmotic demyelination syndrome (ODS).",
                        "clinical_pearl": "Correct chronic hyponatremia slowly: ≤8-10 mEq/L per 24 hours.",
                        "reference_ids": ["rose-hyponatremia-2013"],
                        "choices": [
                            ("A", "4 mEq/L", False, "This is within limits but not the maximum."),
                            ("B", "8-10 mEq/L", True, None),
                            ("C", "15 mEq/L", False, "Exceeds safe correction rate."),
                            ("D", "20 mEq/L", False, "Dangerously fast; high ODS risk."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Acute Kidney Injury",
        "slug": "aki",
        "order_index": 3,
        "description": "Prerenal, intrinsic, postrenal AKI and indications for RRT.",
        "icon": "ExclamationTriangleIcon",
        "category_slug": "acute-kidney-injury",
        "topics": [
            {
                "title": "Prerenal AKI",
                "slug": "prerenal-aki",
                "description": "Volume depletion, heart failure, and hepatorenal syndrome.",
                "lessons": [
                    {
                        "title": "FENa vs FEUrea in AKI",
                        "lesson_type": "animation",
                        "summary": "When to use fractional excretion of sodium vs urea.",
                        "animation_url": f"{ANIMATION_BASE}/fena-feuera.json",
                        "thumbnail_url": "",
                        "duration_seconds": 85,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "easy",
                        "case_text": "A 70-year-old man with CHF develops AKI after aggressive diuresis.",
                        "question_text": "Which lab finding is most consistent with prerenal AKI?",
                        "explanation": "Prerenal AKI shows FENa <1%, urine osmolality >500, and BUN:Cr >20:1 indicating preserved tubular function with decreased perfusion.",
                        "clinical_pearl": "FENa <1% suggests prerenal cause (unless on diuretics — then use FEUrea).",
                        "reference_ids": ["kdigo-aki-2012"],
                        "choices": [
                            ("A", "FENa < 1% and urine osmolality > 500", True, None),
                            ("B", "FENa > 3% and muddy brown casts", False, "Suggests ATN, not prerenal."),
                            ("C", "Urine sodium > 40 mEq/L", False, "Indicates intrinsic renal failure."),
                            ("D", "BUN:Cr ratio < 10:1", False, "Low ratio suggests intrinsic renal disease."),
                        ],
                    },
                ],
            },
            {
                "title": "Indications for Dialysis",
                "slug": "dialysis-indications-aki",
                "description": "AEIOU mnemonic for emergent dialysis in AKI.",
                "lessons": [
                    {
                        "title": "AEIOU Dialysis Indications",
                        "lesson_type": "animation",
                        "summary": "Acidosis, Electrolytes, Intoxication, Overload, Uremia.",
                        "animation_url": f"{ANIMATION_BASE}/aeiou-dialysis.json",
                        "thumbnail_url": "",
                        "duration_seconds": 60,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "question_text": "Which of the following is an absolute indication for emergent hemodialysis in AKI?",
                        "explanation": "Refractory hyperkalemia with ECG changes (E in AEIOU) is an emergent dialysis indication. Severe acidosis, volume overload, and uremic encephalopathy are also indications.",
                        "clinical_pearl": "AEIOU: Acidosis, Electrolytes (K+), Intoxication, Overload, Uremia.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "choices": [
                            ("A", "BUN 80 mg/dL without symptoms", False, "Uremia alone without symptoms is not emergent."),
                            ("B", "Refractory hyperkalemia with ECG changes", True, None),
                            ("C", "Creatinine 4.0 mg/dL", False, "Cr level alone is not an indication."),
                            ("D", "Mild metabolic acidosis pH 7.30", False, "Not refractory or severe."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Chronic Kidney Disease",
        "slug": "ckd",
        "order_index": 4,
        "description": "CKD staging, MBD, anemia, and progression.",
        "icon": "HeartIcon",
        "category_slug": "chronic-kidney-disease",
        "topics": [
            {
                "title": "CKD-Mineral Bone Disease",
                "slug": "ckd-mbd",
                "description": "Phosphate, calcium, PTH targets and management.",
                "lessons": [
                    {
                        "title": "CKD-MBD Management Pathway",
                        "lesson_type": "animation",
                        "summary": "Stepwise approach to phosphate, calcium, and PTH.",
                        "animation_url": f"{ANIMATION_BASE}/ckd-mbd-pathway.json",
                        "thumbnail_url": "",
                        "duration_seconds": 110,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "CKD stage 4: phosphate 6.5, calcium 8.2, PTH 350 pg/mL.",
                        "question_text": "What is the most appropriate initial management?",
                        "explanation": "Secondary hyperparathyroidism with hyperphosphatemia is managed with dietary phosphate restriction and phosphate binders first.",
                        "clinical_pearl": "CKD stage 4 PTH target: 2-9× upper normal limit.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "choices": [
                            ("A", "Parathyroidectomy", False, "Reserved for refractory tertiary HPT."),
                            ("B", "Calcium carbonate and dietary phosphate restriction", True, None),
                            ("C", "IV calcitriol as first-line", False, "Binders and diet come first."),
                            ("D", "No intervention", False, "Elevated phosphate and PTH require treatment."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Glomerular Diseases",
        "slug": "glomerular-diseases",
        "order_index": 5,
        "description": "Nephritic and nephrotic syndromes, GN workup.",
        "icon": "DocumentTextIcon",
        "category_slug": "glomerular-diseases",
        "topics": [
            {
                "title": "Nephrotic Syndrome",
                "slug": "nephrotic-syndrome",
                "description": "Minimal change, FSGS, membranous nephropathy.",
                "lessons": [
                    {
                        "title": "Nephrotic vs Nephritic Syndrome",
                        "lesson_type": "animation",
                        "summary": "Compare proteinuria patterns, complement, and biopsy findings.",
                        "animation_url": f"{ANIMATION_BASE}/nephrotic-nephritic.json",
                        "thumbnail_url": "",
                        "duration_seconds": 95,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 6-year-old boy with periorbital edema, 3+ proteinuria, albumin 2.0 g/dL, no hematuria.",
                        "question_text": "What is the most likely diagnosis?",
                        "explanation": "Minimal change disease is the most common cause of nephrotic syndrome in children, presenting with heavy proteinuria and edema without hematuria.",
                        "clinical_pearl": "MCD accounts for 80-90% of childhood nephrotic syndrome.",
                        "reference_ids": ["kdigo-glomerular-2021", "nelson-peds-nephrotic"],
                        "choices": [
                            ("A", "FSGS", False, "Less common in young children."),
                            ("B", "Minimal change disease", True, None),
                            ("C", "IgA nephropathy", False, "Nephritic, not nephrotic."),
                            ("D", "Membranoproliferative GN", False, "Usually presents with hematuria."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Dialysis",
        "slug": "dialysis",
        "order_index": 6,
        "description": "Hemodialysis, peritoneal dialysis, access, and complications.",
        "icon": "UserGroupIcon",
        "category_slug": "dialysis",
        "topics": [
            {
                "title": "Hemodialysis Complications",
                "slug": "hd-complications",
                "description": "Intradialytic hypotension, disequilibrium, access issues.",
                "lessons": [
                    {
                        "title": "Intradialytic Complications",
                        "lesson_type": "animation",
                        "summary": "Distinguish disequilibrium, hypotension, and hemolysis.",
                        "animation_url": f"{ANIMATION_BASE}/hd-complications.json",
                        "thumbnail_url": "",
                        "duration_seconds": 80,
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "During the last hour of HD, a patient develops headache, nausea, confusion. BP 180/100.",
                        "question_text": "What is the most likely diagnosis?",
                        "explanation": "Dialysis disequilibrium syndrome from rapid urea removal causes cerebral edema. Presents with headache, nausea, hypertension, and confusion near end of dialysis.",
                        "clinical_pearl": "DDS is more common with BUN >150-200 in new dialysis patients.",
                        "reference_ids": ["uptodate-dds", "kdigo-aki-2012"],
                        "choices": [
                            ("A", "Intradialytic hypotension", False, "BP is elevated, not low."),
                            ("B", "Dialysis disequilibrium syndrome", True, None),
                            ("C", "Air embolism", False, "Presents with sudden cardiovascular collapse."),
                            ("D", "First-use syndrome", False, "Occurs at start of dialysis with new dialyzer."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Hypertension",
        "slug": "hypertension",
        "order_index": 7,
        "description": "Primary and secondary hypertension, renovascular disease, and kidney-related BP management.",
        "icon": "HeartIcon",
        "category_slug": "hypertension",
        "topics": [
            {
                "title": "Renovascular Hypertension",
                "slug": "renovascular-hypertension",
                "description": "Renal artery stenosis workup and management.",
                "lessons": [],
                "mcqs": [],
            },
        ],
    },
    {
        "title": "Transplantation",
        "slug": "transplantation",
        "order_index": 8,
        "description": "Kidney transplant immunology, immunosuppression, rejection, and complications.",
        "icon": "UserGroupIcon",
        "category_slug": "transplantation",
        "topics": [
            {
                "title": "Immunosuppression",
                "slug": "immunosuppression",
                "description": "Calcineurin inhibitors, antimetabolites, and rejection treatment.",
                "lessons": [],
                "mcqs": [],
            },
        ],
    },
]
