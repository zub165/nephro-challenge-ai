"""Chapter-wise board MCQ seed data with bundled step animations on GitHub Pages.

Ten-chapter taxonomy follows the ABIM Nephrology Blueprint (March 2026) content
areas, merged into the app's chapter model. All MCQs are original teaching content
written for this repository and seeded with `needs_review` medical review status.
"""

ANIMATION_BASE = "https://zub165.github.io/nephro-challenge-ai/animations"
MEDICAL_ASSET_BASE = "https://zub165.github.io/nephro-challenge-ai/medical"

CHAPTERS = [
    {
        "title": "Acid-Base Disorders",
        "slug": "acid-base-disorders",
        "order_index": 1,
        "description": "Anion gap, metabolic and respiratory acid-base board questions, mixed disorders, and renal tubular acidosis.",
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
                        "lesson_slug": "anion-gap-acidosis-algorithm",
                        "lesson_type": "animation",
                        "summary": "Visual MUDPILES mnemonic and diagnostic workflow for metabolic acidosis.",
                        "animation_url": f"{ANIMATION_BASE}/anion-gap-acidosis.json",
                        "duration_seconds": 90,
                        "reference_ids": ["winters-formula-1979", "abim-nephrology-blueprint-2026"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 30-year-old woman with type 1 diabetes presents with nausea, vomiting, and Kussmaul breathing. ABG: pH 7.15, PCO2 25, HCO3 8.",
                        "labs": {"pH": "7.15", "PCO2": "25", "HCO3": "8", "Na": "138", "Cl": "100"},
                        "question_text": "What is the most appropriate interpretation of this acid-base disorder?",
                        "explanation": "Low pH indicates acidemia. Low HCO3 indicates metabolic acidosis. Winter's formula predicts PCO2 = (1.5 x 8) + 8 +/- 2 = 20 +/- 2. A measured PCO2 of 25 is higher than expected, so there is a concurrent respiratory acidosis (or inappropriate compensation). Anion gap is 138 - (100 + 8) = 30, which is elevated and consistent with ketoacidosis.",
                        "clinical_pearl": "Winter's formula: expected PCO2 = (1.5 x HCO3) + 8 +/- 2. PCO2 above that range means a second, respiratory process.",
                        "reference_ids": ["winters-formula-1979"],
                        "lesson_slug": "anion-gap-acidosis-algorithm",
                        "choices": [
                            ("A", "Metabolic alkalosis with respiratory compensation", False, "pH is acidemic, not alkalemic."),
                            ("B", "Metabolic acidosis with appropriate respiratory compensation", False, "PCO2 25 exceeds the 18-22 range Winter's formula predicts."),
                            ("C", "Metabolic acidosis with concurrent respiratory acidosis", True, None),
                            ("D", "Respiratory alkalosis with metabolic compensation", False, "The primary disorder is metabolic, not respiratory."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 66-year-old man with diarrhea is found on a routine chemistry panel: Na 140, Cl 118, HCO3 14, pH 7.38.",
                        "labs": {"Na": "140", "Cl": "118", "HCO3": "14", "pH": "7.38"},
                        "question_text": "What is the most likely acid-base interpretation?",
                        "explanation": "Anion gap = 140 - (118 + 14) = 8, which is normal, so this is a hyperchloremic (normal anion gap) metabolic acidosis. The near-normal pH with a low bicarbonate indicates a coexisting metabolic alkalosis, a classic pattern in vomiting (loss of H+ and chloride) plus diarrhea or diabetic ketoacidosis, or in diuretic use.",
                        "clinical_pearl": "A normal anion gap with a low bicarbonate is not a diagnosis of diarrhea until you rule out a simultaneous alkalosis (vomiting, diuretics,Contraction alkalosis).",
                        "reference_ids": ["winters-formula-1979"],
                        "lesson_slug": "anion-gap-acidosis-algorithm",
                        "choices": [
                            ("A", "Normal anion gap metabolic acidosis with a superimposed metabolic alkalosis", True, None),
                            ("B", "High anion gap metabolic acidosis", False, "Anion gap is 8, which is normal."),
                            ("C", "Isolated respiratory alkalosis", False, "PCO2 is not reported, and bicarbonate of 14 is too low for a respiratory cause."),
                            ("D", "Chronic respiratory acidosis with full renal compensation", False, "Compensation for respiratory acidosis raises bicarbonate but does not lower it to 14 by itself."),
                        ],
                    },
                ],
            },
            {
                "title": "Mixed Acid-Base Disorders",
                "slug": "mixed-acid-base-disorders",
                "description": "Delta ratio, compensation checks, and recognition of hidden second disorders.",
                "lessons": [
                    {
                        "title": "Approach to Mixed Acid-Base Disorders",
                        "lesson_slug": "approach-to-mixed-acid-base-disorders",
                        "lesson_type": "article",
                        "summary": "Delta gap and delta-delta calculations to uncover a second disorder.",
                        "content_md": "1. Confirm acidemia or alkalemia and identify the primary process.\n2. For a metabolic acidosis, calculate the anion gap and then the delta ratio: (measured HCO3 - 24) / (12 - anion gap). A ratio near 1.0 is a pure high anion gap acidosis; below 0.4 implies a coexisting normal anion gap acidosis; above 2.0 implies a coexisting metabolic alkalosis.\n3. Check respiratory compensation with Winter's formula for acidosis and with the expected PaCO2 = 0.7 x HCO3 + 20 +/- 5 (or 40 + 0.6 x change in HCO3) for metabolic alkalosis.\n4. Any deviation beyond the compensation window is a second respiratory disorder.",
                        "duration_seconds": 120,
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/acid-base-disorders/gi-causes-acid-base.html",
                        "reference_ids": ["winters-formula-1979", "kdigo-aki-2012"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 45-year-old woman with alcoholic ketoacidosis and vomiting has Na 138, Cl 96, HCO3 10, PCO2 30, pH 7.30.",
                        "labs": {"Na": "138", "Cl": "96", "HCO3": "10", "PCO2": "30", "pH": "7.30"},
                        "question_text": "Which combination of disorders is most likely present?",
                        "explanation": "Anion gap = 138 - (96 + 10) = 32 (high). Delta ratio = (10 - 24) / (12 - 32) = (-14) / (-20) = 0.7, close to 1.0, so the metabolic acidosis is predominantly a pure high anion gap acidosis rather than a mixed high plus normal gap process. Winter's formula predicts PCO2 = (1.5 x 10) + 8 +/- 2 = 23 +/- 2; the measured 30 is higher, indicating a concurrent respiratory acidosis. Vomiting adds a metabolic alkalosis but the pattern still fits high gap acidosis with a superimposed respiratory process.",
                        "clinical_pearl": "Delta ratio between 0.4 and 2.0 = single high anion gap process; outside that range assume a second metabolic disorder.",
                        "reference_ids": ["winters-formula-1979"],
                        "lesson_slug": "approach-to-mixed-acid-base-disorders",
                        "choices": [
                            ("A", "High anion gap metabolic acidosis with a concurrent respiratory acidosis", True, None),
                            ("B", "High anion gap metabolic acidosis with a concurrent respiratory alkalosis", False, "Respiratory alkalosis would give a PCO2 below the Winter's formula range."),
                            ("C", "Isolated respiratory acidosis with appropriate compensation", False, "Bicarbonate of 10 is far too low for compensation of a respiratory disorder."),
                            ("D", "Normal anion gap metabolic acidosis with metabolic alkalosis", False, "The anion gap of 32 is clearly elevated."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "An intubated patient in the ICU has pH 7.25, PCO2 58, HCO3 24, Na 140, Cl 100.",
                        "labs": {"pH": "7.25", "PCO2": "58", "HCO3": "24", "Na": "140", "Cl": "100"},
                        "question_text": "Which statement best describes this acid-base status?",
                        "explanation": "The pH is acidemic with a high PCO2 and a normal bicarbonate, which indicates an acute (uncompensated) respiratory acidosis. In acute respiratory acidosis, bicarbonate rises by about 1 mEq/L for every 10 mm Hg rise in PCO2; here PCO2 is 18 above 40, so the expected bicarbonate is roughly 26. A bicarbonate of exactly 24 with an acidemic pH implies no renal compensation yet, consistent with a very acute process.",
                        "clinical_pearl": "Acute respiratory acidosis: HCO3 rises 1 mEq/L per 10 mmHg PCO2. Chronic: 3.5-4 mEq/L per 10 mmHg.",
                        "reference_ids": ["kdigo-aki-2012", "winters-formula-1979"],
                        "lesson_slug": "approach-to-mixed-acid-base-disorders",
                        "choices": [
                            ("A", "Acute respiratory acidosis without renal compensation", True, None),
                            ("B", "Chronic respiratory acidosis with appropriate compensation", False, "Chronic compensation would raise bicarbonate by roughly 6-7 mEq/L here."),
                            ("C", "Metabolic acidosis with respiratory compensation", False, "Bicarbonate is normal, not low, and PCO2 is the abnormal value."),
                            ("D", "Respiratory alkalosis with metabolic compensation", False, "PCO2 is high and the pH is acidemic."),
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
                        "lesson_slug": "chloride-responsive-alkalosis",
                        "lesson_type": "animation",
                        "summary": "Urine chloride algorithm for metabolic alkalosis workup.",
                        "animation_url": f"{ANIMATION_BASE}/metabolic-alkalosis.json",
                        "duration_seconds": 75,
                        "image_url": f"{MEDICAL_ASSET_BASE}/acid-base-disorders/hypokalemic-metabolic-alkalosis.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/acid-base-disorders/hypokalemic-metabolic-alkalosis-thumb.webp",
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/acid-base-disorders/hypokalemic-metabolic-alkalosis-lesson.html",
                        "reference_ids": ["uptodate-metabolic-alk"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A patient on loop diuretics has pH 7.48, HCO3 32, and a urine chloride of 8 mEq/L.",
                        "labs": {"pH": "7.48", "HCO3": "32", "urine_chloride": "8"},
                        "question_text": "What is the best initial treatment?",
                        "explanation": "A urine chloride below 20 mEq/L indicates a chloride-responsive (saline-responsive) metabolic alkalosis, most often from vomiting, nasogastric suction, or remote diuretic use. Chloride and volume repletion with isotonic saline is the correct initial therapy; potassium repletion is also required because alkalosis drives renal potassium loss.",
                        "clinical_pearl": "Urine chloride < 20 mEq/L = chloride-responsive. Urine chloride > 20 mEq/L = chloride-resistant.",
                        "reference_ids": ["uptodate-metabolic-alk"],
                        "lesson_slug": "chloride-responsive-alkalosis",
                        "choices": [
                            ("A", "Intravenous normal saline", True, None),
                            ("B", "Oral potassium chloride alone", False, "Potassium alone does not correct the chloride and volume deficit driving the alkalosis."),
                            ("C", "Acetazolamide", False, "Used for chloride-resistant alkalosis such as that seen with mineralocorticoid excess."),
                            ("D", "Hydrochloric acid infusion", False, "Reserved for severe, refractory alkalosis with critical potassium or cardiac complications."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "A 42-year-old man with severe hypertension (190/105) and a potassium of 2.4 mEq/L has pH 7.50 and HCO3 36. Urine chloride is 30 mEq/L. Aldosterone to renin ratio is markedly elevated.",
                        "labs": {"pH": "7.50", "HCO3": "36", "K": "2.4", "urine_chloride": "30", "bp": "190/105"},
                        "question_text": "Which treatment is most appropriate as initial therapy?",
                        "explanation": "Hypokalemic metabolic alkalosis with a high urine chloride, severe hypertension, and an elevated aldosterone to renin ratio indicates primary hyperaldosteronism, a chloride-resistant alkalosis. Volume expansion with sodium restriction plus a mineralocorticoid receptor antagonist (spironolactone or eplerenone) is first-line; saline loading is ineffective and sodium loading worsens the hypertension.",
                        "clinical_pearl": "Chloride-resistant alkalosis plus hypertension plus a high aldosterone to renin ratio = primary hyperaldosteronism until proven otherwise.",
                        "reference_ids": ["uptodate-metabolic-alk", "kdigo-bp-2021"],
                        "lesson_slug": "chloride-responsive-alkalosis",
                        "choices": [
                            ("A", "Spironolactone with sodium restriction", True, None),
                            ("B", "Intravenous normal saline bolus", False, "Saline will not correct a mineralocorticoid-driven alkalosis and aggravates hypertension."),
                            ("C", "Oral potassium chloride alone", False, "Potassium alone does not block the aldosterone effect and the hypertension needs treatment."),
                            ("D", "Isopropyl alcohol intoxication", False, "There is no history of isopropanol exposure, and that causes an anion gap acidosis, not an alkalosis."),
                        ],
                    },
                ],
            },
            {
                "title": "Renal Tubular Acidosis",
                "slug": "renal-tubular-acidosis",
                "description": "Type 1, 2, and 4 RTA: urine pH, urine anion gap, and stone risk.",
                "lessons": [
                    {
                        "title": "Renal Tubular Acidosis Patterns",
                        "lesson_slug": "renal-tubular-acidosis-patterns",
                        "lesson_type": "article",
                        "summary": "Distal vs proximal vs type 4 RTA bedside patterns.",
                        "content_md": "All forms of RTA are hyperchloremic (normal anion gap) metabolic acidoses with preserved glomerular filtration.\n\nType 1 (distal): impaired H+ secretion in the alpha-intercalated cell. Urine pH stays above 5.3 despite systemic acidosis, urine anion gap is positive, and nephrolithiasis or nephrocalcinosis is common. Causes include Sjögren syndrome, autoimmune hepatitis, amphotericin B, analgesic nephropathy, and obstruction.\n\nType 2 (proximal): impaired bicarbonate reabsorption with intact distal acidification. Urine pH is high only while serum bicarbonate is above the reduced threshold, and it falls below 5.3 once serum bicarbonate is low. Urine anion gap is negative. Causes include multiple myeloma (Fanconi syndrome), carbonic anhydrase inhibitors, heavy metals, and tenofovir.\n\nType 4: hyporeninemic hypoaldosteronism with impaired ammonium excretion. Hyperkalemia is the dominant feature. Common in diabetic CKD, ACE inhibitor or ARB use, heparin, and adrenal insufficiency.",
                        "duration_seconds": 130,
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/acid-base-disorders/renal-tubular-acidosis-patterns.html",
                        "reference_ids": ["statpearls-rta", "ajkd-rta-core-2025"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 38-year-old woman with primary Sjögren syndrome has recurrent calcium phosphate kidney stones. ABG: pH 7.32, HCO3 16, PCO2 30. Urine pH is 6.2 measured during an active metabolic acidosis.",
                        "labs": {"pH": "7.32", "HCO3": "16", "PCO2": "30", "urine_ph": "6.2", "stones": "recurrent Ca phosphate"},
                        "question_text": "Which tubular defect is most likely?",
                        "explanation": "A urine pH that remains above 5.3 during systemic metabolic acidosis indicates failure of distal hydrogen ion secretion, i.e. distal (type 1) renal tubular acidosis. Autoimmune disease such as Sjögren syndrome is a classic cause, and the combination of distal RTA with alkaline urine produces hypocitraturia and hypercalciuria, causing calcium phosphate stones and nephrocalcinosis.",
                        "clinical_pearl": "Urine pH > 5.3 in the face of systemic acidosis = distal (type 1) RTA. Stones plus alkaline urine point to the same diagnosis.",
                        "reference_ids": ["statpearls-rta", "ajkd-rta-core-2025"],
                        "lesson_slug": "renal-tubular-acidosis-patterns",
                        "choices": [
                            ("A", "Distal (type 1) renal tubular acidosis", True, None),
                            ("B", "Proximal (type 2) renal tubular acidosis", False, "Proximal RTA acidifies urine normally once serum bicarbonate has fallen below the reduced threshold."),
                            ("C", "Type 4 renal tubular acidosis", False, "Type 4 RTA is hyperkalemic and does not produce alkaline urine or calcium phosphate stones."),
                            ("D", "Distal (type 1) RTA due to amphotericin B", False, "Amphotericin B is a valid cause of distal RTA, but this patient has no antifungal exposure; the autoimmune association is the intended diagnosis."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 61-year-old man with multiple myeloma has a normal anion gap metabolic acidosis, glycosuria despite normal serum glucose, phosphaturia, and urate wasting. Urine pH is 5.1 when serum bicarbonate is 14.",
                        "labs": {"serum_bicarb": "14", "urine_ph": "5.1", "anion_gap": "9", "serum_phosphate": "1.6"},
                        "question_text": "Which mechanism best explains the acid-base disorder?",
                        "explanation": "Proximal (type 2) RTA results from failure of bicarbonate reabsorption in the proximal tubule, and light chains in myeloma can also produce a generalized Fanconi syndrome with glycosuria, phosphaturia, urate wasting, and aminoaciduria. Because distal acidification is intact, the urine pH falls below 5.3 once serum bicarbonate has dropped to the reduced reabsorptive threshold, which is exactly what is seen here.",
                        "clinical_pearl": "Proximal RTA: urine pH is alkaline only while serum bicarbonate is still above the reduced threshold; look for Fanconi features (glycosuria, phosphaturia, urate wasting).",
                        "reference_ids": ["statpearls-rta", "ajkd-rta-core-2025"],
                        "lesson_slug": "renal-tubular-acidosis-patterns",
                        "choices": [
                            ("A", "Proximal tubular bicarbonate wasting with intact distal acidification", True, None),
                            ("B", "Distal hydrogen ion secretion failure", False, "Distal RTA keeps urine pH above 5.3 during acidosis; here urine acidifies appropriately."),
                            ("C", "Aldosterone deficiency", False, "Type 4 RTA is hyperkalemic and typically accompanies diabetic CKD rather than myeloma."),
                            ("D", "Ureteral obstruction with post-obstructive acidosis", False, "Obstruction would not produce generalized proximal tubular losses."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "A 68-year-old woman with type 2 diabetes and CKD G3b on an ACE inhibitor has a potassium of 6.1 mEq/L, HCO3 17, and an anion gap of 11. Urine potassium is 25 mEq/L and urine pH is 5.0.",
                        "labs": {"K": "6.1", "HCO3": "17", "anion_gap": "11", "urine_ph": "5.0", "urine_k": "25"},
                        "question_text": "What is the most likely mechanism of her hyperkalemic acidosis?",
                        "explanation": "Hyperkalemic (type 4) RTA from hyporeninemic hypoaldosteronism produces impaired distal potassium and hydrogen ion secretion with reduced ammonium excretion, so urine pH can remain acidic (<5.3) while serum bicarbonate is low. Diabetic CKD reduces renin release and ACE inhibitor therapy further lowers aldosterone, so the urine potassium is low relative to the serum hyperkalemia (a low urinary potassium implies impaired renal excretion rather than excess intake).",
                        "clinical_pearl": "Type 4 RTA: hyperkalemia with a low urine potassium and acid urine pH, classically in diabetic CKD, ACEi/ARB use, or hyporeninemic hypoaldosteronism.",
                        "reference_ids": ["statpearls-rta", "kdigo-ckd-2024"],
                        "lesson_slug": "renal-tubular-acidosis-patterns",
                        "choices": [
                            ("A", "Type 4 RTA from hyporeninemic hypoaldosteronism", True, None),
                            ("B", "Distal (type 1) RTA", False, "Distal RTA causes a urine pH above 5.3 and usually hypokalemia, not hyperkalemia."),
                            ("C", "Bartter syndrome", False, "Bartter causes a hypokalemic chloride-responsive metabolic alkalosis, not hyperkalemic acidosis."),
                            ("D", "Primary hyperaldosteronism", False, "Hyperaldosteronism causes hypokalemia and metabolic alkalosis."),
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
                        "lesson_slug": "emergency-hyperkalemia-algorithm",
                        "lesson_type": "animation",
                        "summary": "Fast visual algorithm: stabilize membrane, shift K+, remove K+.",
                        "animation_url": f"{ANIMATION_BASE}/hyperkalemia-algorithm.json",
                        "duration_seconds": 120,
                        "reference_ids": ["aha-hyperk-2015", "uptodate-hyperk"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 64-year-old man on hemodialysis missed dialysis and presents with weakness. ECG shows peaked T waves. Potassium is 6.9 mEq/L.",
                        "labs": {"K": "6.9", "Cr": "9.4", "BUN": "82", "HCO3": "18"},
                        "question_text": "What is the best immediate next step?",
                        "explanation": "Severe hyperkalemia with ECG changes requires immediate cardiac membrane stabilization with intravenous calcium, which acts within 1-3 minutes and does not lower the potassium. Only after membrane stabilization should potassium be shifted intracellularly with insulin plus glucose and nebulized albuterol, and then removed with dialysis or loop diuresis. Potassium binders such as sodium zirconium cyclosilicate or patiromer are too slow for initial stabilization.",
                        "clinical_pearl": "In hyperkalemia with ECG changes, give IV calcium first. Calcium protects the heart; it does not lower potassium.",
                        "reference_ids": ["aha-hyperk-2015", "uptodate-hyperk"],
                        "lesson_slug": "emergency-hyperkalemia-algorithm",
                        "choices": [
                            ("A", "Intravenous calcium gluconate", True, None),
                            ("B", "Sodium polystyrene sulfonate", False, "Too slow for emergency membrane stabilization."),
                            ("C", "Oral patiromer", False, "Too slow for life-threatening hyperkalemia with ECG changes."),
                            ("D", "Dietary potassium restriction only", False, "Inadequate for ECG changes and does not treat the acute emergency."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "A dialysis patient with no ECG changes has a potassium of 6.2 mEq/L. He is hemodynamically stable and euvolemic. Which option is the most appropriate initial potassium-lowering strategy?",
                        "labs": {"K": "6.2", "ecg": "no changes", "hemodynamics": "stable"},
                        "question_text": "Which intervention should be tried first in this stable patient?",
                        "explanation": "In a stable patient with hyperkalemia and no ECG changes, loop diuresis with adequate urine output is the preferred initial potassium-removal strategy, and insulin with glucose can be used to shift potassium while the effect of diuresis is assessed. Insulin plus glucose is appropriate only with monitoring for hypoglycemia. Dialysis is reserved for refractory hyperkalemia, and potassium binders are best used to maintain potassium control between dialysis sessions or when diuresis is not possible.",
                        "clinical_pearl": "Stable, no ECG changes, still making urine: try diuresis first. Reserve dialysis for refractory hyperkalemia.",
                        "reference_ids": ["aha-hyperk-2015", "kdoqi-hd-adequacy-2015"],
                        "lesson_slug": "emergency-hyperkalemia-algorithm",
                        "choices": [
                            ("A", "Loop diuresis with a goal of adequate urine output", True, None),
                            ("B", "Immediate hemodialysis", False, "Dialysis is highly effective but is not the first step in a stable, euvolemic patient who can make urine."),
                            ("C", "Chronic sodium polystyrene sulfonate maintenance resin", False, "Older resins are slow, cause GI side effects, and are not preferred initial therapy."),
                            ("D", "Subcutaneous insulin and glucose", False, "Insulin and glucose shift potassium but do not remove it; it is an adjunct, not the primary removal strategy."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "An end-stage renal disease patient is found to have potassium 7.1 mEq/L. The sample is grossly hemolyzed and the patient is asymptomatic with a normal ECG.",
                        "labs": {"K": "7.1", "specimen": "hemolyzed", "ecg": "normal"},
                        "question_text": "What is the most appropriate first step in management?",
                        "explanation": "A markedly elevated potassium in a hemolyzed specimen should be treated as pseudohyperkalemia until proven otherwise. The correct first step is to repeat the test with a fresh, non-hemolyzed sample while taking precautions to avoid fistula or limb contamination during collection. Empiric therapy should be considered only if the repeat specimen confirms the elevation, or if the clinical situation requires immediate treatment despite a questionable result.",
                        "clinical_pearl": "Pseudohyperkalemia: hemolysis, fistula blood draws, prolonged tourniquet time, and extreme thrombocytosis. Repeat with a fresh sample first.",
                        "reference_ids": ["uptodate-hyperk", "aha-hyperk-2015"],
                        "lesson_slug": "emergency-hyperkalemia-algorithm",
                        "choices": [
                            ("A", "Repeat the potassium with a fresh non-hemolyzed sample", True, None),
                            ("B", "Give intravenous calcium immediately", False, "Unnecessary if the elevation is spurious, and this patient has no ECG changes."),
                            ("C", "Start urgent hemodialysis", False, "Dialysis for a laboratory artifact exposes the patient to avoidable risk."),
                            ("D", "Administer insulin and glucose", False, "Treating an artifact can cause hypoglycemia and does not address the real problem."),
                        ],
                    },
                ],
            },
            {
                "title": "Hyponatremia",
                "slug": "hyponatremia",
                "description": "Acute vs chronic hyponatremia, tonicity, and osmotic demyelination risk.",
                "lessons": [
                    {
                        "title": "Hyponatremia Correction Limits",
                        "lesson_slug": "hyponatremia-correction-limits",
                        "lesson_type": "animation",
                        "summary": "Safe sodium correction rates and osmotic demyelination prevention.",
                        "animation_url": f"{ANIMATION_BASE}/hyponatremia-correction.json",
                        "duration_seconds": 100,
                        "image_url": f"{MEDICAL_ASSET_BASE}/electrolytes/hyponatremia-osmolality-approach.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/electrolytes/hyponatremia-osmolality-approach-thumb.webp",
                        "reference_ids": ["rose-hyponatremia-2013"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 68-year-old with thiazide use and a serum sodium of 118 mEq/L for more than 48 hours has no seizures and is neurologically intact. Correction has been running at about 11 mEq/L in the first 12 hours.",
                        "labs": {"na": "118 mEq/L", "duration": "> 48 h", "correction_so_far": "11 mEq/L in 12 h"},
                        "question_text": "What is the maximum recommended sodium correction in the first 24 hours for this patient with chronic hyponatremia?",
                        "explanation": "In chronic hyponatremia of more than 48 hours duration, over-correction accelerates water loss from oligodendrocytes and precipitates osmotic demyelination syndrome. Experts recommend limiting the rise in sodium to about 8 mEq/L in 24 hours and 18 mEq/L over 48 hours, and certainly avoiding any rise above 8 mEq/L over 24 hours in patients at high risk.",
                        "clinical_pearl": "Correct chronic hyponatremia slowly: no more than 8 mEq/L in 24 hours and 18 mEq/L in 48 hours.",
                        "reference_ids": ["rose-hyponatremia-2013"],
                        "lesson_slug": "hyponatremia-correction-limits",
                        "choices": [
                            ("A", "4 mEq/L", False, "Safe but not the maximum recommended correction."),
                            ("B", "8 mEq/L", True, None),
                            ("C", "15 mEq/L", False, "Exceeds the safe correction rate and risks osmotic demyelination."),
                            ("D", "20 mEq/L", False, "Dangerously fast correction with a high risk of osmotic demyelination syndrome."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "A 72-year-old man on thiazide diuretics and an SSRI presents with confusion. Sodium is 122 mEq/L, serum osmolality 254, and urine osmolality 480. He is euvolemic on exam.",
                        "labs": {"Na": "122", "serum_osm": "254", "urine_osm": "480", "tsh": "2.1"},
                        "question_text": "Which of the following is the most likely mechanism of this hyponatremia?",
                        "explanation": "This is hypotonic (true) hyponatremia with inappropriately concentrated urine (urine osmolality 480 despite low plasma osmolality) in a euvolemic patient, which indicates SIADH. Thiazide diuretics and SSRIs are both classic triggers of SIADH. Hypothyroid and adrenal insufficiency should be excluded, but the normal thyroid-stimulating hormone and euvolemic examination support SIADH. Volume repletion with isotonic saline is the initial therapy.",
                        "clinical_pearl": "Hypotonic hyponatremia with urine osmolality above 100 mOsm/kg and euvolemia = SIADH until proven otherwise. Thiazides and SSRIs are the most common drug triggers.",
                        "reference_ids": ["rose-hyponatremia-2013"],
                        "lesson_slug": "hyponatremia-correction-limits",
                        "choices": [
                            ("A", "Syndrome of inappropriate antidiuretic hormone secretion induced by thiazide diuretic and SSRI therapy", True, None),
                            ("B", "Reset osmostat from chronic alcoholism", False, "A reset osmostat is a chronic, stable, and largely asymptomatic condition without inappropriately low serum sodium at normal water intake."),
                            ("C", "Primary polydipsia", False, "Primary polydipsia produces maximally dilute urine, not a urine osmolality of 480."),
                            ("D", "Hypertonic translocational hyponatremia from hyperglycemia", False, "Serum osmolality is low at 254, and glucose-driven translocational hyponatremia raises serum osmolality."),
                        ],
                    },
                ],
            },
            {
                "title": "Hypocalcemia and Hypomagnesemia",
                "slug": "hypocalcemia-hypomagnesemia",
                "description": "Calcium and magnesium disorders in CKD and the critically ill patient.",
                "lessons": [
                    {
                        "title": "Calcium and Magnesium Disorders",
                        "lesson_slug": "calcium-and-magnesium-disorders",
                        "lesson_type": "article",
                        "summary": "PTH-dependent vs PTH-independent hypocalcemia and magnesium as a cause of refractory hypokalemia.",
                        "content_md": "Hypocalcemia is divided by the PTH response.\n\nPTH-dependent (PTH is high or inappropriately normal): vitamin D deficiency, CKD (impaired 1-alpha hydroxylation and hyperphosphatemia), hypomagnesemia, and hungry bone syndrome after parathyroidectomy.\n\nPTH-independent (PTH is suppressed): hypocalcemia of malignancy (PTH-related peptide or osteolytic metastases), vitamin D excess, calcium chelation, and acute pancreatitis.\n\nCorrected calcium or ionized calcium should be used, and magnesium must be repleted: hypomagnesemia causes renal potassium wasting and PTH resistance, so severe hypokalemia or hypocalcemia will not correct until magnesium is repleted.",
                        "duration_seconds": 90,
                        "reference_ids": ["kdigo-ckd-2024", "kdigo-ckd-mbd-2017"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A patient with CKD G5 on hemodialysis has a calcium of 7.1 mg/dL, phosphate 6.4 mg/dL, and an intact PTH of 780 pg/mL. He has muscle cramps and paresthesias.",
                        "labs": {"Ca": "7.1", "phosphate": "6.4", "PTH": "780", "albumin": "3.0"},
                        "question_text": "What is the most appropriate management of the hypocalcemia?",
                        "explanation": "In advanced CKD, hyperphosphatemia binds calcium and reduced calcitriol synthesis limits intestinal calcium absorption, producing secondary hyperparathyroidism with hypocalcemia. Management combines phosphate reduction with phosphate binders and dietary counseling, active vitamin D analogues for the elevated PTH, and oral calcium carbonate when needed to lower the calcium-phosphate load. Intravenous calcium is reserved for symptomatic or severe hypocalcemia such as tetany or arrhythmia.",
                        "clinical_pearl": "CKD hypocalcemia is a phosphate and vitamin D problem: lower phosphate first, then use active vitamin D; reserve IV calcium for symptoms.",
                        "reference_ids": ["kdigo-ckd-mbd-2017", "kdigo-ckd-2024"],
                        "lesson_slug": "calcium-and-magnesium-disorders",
                        "choices": [
                            ("A", "Phosphate reduction with binders plus an active vitamin D analogue, adding oral calcium as needed", True, None),
                            ("B", "Immediate parathyroidectomy", False, "Parathyroidectomy is reserved for severe, refractory hyperparathyroidism, not for the hypocalcemia of secondary hyperparathyroidism."),
                            ("C", "High-dose intravenous calcium infusion alone", False, "IV calcium alone corrects the number transiently but ignores the driving hyperphosphatemia and secondary hyperparathyroidism."),
                            ("D", "Stop all phosphate binders and increase dietary protein", False, "Increasing dietary phosphate would worsen hyperphosphatemia and hypocalcemia."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 55-year-old alcoholic with persistent diarrhea has a potassium of 2.6 mEq/L. After 3 days of aggressive potassium replacement, the serum potassium remains 2.4 mEq/L. Magnesium is 0.9 mg/dL.",
                        "labs": {"K": "2.6", "Mg": "0.9"},
                        "question_text": "What is the most likely explanation for the refractory hypokalemia?",
                        "explanation": "Intracellular magnesium is required for renal potassium retention: magnesium depletion increases ROMK-mediated renal potassium secretion, producing refractory renal potassium wasting. Hypomagnesemia also causes resistance to parathyroid hormone, which can worsen hypocalcemia. Refractory hypokalemia, especially with diarrhea or alcoholism, should prompt magnesium repletion before further potassium replacement can succeed.",
                        "clinical_pearl": "Replete magnesium before chasing refractory hypokalemia; magnesium depletion causes renal potassium wasting and PTH resistance.",
                        "reference_ids": ["kdigo-ckd-2024", "kdigo-aki-2012"],
                        "lesson_slug": "calcium-and-magnesium-disorders",
                        "choices": [
                            ("A", "Magnesium depletion causing renal potassium wasting", True, None),
                            ("B", "Secretion of a mineralocorticoid-secreting tumor", False, "A mineralocorticoid excess would cause hypertension and metabolic alkalosis, neither of which is present here."),
                            ("C", "Vomiting-induced metabolic alkalosis", False, "Alkalosis does not explain persistent hypokalemia despite replacement in this setting."),
                            ("D", "Bartter syndrome", False, "Bartter is a renal salt-wasting tubulopathy with early onset and is far less likely in this context of alcoholism and diarrhea."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Acute Kidney Injury & ICU",
        "slug": "acute-kidney-injury-icu",
        "order_index": 3,
        "description": "Prerenal, intrinsic, and postrenal AKI, RRT initiation, and CRRT in the critically ill patient.",
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
                        "lesson_slug": "fena-vs-feurea-in-aki",
                        "lesson_type": "animation",
                        "summary": "When to use fractional excretion of sodium versus fractional excretion of urea.",
                        "animation_url": f"{ANIMATION_BASE}/fena-feuera.json",
                        "duration_seconds": 85,
                        "reference_ids": ["kdigo-aki-2012"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "easy",
                        "case_text": "A 70-year-old man with congestive heart failure on furosemide develops worsening creatinine after being over-diuresed in clinic.",
                        "labs": {"Cr": "2.4", "baseline_cr": "1.1", "BUN": "38"},
                        "question_text": "Which finding is most consistent with prerenal AKI in this patient?",
                        "explanation": "In prerenal physiology the kidney avidly reabsorbs sodium, so the fractional excretion of sodium is below 1% and the fractional excretion of urea is below 35%. However, this patient is taking a loop diuretic, which increases urinary sodium excretion and makes the fractional excretion of sodium unreliable, so the fractional excretion of urea (which is not affected by diuretics) is the preferred index. A BUN to creatinine ratio above 20:1 supports a prerenal cause.",
                        "clinical_pearl": "On loop diuretics, use FEUrea (<35%) rather than FENa (<1%) to assess prerenal physiology.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "fena-vs-feurea-in-aki",
                        "choices": [
                            ("A", "Fractional excretion of urea below 35% with a BUN to creatinine ratio above 20:1", True, None),
                            ("B", "Fractional excretion of sodium above 3% with muddy brown casts", False, "That pattern indicates intrinsic tubular injury, and FENa is also unreliable on loop diuretics."),
                            ("C", "Urine sodium above 40 mEq/L", False, "A high urine sodium suggests intrinsic renal failure or diuretic effect rather than avid sodium reabsorption."),
                            ("D", "BUN to creatinine ratio below 10:1", False, "A low BUN to creatinine ratio points to intrinsic renal disease."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A patient with cirrhosis and ascites develops rising creatinine. Urine sodium is 4 mEq/L and fractional excretion of sodium is 0.4%, but urine sediment shows bland hyaline casts only. After albumin challenge, creatinine improves.",
                        "labs": {"urine_sodium": "4", "fena": "0.4", "sediment": "hyaline casts"},
                        "question_text": "Which diagnosis is most likely?",
                        "explanation": "Cirrhosis with ascites, very low urinary sodium, and a bland sediment describes a functional (prerenal) state. This pattern is consistent with hepatorenal syndrome, in which splanchnic vasodilation causes profound renal vasoconstriction and a functional fall in GFR. The response to albumin challenge and improvement in creatinine support functional rather than structural renal injury.",
                        "clinical_pearl": "Hepatorenal syndrome = low urine sodium, bland sediment, and improvement with volume expansion; treat with albumin plus vasoconstrictor therapy.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "fena-vs-feurea-in-aki",
                        "choices": [
                            ("A", "Hepatorenal syndrome physiology (functional prerenal AKI)", True, None),
                            ("B", "Acute tubular necrosis", False, "ATN would show granular muddy brown casts and a higher fractional excretion of sodium."),
                            ("C", "Acute interstitial nephritis", False, "Acute interstitial nephritis shows white cell casts, eosinophilia, and drug exposure."),
                            ("D", "Acute cortical necrosis", False, "Cortical necrosis occurs in obstetric catastrophes or severe shock and does not improve with albumin."),
                        ],
                    },
                ],
            },
            {
                "title": "Intrinsic AKI",
                "slug": "intrinsic-aki",
                "description": "Acute tubular necrosis, acute interstitial nephritis, and vascular injury.",
                "lessons": [
                    {
                        "title": "Intrinsic AKI: Sediment and Timing",
                        "lesson_slug": "intrinsic-aki-sediment-and-timing",
                        "lesson_type": "article",
                        "summary": "Using urine sediment, timing, and exposures to narrow intrinsic AKI.",
                        "content_md": "Intrinsic AKI is divided by the dominant lesion.\n\nAcute tubular necrosis: the most common cause, typically ischemic or nephrotoxic. Sediment shows muddy brown granular casts and renal tubular epithelial cells. A nadir of creatinine at 3-7 days with recovery over 1-3 weeks is typical.\n\nAcute interstitial nephritis: drug, infection, or systemic cause; classic triad of fever, rash, and eosinophilia is uncommon. Sterile pyuria, white cell casts, and mild proteinuria are typical. Kidney function often fails to improve after the drug is stopped, and corticosteroids are recommended when recovery is incomplete.\n\nAcute cortical necrosis: obstetric emergencies, severe shock, or profound hypotension, with anuria and a bland sediment.\n\nVascular: renal vein thrombosis, thrombotic microangiopathy, or cholesterol emboli after vascular manipulation.",
                        "duration_seconds": 100,
                        "image_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/urinary-casts-morphology.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/urinary-casts-morphology-thumb.webp",
                        "reference_ids": ["kdigo-aki-2012"],
                    },
                    {
                        "title": "Urinary Casts Morphology and Localization",
                        "lesson_slug": "urinary-casts-morphology-and-localization",
                        "lesson_type": "article",
                        "summary": "How casts form in the tubule and what each type localizes.",
                        "content_md": "Casts are formed inside the tubule from uromodulin (Tamm-Horsfall protein) secreted by tubular cells, so a cast always localizes the disease to that nephron segment.\n\nHyaline casts: most numerous, low refractive index, seen in concentrated urine, exercise, and volume depletion. Not diagnostic.\n\nGranular casts (muddy brown): breakdown of cellular debris in acute tubular necrosis.\n\nRed cell casts: glomerular bleeding, essentially always glomerulonephritis or vasculitis. Their presence is a board favorite because they separate nephritic from nephrotic disease.\n\nWhite cell casts and white cell casts with eosinophils: pyelonephritis and acute interstitial nephritis.\n\nWaxy casts: broad, homogeneous, cracked casts indicating chronic advanced kidney disease with dilated tubules. Fatty casts and oval fat bodies (Maltese cross under polarized light) indicate heavy proteinuria.",
                        "duration_seconds": 90,
                        "image_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/urinary-casts-morphology.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/urinary-casts-morphology-thumb.webp",
                        "reference_ids": ["kdigo-aki-2012", "abim-nephrology-blueprint-2026"],
                    },
                    {
                        "title": "Renal Papillary Necrosis",
                        "lesson_slug": "renal-papillary-necrosis",
                        "lesson_type": "article",
                        "summary": "Causes, classic imaging signs, and the differential for sloughed papillae.",
                        "content_md": "Papillary necrosis is ischemic coagulative necrosis of the renal medullary papillae, which have the lowest blood supply in the kidney.\n\nCauses: diabetes mellitus (the most common), analgesic nephropathy (phenacetin, NSAIDs), sickle cell disease, pyelonephritis, obstruction, severe hypotension, and transplant rejection.\n\nImaging: on IV urography the classic sign is the ring shadow, moth-eaten calyx, or ball-on-tee deformity. CT urography is more sensitive and shows a contrast-filled cleft at the papilla.\n\nClinical: sloughed papillae may pass per urethra, causing acute flank pain and hematuria, or obstruct and produce postrenal acute kidney injury. Papillary necrosis also raises the risk of renal papillary adenoma and transitional cell carcinoma in analgesic nephropathy.\n\nAlways ask about diabetes, analgesic dose and duration, and sickle trait in a patient with sterile pyuria and flank pain.",
                        "duration_seconds": 90,
                        "image_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/renal-papillary-necrosis.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/acute-kidney-injury-icu/renal-papillary-necrosis-thumb.webp",
                        "reference_ids": ["kdigo-aki-2012", "abim-nephrology-blueprint-2026"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 58-year-old man taking trimethoprim-sulfamethoxazole for 3 weeks develops a rise in creatinine from 1.0 to 2.8 mg/dL. Urinalysis shows 25 white cells per high power field, white cell casts, 1+ protein, and 2% eosinophils.",
                        "labs": {"Cr": "2.8", "eosinophils": "2%", "urine_wbc": "25/hpf", "protein": "1+"},
                        "question_text": "What is the most appropriate management of this drug-induced acute kidney injury?",
                        "explanation": "The combination of a drug exposure, sterile pyuria, white cell casts, mild proteinuria, and eosinophiluria after 1-3 weeks of therapy is classic for drug-induced acute interstitial nephritis. The cornerstone of management is immediate discontinuation of the culprit drug. If kidney function does not start to recover within 3-5 days after drug withdrawal, or if there is severe AKI, corticosteroids should be started, since early steroids are associated with better renal recovery.",
                        "clinical_pearl": "Stop the drug first. Add corticosteroids when kidney function does not recover within 3-5 days or the AKI is severe.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "intrinsic-aki-sediment-and-timing",
                        "choices": [
                            ("A", "Discontinue the drug and start corticosteroids given the severity of AKI", True, None),
                            ("B", "Continue the drug and observe for 2 weeks", False, "Continuing the offending drug perpetuates the injury and worsens outcomes."),
                            ("C", "Perform a renal biopsy as the first step", False, "Biopsy is unnecessary when the clinical picture is diagnostic of drug-induced interstitial nephritis."),
                            ("D", "Start plasmapheresis", False, "Plasmapheresis has no role in drug-induced interstitial nephritis."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 45-year-old man undergoing elective vascular surgery has a creatinine nadir at day 4 after exposure to an aminoglycoside and a contrast study, then gradual recovery over 2 weeks.",
                        "labs": {"nadir_day": "4", "egfr_frac": "22", "bicarb": "17", "urine_sediment": "muddy brown casts"},
                        "question_text": "Which diagnosis and course are most consistent with these findings?",
                        "explanation": "Ischemic and nephrotoxic injury to the tubule produces acute tubular necrosis. The characteristic course is a rise in creatinine that nadir at 3-7 days after the insult, followed by recovery over 1-3 weeks once the injurious exposure is removed. Urine sediment with muddy brown granular casts and tubular epithelial cell casts supports tubular injury.",
                        "clinical_pearl": "ATN: nadir of creatinine at 3-7 days, recovery over 1-3 weeks, muddy brown granular casts.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "intrinsic-aki-sediment-and-timing",
                        "choices": [
                            ("A", "Acute tubular necrosis with recovery over 1 to 3 weeks", True, None),
                            ("B", "Acute cortical necrosis with permanent anuria", False, "Cortical necrosis is anuric and does not show a recovery phase."),
                            ("C", "Acute interstitial nephritis", False, "Interstitial nephritis produces white cell casts and an eosinophil-rich sediment, not muddy brown casts."),
                            ("D", "Postrenal obstruction", False, "Obstruction does not produce a delayed nadir and recovery pattern and would be relieved by decompression."),
                        ],
                    },
                ],
            },
            {
                "title": "Indications for Renal Replacement Therapy",
                "slug": "dialysis-indications-aki",
                "description": "AEIOU indications and timing of RRT in AKI.",
                "lessons": [
                    {
                        "title": "AEIOU Dialysis Indications",
                        "lesson_slug": "aeiou-dialysis-indications",
                        "lesson_type": "animation",
                        "summary": "Acidosis, Electrolytes, Intoxication, Overload, Uremia.",
                        "animation_url": f"{ANIMATION_BASE}/aeiou-dialysis.json",
                        "duration_seconds": 60,
                        "reference_ids": ["kdigo-aki-2012"],
                    }
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 64-year-old with septic shock and AKI on vasopressors has a potassium of 7.1 mEq/L despite a dextrose-insulin infusion and calcium gluconate, with peaked T waves and a widened QRS. Creatinine is 5.4 mg/dL and urine output is 15 mL/hr.",
                        "labs": {"k": "7.1 mEq/L", "ecg": "peaked T waves, wide QRS", "cr": "5.4 mg/dL", "uo": "15 mL/hr"},
                        "question_text": "Which of the following is an absolute indication for urgent renal replacement therapy in this patient with AKI?",
                        "explanation": "Refractory hyperkalemia with ECG changes is an emergency indication for RRT. Severe refractory acidosis, refractory volume overload with pulmonary edema, uremic complications such as pericarditis or encephalopathy, and removal of dialyzable toxins are the other standard indications. Creatinine or urea nitrogen values alone, without symptoms, are not indications for RRT.",
                        "clinical_pearl": "AEIOU: Acidosis, Electrolytes (potassium), Intoxication, Overload, Uremia. Use AEIOU plus refractory fluid overload, not a creatinine threshold.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "aeiou-dialysis-indications",
                        "choices": [
                            ("A", "BUN 80 mg/dL without symptoms", False, "Urea nitrogen alone is not an indication for RRT."),
                            ("B", "Refractory hyperkalemia with ECG changes", True, None),
                            ("C", "Creatinine 4.0 mg/dL", False, "Creatinine alone is not an indication; the clinical context determines the need."),
                            ("D", "Mild metabolic acidosis with pH 7.30", False, "Mild, non-refractory acidosis is managed medically."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A patient with septic shock and AKI on mechanical ventilation requires a vasopressor. Urine output is 0.4 mL/kg/hr for 8 hours and creatinine is rising. The team asks whether to start continuous kidney replacement therapy now.",
                        "labs": {"urine_output": "0.4 mL/kg/hr", "creatinine": "rising", "pressors": "norepinephrine"},
                        "question_text": "Which rationale best supports starting kidney replacement therapy at this time?",
                        "explanation": "The best argument for initiating RRT here is that the patient is in a dangerous biochemical and hemodynamic situation: refractory oliguria with a rising creatinine on vasopressors, with high risk of metabolic complications and fluid overload. Evidence from randomized trials shows no survival benefit to early versus selective RRT, so initiation should be driven by the severity and trajectory of illness rather than a creatinine or urea threshold, with continued reassessment once started.",
                        "clinical_pearl": "Start RRT for refractory metabolic, volume, or hemodynamic indications in a trajectory of worsening AKI, not for a creatinine value alone.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "aeiou-dialysis-indications",
                        "choices": [
                            ("A", "The patient has refractory oliguria with a rising creatinine and is on vasopressors, indicating a high risk of complications if untreated", True, None),
                            ("B", "The creatinine exceeds 3 mg/dL, which mandates RRT", False, "No creatinine or urea threshold mandates RRT, and trials showed no benefit to starting early based on laboratory values."),
                            ("C", "Starting RRT guarantees recovery of kidney function", False, "RRT does not guarantee recovery and may cause harm if started for the wrong indication."),
                            ("D", "RRT should be delayed until anuria develops", False, "Waiting for anuria risks fluid overload and metabolic complications."),
                        ],
                    },
                ],
            },
            {
                "title": "CRRT",
                "slug": "crrt",
                "description": "Modality choice, dose, circuit pressures, and monitoring in CRRT.",
                "lessons": [
                    {
                        "title": "CRRT Modality Selection",
                        "lesson_slug": "crrt-modality-selection",
                        "lesson_type": "animation",
                        "summary": "Choosing CVVH, CVVHD, or CVVHDF in the critically ill patient.",
                        "animation_url": f"{ANIMATION_BASE}/crrt-modality.json",
                        "duration_seconds": 95,
                        "reference_ids": ["kdigo-aki-2012"],
                    },
                    {
                        "title": "CRRT Dose and Effluent Targets",
                        "lesson_slug": "crrt-dose-and-effluent-targets",
                        "lesson_type": "animation",
                        "summary": "Effluent dose, filtration fraction, and net fluid balance targets.",
                        "animation_url": f"{ANIMATION_BASE}/crrt-dose-effluent.json",
                        "duration_seconds": 100,
                        "reference_ids": ["kdigo-aki-2012"],
                    },
                    {
                        "title": "CRRT Circuit Pressures",
                        "lesson_slug": "crrt-circuit-pressures",
                        "lesson_type": "animation",
                        "summary": "Interpreting access and return pressures to find clotting or access problems.",
                        "animation_url": f"{ANIMATION_BASE}/crrt-circuit-pressures.json",
                        "duration_seconds": 90,
                        "reference_ids": ["kdigo-aki-2012"],
                    },
                    {
                        "title": "CRRT Monitoring",
                        "lesson_slug": "crrt-monitoring",
                        "lesson_type": "animation",
                        "summary": "Anticoagulation, electrolyte trends, and nutrition during CRRT.",
                        "animation_url": f"{ANIMATION_BASE}/crrt-monitoring.json",
                        "duration_seconds": 90,
                        "reference_ids": ["kdigo-aki-2012"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A patient with septic shock and anuria is started on continuous venovenous hemofiltration for hemodynamic stability. Effluent is 2100 mL/hr in a 100 kg patient and filtration fraction is 15%.",
                        "labs": {"effluent": "2100 mL/hr", "weight": "100 kg", "ff": "15%", "post_dilution": "yes"},
                        "question_text": "Which statement about the prescription is correct?",
                        "explanation": "The delivered dose is effluent divided by body weight: 2100 mL/hr / 100 kg = 21 mL/kg/hr, which is an appropriate target for most critically ill patients. The filtration fraction of 15% is below the recommended 20% ceiling, reducing the risk of membrane clotting with post-dilution hemofiltration. Potassium and bicarbonate are typically low with CRRT, so potassium and acid-base status need frequent monitoring and replacement.",
                        "clinical_pearl": "CRRT dose = effluent (mL/hr) divided by patient weight; keep filtration fraction at or below 20%.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "crrt-dose-and-effluent-targets",
                        "choices": [
                            ("A", "Delivered dose is 21 mL/kg/hr and the filtration fraction is within the recommended target", True, None),
                            ("B", "Delivered dose is 2100 mL/kg/hr and the filtration fraction is dangerously high", False, "The dose is effluent divided by weight, and a filtration fraction of 15% is below the 20% ceiling."),
                            ("C", "The prescription is under-dosed and potassium supplementation is never needed", False, "21 mL/kg/hr is appropriate, and CRRT typically requires potassium replacement."),
                            ("D", "CRRT is contraindicated in hemodynamic instability", False, "CRRT is preferred in hemodynamic instability precisely because of its gentle solute and fluid removal."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "Sixteen hours into continuous kidney replacement therapy, access pressure is -180 mm Hg and return pressure is 250 mm Hg, with a 40% reduction in effluent delivery and visible clotting in the circuit.",
                        "labs": {"access_pressure": "-180 mmHg", "return_pressure": "250 mmHg", "effluent_drop": "40%"},
                        "question_text": "What is the most appropriate next step for this clotted CRRT circuit?",
                        "explanation": "A markedly negative access pressure with a high return pressure and falling effluent indicates circuit clotting, usually from a high filtration fraction, prolonged circuit life, or inadequate anticoagulation. The first step is to assess circuit and line position for kinking, recirculation, or compression, then correct the prescription (reduce filtration fraction, increase blood flow, or change dilution) and anticoagulation strategy, and replace the circuit when clotting is confirmed.",
                        "clinical_pearl": "Rising access negativity with a high return pressure and falling effluent = circuit clotting. Check lines first, then lower the filtration fraction and consider circuit change.",
                        "reference_ids": ["kdigo-aki-2012"],
                        "lesson_slug": "crrt-circuit-pressures",
                        "choices": [
                            ("A", "Check for line kinking and recirculation, reduce the filtration fraction, and replace the clotted circuit", True, None),
                            ("B", "Increase the blood flow to the maximum and wait for the circuit to clear", False, "Increasing blood flow alone will not correct a clotted circuit and can worsen hemoconcentration."),
                            ("C", "Stop CRRT and start intermittent hemodialysis immediately", False, "Circuit problems are usually managed by correcting access and prescription issues before changing modality."),
                            ("D", "Administer a large fluid bolus to dilute the blood", False, "The problem is mechanical clotting, not hypovolemia, and a fluid bolus risks volume overload."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Chronic Kidney Disease",
        "slug": "chronic-kidney-disease",
        "order_index": 4,
        "description": "CKD definition, eGFR and albuminuria staging, the KDIGO risk grid, CKD-mineral bone disorder, and anemia of CKD.",
        "icon": "ClockIcon",
        "category_slug": "chronic-kidney-disease",
        "topics": [
            {
                "title": "CKD Staging and Progression",
                "slug": "ckd-staging-progression",
                "description": "Defining and staging CKD, and interventions that slow progression.",
                "lessons": [
                    {
                        "title": "CKD Staging, eGFR, and Albuminuria",
                        "lesson_slug": "ckd-staging-egfr-and-albuminuria",
                        "lesson_type": "article",
                        "summary": "Definition of CKD, eGFR categories G1-G5, albuminuria categories A1-A3, and the KDIGO heat map.",
                        "content_md": (
                            "# CKD staging\n\n"
                            "CKD is defined as abnormalities of kidney structure or function present for "
                            "more than 3 months with implications for health, evidenced by a reduced eGFR "
                            "below 60 mL/min/1.73 m2, markers of kidney damage such as albuminuria, or "
                            "abnormal imaging or histology.\n\n"
                            "## eGFR categories\n"
                            "- G1: >= 90\n- G2: 60-89\n- G3a: 45-59\n- G3b: 30-44\n- G4: 15-29\n- G5: < 15\n\n"
                            "## Albuminuria categories (spot UACR)\n"
                            "- A1: < 30 mg/g\n- A2: 30-300 mg/g\n- A3: > 300 mg/g\n\n"
                            "## Risk grid\n"
                            "Green = low risk (G1-G2, A1-A2); yellow = moderately increased risk (G1-G2 with A3, "
                            "G3a with A1-A2, G3b with A1); orange = high risk (G3a A3, G3b A2-A3, all G4, all G5); "
                            "red = very high risk (G5 with A3 and G4-G5 with A3 plus another risk marker).\n\n"
                            "Risk is driven by both eGFR and albuminuria: a patient with G4 and A1 is still high risk, "
                            "while G3a with A2 requires close follow-up."
                        ),
                        "duration_seconds": 180,
                        "reference_ids": ["kdigo-ckd-2024"],
                    },
                    {
                        "title": "CKD Progression and Risk Reduction",
                        "lesson_slug": "ckd-progression-and-risk-reduction",
                        "lesson_type": "article",
                        "summary": "Modifiable progression risk factors and the evidence-based slowing strategies.",
                        "content_md": (
                            "# Slowing CKD progression\n\n"
                            "## Non-modifiable risk factors\n"
                            "Age, sex, race/genetics, family history, and the cause of CKD.\n\n"
                            "## Modifiable risk factors\n"
                            "Albuminuria, hypertension, hyperglycemia, smoking, high sodium and phosphate intake, "
                            "obesity, hyperuricemia, and nephrotoxin exposure.\n\n"
                            "## Evidence-based interventions\n"
                            "- ACE inhibitor or ARB for albuminuric CKD, with potassium and creatinine monitoring\n"
                            "- SGLT2 inhibitors for CKD with or without diabetes when eGFR permits\n"
                            "- Finerenone (nonsteroidal mineralocorticoid receptor antagonist) in selected CKD-T2D patients\n"
                            "- Statins for cardiovascular risk reduction\n"
                            "- Glycemic control without hypoglycemia or excess weight gain\n"
                            "- Avoidance of NSAIDs, contrast when avoidable, and other nephrotoxins\n\n"
                            "A modest creatinine rise (up to about 30%) after starting an ACEi or ARB is expected and "
                            "should not prompt discontinuation unless potassium rises or creatinine rises further."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["kdigo-ckd-2024", "awdishu-kdigo-ckd-pharm-2025"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 62-year-old with type 2 diabetes and hypertension has persistent UACR 320 mg/g over two visits. Creatinine 1.9 mg/dL, no acute illness.",
                        "labs": {"creatinine": "1.9 mg/dL", "uacr": "320 mg/g", "bp": "138/80", "egfr": "38 mL/min/1.73m2"},
                        "question_text": "How is this patient's CKD classified, and what is the most appropriate first-line renoprotective therapy?",
                        "explanation": "eGFR 38 mL/min/1.73 m2 is G3b and UACR 320 mg/g is A3, so this is G3b A3 CKD, which sits in the high-risk (orange) zone of the KDIGO heat map. With albuminuric CKD, an ACE inhibitor or ARB is first-line to reduce intraglomerular pressure and albuminuria, with potassium and creatinine checked 1-2 weeks after starting or titrating. An SGLT2 inhibitor should be added for further progression and cardiovascular benefit.",
                        "clinical_pearl": "A3 albuminuria plus eGFR below 45 is high risk on the KDIGO heat map even when GFR decline is slow; start ACEi/ARB and an SGLT2 inhibitor.",
                        "reference_ids": ["kdigo-ckd-2024", "awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "ckd-staging-egfr-and-albuminuria",
                        "choices": [
                            ("A", "G3b A3, and an ACE inhibitor or ARB should be started with a plan to add an SGLT2 inhibitor", True, None),
                            ("B", "G2 A1, and only lifestyle modification is needed", False, "eGFR 38 is G3b and UACR 320 mg/g is A3, not A1."),
                            ("C", "G5 A3, and dialysis should be planned immediately", False, "An eGFR of 38 is far above the G5 threshold for dialysis initiation."),
                            ("D", "G4 A3, and an ARB plus a calcium channel blocker is contraindicated", False, "eGFR 38 is G3b, not G4, and RAAS blockade is indicated rather than contraindicated."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "An 81-year-old with a single atrophic kidney and chronic ischemic nephropathy has a stable eGFR of 24 mL/min/1.73 m2. Two of three spot UACR values are below 30 mg/g.",
                        "labs": {"egfr": "24 mL/min/1.73m2", "uacr": "12 and 20 mg/g", "cr": "2.6 mg/dL"},
                        "question_text": "Which statement best describes this patient's risk and appropriate management?",
                        "explanation": "An eGFR of 24 places the patient in G4, and the KDIGO heat map classifies any G4 regardless of albuminuria as high risk, even with A1 albuminuria. A G4 eGFR also meets the KDIGO criterion for referral to a nephrologist and falls in the range where dialysis planning discussions should begin, and SGLT2 inhibitor therapy applies where eGFR allows. Absence of albuminuria does not reassure here, because structural and functional kidney loss alone confers high risk.",
                        "clinical_pearl": "Albuminuria is not required for high risk: every G4 patient is high risk on the heat map and needs nephrology referral.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "ckd-staging-egfr-and-albuminuria",
                        "choices": [
                            ("A", "Low risk because there is no albuminuria, so no renal protective therapy is needed", False, "All G4 patients fall in the high-risk zone of the heat map regardless of A1 albuminuria."),
                            ("B", "Moderate risk, so monitor every 6 months without drug therapy", False, "G4 is high risk and demands nephrology referral, SGLT2 inhibitor therapy where appropriate, and early dialysis planning discussion."),
                            ("C", "High risk, warranting nephrology referral, SGLT2 inhibitor therapy where eGFR allows, and early discussion of kidney replacement options", True, None),
                            ("D", "Very high risk, which only occurs at eGFR below 15 mL/min/1.73 m2", False, "The red very-high-risk zone requires G5 with A3 or G4-G5 with additional risk markers; G4 A1 is orange, high risk."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 55-year-old with diabetic CKD G3a, UACR 450 mg/g, and BP 152/94 on amlodipine 5 mg daily, is euvolemic.",
                        "labs": {"egfr": "52 mL/min/1.73m2", "uacr": "450 mg/g", "bp": "152/94", "k": "4.3 mEq/L"},
                        "question_text": "Which change has the strongest evidence for slowing this patient's kidney disease progression?",
                        "explanation": "SGLT2 inhibitors reduce intraglomerular pressure through tubuloglomerular feedback, lower albuminuria, and slow eGFR decline in diabetic and non-diabetic CKD, with benefit independent of glycemic lowering. The patient's BP is also above goal, so RAAS blockade should be added: an ACE inhibitor or ARB reduces albuminuria and progression in albuminuric CKD. The blood pressure elevation itself must be treated to goal, but among disease-modifying agents, SGLT2 inhibitors plus RAAS blockade provide the strongest evidence.",
                        "clinical_pearl": "SGLT2 inhibitors are renoprotective in albuminuric CKD whether or not the patient has diabetes; combine with ACEi/ARB when tolerated.",
                        "reference_ids": ["kdigo-ckd-2024", "awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "ckd-progression-and-risk-reduction",
                        "choices": [
                            ("A", "Switch amlodipine to a beta blocker", False, "Beta blockers are not first-line for albuminuric CKD progression; RAAS blockade and SGLT2 inhibition are."),
                            ("B", "Add an SGLT2 inhibitor and start an ACE inhibitor or ARB with potassium and creatinine monitoring", True, None),
                            ("C", "Add a beta blocker and a thiazide diuretic only", False, "Thiazides work at low GFR but do not provide the antiproteinuric benefit of RAAS blockade or SGLT2 inhibitors."),
                            ("D", "Restrict protein to 0.6 g/kg/day", False, "KDIGO recommends avoiding high protein intake but not restricting protein below 0.8 g/kg/day, which risks malnutrition."),
                        ],
                    },
                ],
            },
            {
                "title": "CKD-MBD",
                "slug": "ckd-mbd",
                "description": "CKD-mineral and bone disorder: phosphate, PTH, calcium, and bone disease.",
                "lessons": [
                    {
                        "title": "CKD-MBD Pathway",
                        "lesson_slug": "ckd-mbd-pathway",
                        "lesson_type": "animation",
                        "summary": "Step animation of phosphate retention, PTH, and skeletal consequences in CKD.",
                        "animation_url": f"{ANIMATION_BASE}/ckd-mbd-pathway.json",
                        "duration_seconds": 120,
                        "reference_ids": ["kdigo-ckd-mbd-2017"],
                    },
                    {
                        "title": "CKD-MBD Management",
                        "lesson_slug": "ckd-mbd-management",
                        "lesson_type": "article",
                        "summary": "Dietary phosphate, phosphate binders, calcimimetics, and bone biopsy indications.",
                        "content_md": (
                            "# Managing CKD-MBD\n\n"
                            "## Phosphate\n"
                            "- Restrict dietary phosphate additives (processed food, cola, enhanced meats) first: additives "
                            "are far more absorbable than natural food phosphate\n"
                            "- Prefer sevelamer (non-calcium) over calcium-based binders in adults, and limit total calcium "
                            "exposure to avoid vascular calcification\n"
                            "- Do not routinely dialyze patients to lower phosphate for uremic symptoms\n\n"
                            "## Calcium and PTH\n"
                            "- Maintain normal serum calcium; correct hypocalcemia before giving a calcimimetic\n"
                            "- In dialysis patients, avoid routine PTH suppression to the normal range in secondary "
                            "hyperparathyroidism; cinacalcet lowers PTH and calcium requirements\n"
                            "- Parathyroidectomy is reserved for severe, refractory disease\n\n"
                            "## Bone\n"
                            "- Renal osteodystrophy ranges from high-turnover (osteitis fibrosa) to low-turnover adynamic bone "
                            "disease; bone biopsy is reserved for atypical fractures, unexplained skeletal pain, or "
                            "biochemical discordance\n\n"
                            "## Other components\n"
                            "Correction of metabolic acidosis, avoidance of unnecessary vitamin D analogues in patients not on "
                            "vitamin D therapy, and management of hypermagnesemia in advanced CKD."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-ckd-mbd-2017"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A patient on thrice-weekly hemodialysis has calcium 9.9 mg/dL, phosphate 7.4 mg/dL, intact PTH 820 pg/mL, and bone pain. He takes sevelamer carbonate with meals and calcium carbonate twice daily.",
                        "labs": {"ca": "9.9 mg/dL", "phosphate": "7.4 mg/dL", "pth": "820 pg/mL"},
                        "question_text": "What is the most appropriate next step in managing this dialysis patient with severe secondary hyperparathyroidism?",
                        "explanation": "This patient has severe secondary hyperparathyroidism with hyperphosphatemia despite phosphate binder therapy. The first step is dietary phosphate restriction (especially additives), reduction or discontinuation of calcium-based binders to limit calcium loading, and optimization of dialysis. In dialysis patients with PTH persistently above the target range, a calcimimetic such as cinacalcet is indicated; it lowers PTH and calcium requirements without the calcium loading of vitamin D analogues. Parathyroidectomy is reserved for refractory disease, and bisphosphonates are generally avoided in advanced CKD because of adynamic bone risk.",
                        "clinical_pearl": "In dialysis CKD-MBD: drop calcium-based binders, use sevelamer, and add cinacalcet for persistent PTH elevation.",
                        "reference_ids": ["kdigo-ckd-mbd-2017"],
                        "lesson_slug": "ckd-mbd-management",
                        "choices": [
                            ("A", "Increase the calcium carbonate dose and add calcitriol", False, "More calcium-based binder plus vitamin D would raise calcium and worsen calcium-based vascular calcification risk without controlling PTH."),
                            ("B", "Continue sevelamer only, add doxercalciferol, and follow in 3 months", False, "PTH of 820 with phosphate 7.4 despite binders needs binder optimization and a calcimimetic, not more vitamin D."),
                            ("C", "Restrict dietary phosphate additives, reduce calcium-based binder use, and start a calcimimetic such as cinacalcet", True, None),
                            ("D", "Refer for parathyroidectomy", False, "Parathyroidectomy is reserved for severe refractory disease after medical therapy is optimized."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 68-year-old with CKD G4 not on dialysis has been started on sevelamer carbonate for hyperphosphatemia. She asks why her doctor avoided calcium carbonate.",
                        "labs": {"egfr": "22 mL/min/1.73m2", "phosphate": "6.1 mg/dL", "ca": "9.6 mg/dL"},
                        "question_text": "What is the strongest evidence-based reason to prefer sevelamer over a calcium-based phosphate binder in this patient?",
                        "explanation": "Randomized trials in CKD and ESRD patients on phosphate-lowering treatment showed that sevelamer was associated with lower mortality and fewer hospitalizations for cardiovascular and infectious causes, whereas calcium-based binders did not. Excess calcium absorption also promotes vascular and soft-tissue calcification. KDIGO therefore suggests limiting the use of calcium-based phosphate binders in adults receiving phosphate-lowering treatment. Sevelamer does not bind vitamin D analogues as calcium-based binders do, so vitamin D deficiency can occur and needs monitoring.",
                        "clinical_pearl": "Calcium-based phosphate binders are cheap but carry a mortality signal and calcium load; sevelamer is preferred for chronic phosphate control.",
                        "reference_ids": ["kdigo-ckd-mbd-2017"],
                        "lesson_slug": "ckd-mbd-pathway",
                        "choices": [
                            ("A", "Sevelamer lowers PTH more effectively than calcium-based binders", False, "Sevelamer does not lower PTH; that is the role of cinacalcet and vitamin D analogues."),
                            ("B", "Calcium-based binders cause worsening metabolic acidosis", False, "Calcium citrate is alkalinizing, but binder choice is driven by mortality and calcium load, not acidosis."),
                            ("C", "Calcium-based binders add absorbed calcium load and were associated with higher mortality and hospitalizations than sevelamer in randomized trials", True, None),
                            ("D", "Sevelamer has a more favorable gastrointestinal side effect profile than calcium-based binders", False, "Sevelamer commonly causes GI upset and constipation; it is not better tolerated."),
                        ],
                    },
                ],
            },
            {
                "title": "Anemia of CKD",
                "slug": "anemia-of-ckd",
                "description": "Erythropoietin deficiency, iron deficiency, and safe use of ESA therapy.",
                "lessons": [
                    {
                        "title": "Anemia of CKD and Erythropoiesis-Stimulating Agents",
                        "lesson_slug": "anemia-of-ckd-and-erythropoiesis-stimulating-agents",
                        "lesson_type": "article",
                        "summary": "Iron status, ESA initiation thresholds, targets, and risks of ESAs in CKD.",
                        "content_md": (
                            "# Anemia of CKD\n\n"
                            "## Mechanism\n"
                            "Progressive CKD reduces renal peritubular cell mass, lowering erythropoietin production, while "
                            "shortened red cell survival, iron deficiency, inflammation, and blood loss add to the deficit.\n\n"
                            "## Always exclude reversible causes\n"
                            "Check iron indices (ferritin, transferrin saturation), B12 and folate, blood loss (including GI "
                            "and menstrual), hemolysis, and occult inflammation before labeling anemia as CKD-related.\n\n"
                            "## Iron therapy\n"
                            "- Oral iron first in non-dialysis patients when TSAT is low and ferritin is below 500 ng/mL\n"
                            "- IV iron for dialysis patients, poor responders, or when oral therapy is not tolerated\n"
                            "- KDIGO targets for non-dialysis CKD are ferritin above 100 ng/mL and TSAT above 20% "
                            "(500 ng/mL and 20% on dialysis)\n\n"
                            "## ESAs\n"
                            "- Consider an ESA when hemoglobin is below 10 g/dL in non-dialysis CKD after iron repletion\n"
                            "- Do not use ESAs to correct anemia secondary to bleeding, hemolysis, or folate/B12 deficiency\n"
                            "- Do not intentionally exceed hemoglobin 11.5 g/dL in non-dialysis patients: ESA trials showed "
                            "increased cardiovascular and thrombotic events at higher targets\n"
                            "- Risks: hypertension, seizures, thrombosis, pure red cell aplasia (anti-EPO antibodies)\n\n"
                            "## Monitoring\n"
                            "Avoid routine transcranial ultrasound screening; monitor CBC and dose-adjust to the lowest "
                            "effective dose."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["nkf-anemia-2021", "kdigo-ckd-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 68-year-old woman with CKD G4 (eGFR 19) has hemoglobin 8.0 g/dL, ferritin 60 ng/mL, transferrin saturation 18%, MCV 89 fL. She is not on dialysis and reports no bleeding history.",
                        "labs": {"hgb": "8.0 g/dL", "ferritin": "60 ng/mL", "tsat": "18%", "mcv": "89 fL", "egfr": "19 mL/min/1.73m2"},
                        "question_text": "What is the most appropriate next step in the management of this anemia?",
                        "explanation": "Iron-restricted indices (ferritin 60, TSAT 18%) show absolute iron deficiency, which is correctable and must be treated before an erythropoiesis-stimulating agent. KDIGO suggests initiating iron therapy in non-dialysis CKD when hemoglobin is below 10 g/dL, ferritin is below 500 ng/mL, and TSAT is below 30%. Oral iron is first-line in non-dialysis patients; IV iron is reserved for intolerance, malabsorption, non-response, or dialysis patients. An ESA is only considered after iron repletion.",
                        "clinical_pearl": "Always replete iron before starting an ESA: ferritin 60 with TSAT 18% is a treatable cause of anemia in CKD.",
                        "reference_ids": ["nkf-anemia-2021", "kdigo-ckd-2024"],
                        "lesson_slug": "anemia-of-ckd-and-erythropoiesis-stimulating-agents",
                        "choices": [
                            ("A", "Start an erythropoiesis-stimulating agent at a dose targeting hemoglobin 12 g/dL", False, "Iron deficiency must be corrected first, and hemoglobin should not be intentionally pushed to 12 g/dL because higher ESA targets increase cardiovascular and thrombotic risk."),
                            ("B", "Replete iron (oral first in non-dialysis CKD) and reassess hemoglobin before considering an ESA", True, None),
                            ("C", "Transfuse two units of packed red cells", False, "Transfusion is reserved for severe symptomatic or life-threatening anemia, not a hemoglobin of 8.0 g/dL that is correctable with iron and an ESA."),
                            ("D", "Check the serum erythropoietin level and replace it", False, "Exogenous erythropoietin is not replaced as a hormone; a serum EPO level is not clinically useful for guiding therapy."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 72-year-old on hemodialysis with hemoglobin 10.4 g/dL is on darbepoetin 40 mcg weekly with monthly dose escalation. He now has BP 168/96 despite amlodipine. Two months ago his hemoglobin was 11.2 g/dL on the same dose.",
                        "labs": {"hgb": "10.4 g/dL", "hgb_prior": "11.2 g/dL", "bp": "168/96", "tsat": "31%"},
                        "question_text": "Which adjustment is most appropriate?",
                        "explanation": "The patient has new or worsening anemia after a period of adequate ESA response, which should prompt a search for a new cause (occult blood loss, iron depletion, infection, inflammation, or malignancy) rather than escalation. Dose escalation is a recognized cause of resistant anemia. Independently, a rising hemoglobin with worsening hypertension is a signal to hold or reduce the ESA: guidance is to use the lowest effective dose and avoid intentional normalization of hemoglobin, because higher targets were associated with increased cardiovascular events, hypertension, and thrombosis. Iron repletion and an etiology workup should precede any increase in dose.",
                        "clinical_pearl": "Anemia that worsens on a stable ESA dose is a red flag for a new cause. Never escalate an ESA with uncontrolled hypertension.",
                        "reference_ids": ["nkf-anemia-2021"],
                        "lesson_slug": "anemia-of-ckd-and-erythropoiesis-stimulating-agents",
                        "choices": [
                            ("A", "Increase darbepoetin to 60 mcg weekly to raise hemoglobin above 11.5 g/dL", False, "Dose escalation is a cause of resistant anemia, and raising hemoglobin further with BP 168/96 risks thrombosis and cardiovascular events."),
                            ("B", "Hold or reduce the ESA dose, evaluate for occult blood loss and iron depletion, and manage blood pressure", True, None),
                            ("C", "Add an ACE inhibitor to lower blood pressure and continue escalation", False, "Blood pressure control is appropriate, but ESA escalation should be avoided while the new anemia is unexplained."),
                            ("D", "Add androgens to stimulate endogenous erythropoiesis", False, "Androgens are not recommended for CKD anemia and carry substantial toxicity."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Hypertension",
        "slug": "hypertension",
        "order_index": 5,
        "description": "Blood pressure measurement and diagnosis, primary and secondary hypertension, resistant hypertension, and renovascular disease.",
        "icon": "HeartIcon",
        "category_slug": "hypertension",
        "topics": [
            {
                "title": "Primary Hypertension",
                "slug": "primary-hypertension",
                "description": "Confirming the diagnosis and choosing initial pharmacotherapy.",
                "lessons": [
                    {
                        "title": "Blood Pressure Measurement and Diagnosis",
                        "lesson_slug": "blood-pressure-measurement-and-diagnosis",
                        "lesson_type": "article",
                        "summary": "Correct office technique, ambulatory and home monitoring, and when hypertension is confirmed.",
                        "content_md": (
                            "# Confirming hypertension\n\n"
                            "## Office technique\n"
                            "- No caffeine, nicotine, or exercise for 30 minutes; empty the bladder\n"
                            "- Cuff bladder length 80% and width 40% of arm circumference; use the larger arm\n"
                            "- Patient seated, back and arm supported, feet flat, arm at heart level\n"
                            "- Average at least two readings one minute apart\n\n"
                            "## Thresholds\n"
                            "- Clinic: >= 140/90 mmHg (ACC/AHA); KDIGO uses >= 130/80 mmHg as the office threshold in CKD\n"
                            "- Home or 24-hour ambulatory average determines white-coat and masked hypertension\n"
                            "- White-coat hypertension: office >= 140/90 with out-of-office < 135/85 and no target-organ damage\n"
                            "- Masked hypertension: office < 140/90 with out-of-office elevation\n\n"
                            "## Evaluation\n"
                            "Check for target-organ damage (retina, heart, kidney, peripheral arteries) and screen for "
                            "secondary causes in young patients, sudden onset, resistant or severe hypertension, "
                            "hypokalemia, or asymmetric kidneys."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["kdigo-bp-2021", "kdigo-ckd-2024"],
                    },
                    {
                        "title": "Antihypertensive Pharmacotherapy",
                        "lesson_slug": "antihypertensive-pharmacotherapy",
                        "lesson_type": "article",
                        "summary": "First-line drug classes, combination therapy, and individualized BP targets.",
                        "content_md": (
                            "# Pharmacologic treatment\n\n"
                            "## First-line classes\n"
                            "Thiazide-type diuretics, ACE inhibitors, ARBs, dihydropyridine calcium channel blockers, and "
                            "in CKD, a mineralocorticoid receptor antagonist or SGLT2 inhibitor where indicated.\n\n"
                            "## Combination therapy\n"
                            "- Stage 2 hypertension is generally treated with two agents from different classes\n"
                            "- Prefer single-pill combinations to improve adherence\n"
                            "- Use the maximally tolerated dose of the first agent before adding a second\n\n"
                            "## Renal-specific choices\n"
                            "- ACEi/ARB reduce albuminuria in CKD and are the drugs of choice for proteinuric disease\n"
                            "- SGLT2 inhibitors lower blood pressure and slow CKD progression\n"
                            "- Avoid dual ACEi plus ARB combination (hyperkalemia, AKI, no outcome benefit)\n\n"
                            "## Targets\n"
                            "KDIGO suggests a systolic target below 120 mmHg when tolerated; ACC/AHA and ADA targets are "
                            "below 130/80 mmHg in CKD and diabetes. Individualize for orthostatic symptoms and frailty."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-bp-2021", "kdigo-ckd-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 58-year-old is found to have office blood pressures of 138-146/86-92 mmHg on three visits. His home readings average 126/76 mmHg twice daily and his 24-hour ambulatory average is 124/74 mmHg. He has no diabetes, no CKD, and a normal examination.",
                        "labs": {"clinic_bp": "138-146/86-92", "home_bp": "126/76", "abpm": "124/74", "bmi": "31 kg/m2"},
                        "question_text": "What is the most appropriate next step for elevated office but normal home and ambulatory blood pressure?",
                        "explanation": "The out-of-office readings are below the white-coat hypertension thresholds (home < 135/85, 24-hour < 130/80). Without target-organ damage, this pattern is white-coat hypertension. The correct approach is lifestyle modification, avoidance of office-triggered overtreatment, and continued out-of-office monitoring, not antihypertensive drugs. Treating here exposes the patient to hypotension and drug side effects without benefit; failing to detect masked hypertension is the opposite error and is dangerous.",
                        "clinical_pearl": "Never diagnose or treat hypertension on office readings alone when home or ambulatory monitoring is available.",
                        "reference_ids": ["kdigo-bp-2021"],
                        "lesson_slug": "blood-pressure-measurement-and-diagnosis",
                        "choices": [
                            ("A", "Start a thiazide diuretic and titrate until office BP is below 140/90", False, "Out-of-office pressure is already at goal, so antihypertensive therapy would produce office hypotension and overtreatment."),
                            ("B", "Treat as white-coat hypertension with lifestyle measures and continued home BP monitoring", True, None),
                            ("C", "Start lisinopril because the patient is high risk", False, "Without target-organ damage or a risk profile that meets treatment thresholds, white-coat hypertension is not treated pharmacologically."),
                            ("D", "Repeat office measurements only in the morning without out-of-office monitoring", False, "Office-only repeat measurements cannot distinguish white-coat from sustained hypertension."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 55-year-old man presents with newly diagnosed stage 2 hypertension, average BP 158/96 mmHg, with no diabetes, eGFR 70 mL/min/1.73 m2, and no target-organ damage.",
                        "labs": {"bp": "158/96", "egfr": "70 mL/min/1.73m2", "k": "4.1 mEq/L"},
                        "question_text": "Which initial pharmacotherapy approach is most appropriate?",
                        "explanation": "Stage 2 hypertension is defined as a blood pressure of at least 140/90 mmHg, and a starting BP of 158/96 is more than 20/10 mmHg above goal. Guidelines recommend initiating two agents from different classes rather than a single agent, ideally as a single-pill combination. For a patient with hypertension and elevated albuminuria risk, an ACE inhibitor or ARB plus a dihydropyridine calcium channel blocker is an appropriate, evidence-based starting pair. Single-agent therapy would require several visits to reach goal and would undertreat a known, easily treated condition.",
                        "clinical_pearl": "Stage 2 hypertension starts with two complementary agents, ideally in one pill, to reach goal faster.",
                        "reference_ids": ["kdigo-bp-2021"],
                        "lesson_slug": "antihypertensive-pharmacotherapy",
                        "choices": [
                            ("A", "Begin two complementary first-line agents, such as an ACE inhibitor or ARB plus a dihydropyridine calcium channel blocker, ideally as a single-pill combination", True, None),
                            ("B", "Begin a single beta blocker and reassess in 4 weeks", False, "Beta blockers are not first-line for uncomplicated primary hypertension, and single-agent therapy is slow for stage 2 disease."),
                            ("C", "Begin a low-dose thiazide only, then add a loop diuretic next month", False, "Sequential single-agent therapy delays goal attainment, and loop diuretics are reserved for resistant disease or low eGFR."),
                            ("D", "Begin an ACE inhibitor alone because monotherapy is preferred to avoid adverse effects", False, "Dual combination therapy is recommended for stage 2 hypertension, with adverse effects managed by agent choice and combination pills."),
                        ],
                    },
                ],
            },
            {
                "title": "Hypertension in CKD",
                "slug": "hypertension-ckd",
                "description": "Blood pressure targets and RAAS blockade in proteinuric kidney disease.",
                "lessons": [
                    {
                        "title": "Hypertension in CKD",
                        "lesson_slug": "hypertension-in-ckd",
                        "lesson_type": "article",
                        "summary": "Why albuminuria changes drug selection, and monitoring after starting ACEi/ARB.",
                        "content_md": (
                            "# Hypertension in CKD\n\n"
                            "## Why albuminuria drives drug choice\n"
                            "Angiotensin II constricts the efferent arteriole, raising intraglomerular pressure. ACE inhibitors "
                            "and ARBs dilate the efferent arteriole, lowering intraglomerular pressure and albuminuria, and "
                            "they slow GFR decline in albuminuric CKD.\n\n"
                            "## Starting and monitoring\n"
                            "- Check creatinine and potassium 1-2 weeks after starting and with every dose change\n"
                            "- A creatinine rise of up to about 30% is expected; continue therapy and reassess\n"
                            "- Hyperkalemia is managed with dietary counselling, diuretics, potassium binders, or a "
                            "beta-2 agonist before stopping the RAAS inhibitor\n\n"
                            "## Targets\n"
                            "KDIGO suggests a systolic target below 120 mmHg when tolerated; targets below 130/80 mmHg are "
                            "recommended by ACC/AHA and ADA for CKD and diabetes.\n\n"
                            "## What not to do\n"
                            "Do not combine an ACEi with an ARB, and do not combine either with a direct renin inhibitor."
                        ),
                        "duration_seconds": 200,
                        "reference_ids": ["kdigo-ckd-2024", "kdigo-bp-2021"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 66-year-old with diabetic CKD and UACR 800 mg/g starts lisinopril 10 mg daily. Two weeks later creatinine rose from 1.4 to 1.7 mg/dL (21% increase) and potassium is 4.6 mEq/L.",
                        "labs": {"cr_before": "1.4 mg/dL", "cr_after": "1.7 mg/dL", "k": "4.6 mEq/L", "uacr": "800 mg/g"},
                        "question_text": "What is the most appropriate next step after this 21% creatinine rise on a newly started ACE inhibitor?",
                        "explanation": "A 21% creatinine rise after starting an ACE inhibitor is within the expected hemodynamic effect of reducing intraglomerular pressure, and potassium is acceptable at 4.6 mEq/L. KDIGO recommends continuing ACEi/ARB therapy despite a creatinine rise of up to approximately 30% and monitoring, because albuminuric CKD with blood pressure above goal needs antiproteinuric therapy. Additional workup is warranted if the rise exceeds 30%, if potassium rises above about 5.0-5.5 mEq/L, or if there is volume depletion, concurrent NSAID use, or suspicion of renal artery stenosis.",
                        "clinical_pearl": "Up to a ~30% creatinine rise is an acceptable price of RAAS blockade in albuminuric CKD; only larger rises should trigger workup.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "hypertension-in-ckd",
                        "choices": [
                            ("A", "Stop lisinopril and switch to a calcium channel blocker", False, "A 21% rise with normal potassium is the expected effect; stopping removes antiproteinuric benefit that a calcium channel blocker will not match."),
                            ("B", "Continue lisinopril, recheck creatinine and potassium in 1-2 weeks, and titrate toward a systolic goal below 120-130 mmHg", True, None),
                            ("C", "Add an ARB to intensify renin-angiotensin blockade", False, "Dual RAAS blockade raises potassium and acute kidney injury risk without improving kidney outcomes."),
                            ("D", "Order a renal artery Doppler ultrasound immediately", False, "A mild, asymptomatic creatinine rise after ACEi initiation does not by itself indicate renal artery stenosis."),
                        ],
                    },
                ],
            },
            {
                "title": "Resistant Hypertension",
                "slug": "resistant-hypertension",
                "description": "Definition, confirmation, and fourth-line therapy with mineralocorticoid receptor antagonists.",
                "lessons": [
                    {
                        "title": "Resistant Hypertension",
                        "lesson_slug": "resistant-hypertension",
                        "lesson_type": "article",
                        "summary": "Confirming true resistance, the usual contributing causes, and MRA therapy.",
                        "content_md": (
                            "# Resistant hypertension\n\n"
                            "## Definition\n"
                            "Blood pressure above goal despite three antihypertensive agents of different classes, including "
                            "a diuretic, at maximally tolerated doses, or blood pressure controlled only with four or more "
                            "agents. Apparent or pseudo-resistance arises from non-adherence, inaccurate measurement, or a "
                            "white-coat effect.\n\n"
                            "## Always confirm\n"
                            "1. Verify adherence (pill counts, pharmacy refill data, drug levels)\n"
                            "2. Verify technique and cuff size, and out-of-office blood pressure\n"
                            "3. Review for interfering drugs: NSAIDs, decongestants, combined oral contraceptives, "
                            "corticosteroids, calcineurin inhibitors, licorice, ephedra\n"
                            "4. Screen for secondary causes: primary aldosteronism, renovascular disease, obstructive "
                            "sleep apnea, Cushing syndrome, pheochromocytoma, coarctation, CKD\n\n"
                            "## Fourth-line therapy\n"
                            "A mineralocorticoid receptor antagonist (spironolactone or eplerenone; eplerenone or amiloride if "
                            "gynecomastia). Check potassium and eGFR at 1 week, 1 month, then every 3-6 months."
                        ),
                        "duration_seconds": 240,
                        "image_url": f"{MEDICAL_ASSET_BASE}/hypertension/renal-denervation.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/hypertension/renal-denervation-thumb.webp",
                        "reference_ids": ["kdigo-bp-2021", "uptodate-renovascular"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 60-year-old with CKD G3a has BP 168/92 on amlodipine 10 mg, lisinopril 40 mg, and chlorthalidone 25 mg. In clinic BP is 182/96; home average is 152/86. Sodium is 138 mEq/L, potassium 4.4 mEq/L. She reports good adherence and uses NSAIDs for back pain.",
                        "labs": {"clinic_bp": "182/96", "home_bp": "152/86", "na": "138 mEq/L", "k": "4.4 mEq/L"},
                        "question_text": "What is the most appropriate next step before adding fourth-line therapy?",
                        "explanation": "The patient meets criteria for apparent resistant hypertension on three agents including a diuretic, and home readings confirm real elevation, so this is not a white-coat effect. However, correctable contributors remain: NSAID use causes sodium retention, blunts diuretic and ACEi effect, and impairs autoregulation, and a sodium of 138 mEq/L suggests high sodium intake. Stopping the NSAID, restricting sodium, and confirming adherence are prerequisites before escalating to a mineralocorticoid receptor antagonist, which is then the preferred fourth agent if potassium and eGFR permit.",
                        "clinical_pearl": "Before the fourth drug: stop NSAIDs, cut sodium, confirm adherence, and check out-of-office BP. Spironolactone is the usual fourth agent.",
                        "reference_ids": ["kdigo-bp-2021"],
                        "lesson_slug": "resistant-hypertension",
                        "choices": [
                            ("A", "Add spironolactone 25 mg daily immediately", False, "Interfering NSAID use and sodium intake must be corrected, and adherence and out-of-office BP confirmed, before labelling true resistance and escalating."),
                            ("B", "Discontinue the NSAID, institute sodium restriction, verify adherence and home BP, then add a mineralocorticoid receptor antagonist if still uncontrolled", True, None),
                            ("C", "Add metoprolol and a hydralazine regimen", False, "Beta blocker plus hydralazine is a later-line, poorly tolerated strategy that ignores correctable causes."),
                            ("D", "Refer for renal artery stenting", False, "Stenting is reserved for specific high-risk anatomy or recurrent flash pulmonary edema, not for apparent resistant hypertension."),
                        ],
                    },
                ],
            },
            {
                "title": "Renovascular Hypertension",
                "slug": "renovascular-hypertension",
                "description": "Suspecting, screening, and treating renovascular disease.",
                "lessons": [
                    {
                        "title": "Renovascular Hypertension Pathway",
                        "lesson_slug": "renovascular-hypertension-pathway",
                        "lesson_type": "animation",
                        "summary": "Step animation of RAAS activation and the hemodynamic consequences of renal artery stenosis.",
                        "animation_url": f"{ANIMATION_BASE}/renovascular-htn.json",
                        "duration_seconds": 110,
                        "image_url": f"{MEDICAL_ASSET_BASE}/hypertension/renovascular-hypertension-angiogram.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/hypertension/renovascular-hypertension-angiogram-thumb.webp",
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/hypertension/renovascular-hypertension.html",
                        "reference_ids": ["uptodate-renovascular"],
                    },
                    {
                        "title": "Fibromuscular Dysplasia",
                        "lesson_slug": "fibromuscular-dysplasia",
                        "lesson_type": "article",
                        "summary": "Clinical profile, imaging, and angioplasty-based management of renal FMD.",
                        "content_md": (
                            "# Renal artery fibromuscular dysplasia\n\n"
                            "## Profile\n"
                            "A non-atherosclerotic, non-inflammatory arterial disease of young to middle-aged women. Renal "
                            "involvement causes hypertension, often with onset before age 30. Extrarenal involvement includes "
                            "the carotid and iliac territories and may present with dissection, aneurysm, or stroke.\n\n"
                            "## Imaging\n"
                            "- Duplex ultrasound: screening test of choice, though operator dependent and limited by body habitus\n"
                            "- CT or MR angiography: the noninvasive tests of choice for definitive diagnosis when creatinine "
                            "permits contrast for CTA\n"
                            "- Catheter angiography: the reference standard and used before intervention\n\n"
                            "## Medial fibroplasia (the commonest subtype)\n"
                            "The classic string-of-beads appearance alternating stenosis and aneurysm-like dilation.\n\n"
                            "## Management\n"
                            "Balloon angioplasty without stent is the treatment of choice for hemodynamically significant "
                            "renal FMD; stenting is generally avoided because of fracture risk. RAAS blockade is used for "
                            "hypertension and may reduce the need for intervention."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["uptodate-renovascular"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 29-year-old woman with no prior history presents with new-onset hypertension of 168/94 mmHg. Creatinine rose from 0.9 to 1.5 mg/dL three weeks after starting lisinopril. Renal ultrasound shows the right kidney is 9.2 cm and the left is 12.4 cm.",
                        "labs": {"bp": "168/94", "cr": "1.5 mg/dL", "kidneys": "9.2 vs 12.4 cm"},
                        "question_text": "What is the most appropriate next diagnostic step?",
                        "explanation": "This constellation strongly suggests unilateral renal artery stenosis: new hypertension under age 30 in a woman, a greater than 1.5 cm difference in kidney size, and a creatinine rise after starting an ACE inhibitor from loss of efferent arteriolar support to the affected kidney. Duplex ultrasonography is the preferred first-line screening test because it is noninvasive, has no contrast risk, and can measure flow velocity. CTA and MRA improve anatomic definition when duplex is equivocal, and catheter angiography is the reference standard used when an intervention is planned.",
                        "clinical_pearl": "Onset under 30, asymmetric kidneys, and a creatinine rise on an ACE inhibitor = renal artery stenosis; screen with duplex ultrasound.",
                        "reference_ids": ["uptodate-renovascular"],
                        "lesson_slug": "renovascular-hypertension-pathway",
                        "choices": [
                            ("A", "Renal artery duplex ultrasound", True, None),
                            ("B", "Adrenal CT to look for an aldosterone-producing adenoma", False, "Primary aldosteronism causes hypertension with hypokalemic metabolic alkalosis, not kidney size asymmetry or an ACEi-associated creatinine rise."),
                            ("C", "Plasma renin and aldosterone to screen for primary aldosteronism", False, "Same as above: this is a renovascular pattern, not an aldosterone-producing tumor pattern."),
                            ("D", "Renal biopsy to exclude glomerulonephritis", False, "There is no proteinuria or active sediment here, and kidney size asymmetry points to a vascular cause."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 34-year-old woman with hypertension since age 26 presents after a transient ischemic attack. CTA shows a string-of-beads appearance in the mid right renal artery and a similar pattern in the right internal carotid artery.",
                        "labs": {"bp": "154/92", "ct_rca": "string-of-beads, mid segment", "ct_ric": "string-of-beads"},
                        "question_text": "What is the most appropriate management of the renal artery lesion?",
                        "explanation": "The string-of-beads appearance in the mid renal artery in a young woman with extracranial carotid involvement is classic for medial fibromuscular dysplasia. For hemodynamically significant renal FMD, percutaneous transluminal balloon angioplasty without stent is the treatment of choice; stenting is generally avoided because the diseased segment is fragile and prone to dissection and stent fracture. Blood pressure, renal function, and statin plus antiplatelet therapy are managed medically, and carotid FMD warrants a multidisciplinary stroke-prevention approach.",
                        "clinical_pearl": "Renal FMD: balloon angioplasty without stenting. Stent only as bailout for a flow-limiting dissection.",
                        "reference_ids": ["uptodate-renovascular"],
                        "lesson_slug": "fibromuscular-dysplasia",
                        "choices": [
                            ("A", "Percutaneous balloon angioplasty without stent placement", True, None),
                            ("B", "Primary stenting of the renal artery stenosis", False, "Stents fracture readily in fibromuscular dysplasia and are reserved for bailout situations such as a flow-limiting dissection."),
                            ("C", "Optimal medical therapy alone, with no intervention planned", False, "In young patients with hemodynamically significant FMD, angioplasty improves blood pressure and preserves renal function rather than relying on lifelong medical therapy."),
                            ("D", "Systemic corticosteroids to treat the arteriopathy", False, "Fibromuscular dysplasia is neither inflammatory nor vasculitic, so immunosuppression has no role."),
                        ],
                    },
                ],
            },
            {
                "title": "Secondary Hypertension",
                "slug": "secondary-hypertension",
                "description": "Screening for and confirming the common causes of secondary hypertension.",
                "lessons": [
                    {
                        "title": "Secondary Hypertension",
                        "lesson_slug": "secondary-hypertension",
                        "lesson_type": "article",
                        "summary": "Clinical clues and confirmatory testing for primary aldosteronism, OSA, pheochromocytoma, and thyroid disease.",
                        "content_md": (
                            "# Secondary hypertension\n\n"
                            "## Clues to look for\n"
                            "- Onset before age 30 or after age 55\n"
                            "- Sudden onset, severe hypertension (>= 180/120 mmHg), or resistant hypertension\n"
                            "- Spontaneous or readily provoked hypokalemia with metabolic alkalosis (mineralocorticoid excess)\n"
                            "- Snoring, witnessed apnea, morning headache, obesity (obstructive sleep apnea)\n"
                            "- Episodic headache, palpitations, diaphoresis (pheochromocytoma)\n"
                            "- Cushingoid features, purple striae, proximal myopathy\n"
                            "- Renal asymmetry or bruit (renovascular), abdominal bruit\n"
                            "- Coarctation: radiofemoral delay with lower leg than arm pressure\n\n"
                            "## Confirmatory testing\n"
                            "- Primary aldosteronism: elevated aldosterone-to-renin ratio confirmed by saline infusion, oral "
                            "sodium loading, fludrocortisone suppression, or captopril challenge; adrenal vein sampling for "
                            "subtyping when surgery is considered\n"
                            "- Pheochromocytoma: plasma free or 24-hour urine fractionated metanephrines\n"
                            "- Thyroid dysfunction: TSH\n"
                            "- Hyperparathyroidism: calcium and PTH\n"
                            "- Obstructive sleep apnea: polysomnography or home sleep apnea test"
                        ),
                        "duration_seconds": 240,
                        "image_url": f"{MEDICAL_ASSET_BASE}/hypertension/secondary-hypertension-renin-aldosterone.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/hypertension/secondary-hypertension-renin-aldosterone-thumb.webp",
                        "reference_ids": ["uptodate-dds", "kdigo-bp-2021"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 45-year-old with hypertension on three agents including chlorthalidone has persistent BP 162/88. He has taken no diuretics for 2 weeks. Potassium is 2.9 mEq/L with a metabolic alkalosis: bicarbonate 35 mEq/L. Plasma aldosterone is 22 ng/dL with a plasma renin activity of 0.3 ng/mL/h. The patient declines surgery.",
                        "labs": {"bp": "162/88", "k": "2.9 mEq/L", "hco3": "35 mEq/L", "aldosterone": "22 ng/dL", "pra": "0.3 ng/mL/h"},
                        "question_text": "What is the next step in management?",
                        "explanation": "Spontaneous hypokalemia with metabolic alkalosis and an inappropriately elevated aldosterone-to-renin ratio (22/0.3, well above a screening threshold of roughly 20 with aldosterone above 15 ng/dL) indicates primary aldosteronism; false positives are minimized by stopping the diuretic and correcting potassium. This causes hypertension through volume expansion and hypokalemia through aldosterone-driven renal potassium wasting. If the patient declines surgery, medical treatment with a mineralocorticoid receptor antagonist is indicated, along with correction of hypokalemia, dietary sodium restriction, and surveillance of potassium and creatinine on treatment.",
                        "clinical_pearl": "Primary aldosteronism: hypertension, hypokalemia, metabolic alkalosis, suppressed renin with high aldosterone. Treat with an MRA if not surgically eligible.",
                        "reference_ids": ["uptodate-dds", "kdigo-bp-2021"],
                        "lesson_slug": "secondary-hypertension",
                        "choices": [
                            ("A", "Start a mineralocorticoid receptor antagonist, correct potassium, and restrict sodium", True, None),
                            ("B", "Increase chlorthalidone to 50 mg daily and recheck potassium", False, "Thiazide and loop diuretics worsen hypokalemia and metabolic alkalosis; they do not treat aldosterone excess."),
                            ("C", "Start metoprolol as the agent of choice", False, "Beta blockers are less effective in primary aldosteronism because they lower renin further and can impair aldosterone measurement; an MRA is preferred."),
                            ("D", "Repeat the aldosterone-to-renin ratio after stopping chlorthalidone and take no further action", False, "The phenotype is diagnostic of primary aldosteronism and needs treatment, not repeat screening alone."),
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
        "description": "Hemodialysis principles and adequacy, vascular access, hemodialysis complications, and peritoneal dialysis.",
        "icon": "RepeatIcon",
        "category_slug": "dialysis",
        "topics": [
            {
                "title": "Hemodialysis Principles",
                "slug": "hemodialysis-principles",
                "description": "Transport mechanisms, membrane basics, and prescription components.",
                "lessons": [
                    {
                        "title": "Hemodialysis Principles",
                        "lesson_slug": "hemodialysis-principles",
                        "lesson_type": "article",
                        "summary": "Diffusion, convection, ultrafiltration, and the components of a dialysis prescription.",
                        "content_md": (
                            "# Hemodialysis principles\n\n"
                            "## Transport mechanisms\n"
                            "- Diffusion: the main mechanism of small-solute removal (urea, creatinine, electrolytes) down a "
                            "concentration gradient across a semipermeable membrane, driven by blood and dialysate counterflow\n"
                            "- Convection: solute drag with water across the membrane, which is how middle molecules and "
                            "cytokines are removed; enhanced by internal filtration and backfiltration\n"
                            "- Ultrafiltration: transmembrane pressure-driven removal of plasma water plus the electrolytes "
                            "and small solutes carried with it\n\n"
                            "## Prescription components\n"
                            "Blood flow rate, dialysate flow rate, dialysate potassium, buffer, ultrafiltration rate, and "
                            "treatment time. Intermittent hemodialysis is typically 3 times weekly for 4 hours using high-flux "
                            "dialyzers.\n\n"
                            "## What matters most\n"
                            "Membrane surface area and flux, treatment time, blood and dialysate flow, and residual kidney "
                            "function. Convective clearance depends on time, so longer or more frequent sessions improve "
                            "middle-molecule removal more than a higher blood flow rate alone."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdoqi-hd-adequacy-2015", "kdoqi-dialysis-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A patient is on thrice-weekly hemodialysis with a high-flux dialyzer, blood flow 350 mL/min, and dialysate flow 500 mL/min. The team asks how middle molecules are best cleared.",
                        "labs": {"blood_flow": "350 mL/min", "dialysate_flow": "500 mL/min", "dialyzer": "high flux"},
                        "question_text": "Which statement about solute transport during hemodialysis is most accurate?",
                        "explanation": "Diffusion is the dominant mechanism for small solutes such as urea, creatinine, potassium, and phosphate, driven by the concentration gradient, blood and dialysate flow rates, and membrane surface area. Middle molecules are too large for effective diffusion and are cleared mainly by convection, in which solute is dragged with water across the membrane. Because convective clearance is time dependent, longer or more frequent treatments improve middle-molecule removal more than a higher blood flow rate alone, which is why longer or nocturnal sessions are favored for middle-molecule clearance.",
                        "clinical_pearl": "Diffusion clears small solutes, convection clears middle molecules, and time matters more than blood flow for the latter.",
                        "reference_ids": ["kdoqi-hd-adequacy-2015"],
                        "lesson_slug": "hemodialysis-principles",
                        "choices": [
                            ("A", "Small solutes are removed mainly by diffusion and middle molecules mainly by convection, with middle-molecule clearance limited by treatment time", True, None),
                            ("B", "All solutes are removed by ultrafiltration driven by transmembrane pressure", False, "Ultrafiltration removes plasma water and its dissolved small solutes; it cannot clear middle molecules without convection, and diffusion is the main small-solute mechanism."),
                            ("C", "Middle molecules are removed by diffusion because the dialysate flow rate exceeds 500 mL/min", False, "Diffusion becomes ineffective as molecular size approaches the molecular weight cutoff; middle molecules depend on convection."),
                            ("D", "Increasing transmembrane pressure increases small-solute clearance by steepening the diffusion gradient", False, "Transmembrane pressure drives ultrafiltration, not the diffusive gradient for small solutes."),
                        ],
                    },
                ],
            },
            {
                "title": "Dialysis Adequacy",
                "slug": "dialysis-adequacy",
                "description": "Kt/V, urea reduction ratio, and when to start or intensify dialysis.",
                "lessons": [
                    {
                        "title": "Dialysis Adequacy",
                        "lesson_slug": "dialysis-adequacy",
                        "lesson_type": "article",
                        "summary": "Measuring Kt/V, target values, and incremental versus thrice-weekly regimens.",
                        "content_md": (
                            "# Dialysis adequacy\n\n"
                            "## Key measure\n"
                            "Kt/V (a dimensionless measure of urea clearance) is the standard. KDOQI targets for "
                            "thrice-weekly hemodialysis:\n"
                            "- Target Kt/V 1.4 per session for patients with residual kidney function, aiming for a mean of "
                            "at least 1.2\n"
                            "- Minimum delivered Kt/V 1.2, measured at least monthly\n"
                            "- Single-pool Kt/V underestimates equilibrated Kt/V, particularly with residual function\n\n"
                            "## Other measures\n"
                            "A urea reduction ratio above 65% corresponds roughly to a Kt/V above 1.2 in patients with "
                            "little residual function. URR and Kt/V are not equivalent in patients with residual function, "
                            "because the denominator (urea generation) is not at steady state.\n\n"
                            "## Practical prescribing\n"
                            "4 hours 3 times weekly for most patients; extended or nocturnal dialysis for better "
                            "middle-molecule clearance. Incremental (twice-weekly) initiation is acceptable in selected "
                            "patients with residual function and stable volume, with frequency increased over time."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdoqi-hd-adequacy-2015", "kdoqi-dialysis-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 58-year-old on thrice-weekly hemodialysis has residual urine output of 800 mL/day. A single-pool Kt/V measured at the end of a session is 1.30. Post-dialysis BUN 8 mg/dL and pre-dialysis BUN 42 mg/dL.",
                        "labs": {"spktv": "1.30", "pre_bun": "42 mg/dL", "post_bun": "8 mg/dL", "uuo": "800 mL/day"},
                        "question_text": "What is the most appropriate interpretation and response?",
                        "explanation": "Guidance sets a target single-pool Kt/V of 1.4 for hemodialysis patients with residual kidney function and recommends a mean delivered Kt/V of at least 1.2, so a single-pool Kt/V of 1.30 warrants a prescription adjustment. The urea reduction ratio here is 81%, which looks reassuring but overstates adequacy in patients with residual function, because URR assumes a steady-state urea generation that does not hold when residual function replenishes urea between sessions and because single-pool Kt/V underestimates equilibrated Kt/V by rebound. The correct response is to increase the delivered dose, not to accept the reassuring URR.",
                        "clinical_pearl": "With residual function, target Kt/V 1.4. A normal URR does not override a Kt/V below target, because URR and single-pool Kt/V diverge.",
                        "reference_ids": ["kdoqi-hd-adequacy-2015"],
                        "lesson_slug": "dialysis-adequacy",
                        "choices": [
                            ("A", "Adequacy is met because the urea reduction ratio is 81% (above 65%)", False, "URR overstates adequacy in patients with residual function, and single-pool Kt/V 1.30 is below the 1.4 target for this group."),
                            ("B", "Increase treatment time, blood flow, or access flow to reach a single-pool Kt/V of at least 1.4", True, None),
                            ("C", "Switch to peritoneal dialysis because hemodialysis cannot achieve target adequacy", False, "Adequacy is a prescription problem first: time, blood flow, and access should be optimized before changing modality."),
                            ("D", "Reduce the number of sessions to twice weekly because residual function is present", False, "Reducing frequency lowers total clearance and is the opposite of the required adjustment."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 74-year-old with newly recognized CKD has an eGFR of 11 mL/min/1.73 m2, creatinine 5.4 mg/dL, persistent nausea, acidosis with bicarbonate 18 mEq/L, and worsening uremic symptoms. His urine output is 400 mL/day.",
                        "labs": {"egfr": "11 mL/min/1.73m2", "hco3": "18 mEq/L", "uo": "400 mL/day", "cr": "5.4 mg/dL"},
                        "question_text": "Which guidance statement best applies to starting kidney replacement therapy here?",
                        "explanation": "The IDEAL and EARLY trials found no survival advantage to starting dialysis at a specified eGFR compared with waiting for a clinical indication or until eGFR fell to about 5.0-5.5 mL/min/1.73 m2, in patients followed carefully. Consequently, guidance recommends initiating dialysis based on symptoms and uremic complications rather than an isolated eGFR threshold. This patient has uremic symptoms, persistent metabolic acidosis, and low residual urine output with a falling eGFR, so a plan for kidney replacement therapy should be made now, with arteriovenous access created ahead of the anticipated start date because maturation takes weeks to months.",
                        "clinical_pearl": "Start dialysis for uremic symptoms, not for an eGFR number, and create AV access months before the planned start.",
                        "reference_ids": ["kdoqi-dialysis-2015", "kdoqi-hd-adequacy-2015"],
                        "lesson_slug": "dialysis-adequacy",
                        "choices": [
                            ("A", "Continue conservative management indefinitely, since randomized trials showed no benefit from starting dialysis at a higher eGFR", False, "Those trials showed no benefit from starting early by eGFR alone, not that patients with uremic symptoms and acidosis should be managed conservatively indefinitely."),
                            ("B", "Begin planning for dialysis now based on uremic symptoms, persistent acidosis, and low residual urine output, and create vascular access in advance", True, None),
                            ("C", "Wait until the eGFR is below 5 mL/min/1.73 m2 before planning access", False, "Waiting allows uremic complications to progress, and access maturation takes months."),
                            ("D", "Start peritoneal dialysis immediately because the eGFR is 11 mL/min/1.73 m2", False, "Modality choice should follow a deliberate planning conversation, education, and access assessment rather than an eGFR in isolation."),
                        ],
                    },
                ],
            },
            {
                "title": "Hemodialysis Complications",
                "slug": "hemodialysis-complications",
                "description": "Intradialytic hypotension, disequilibrium syndrome, and access-related emergencies.",
                "lessons": [
                    {
                        "title": "Hemodialysis Complications",
                        "lesson_slug": "hemodialysis-complications",
                        "lesson_type": "animation",
                        "summary": "Step animation of intradialytic hypotension, access failure, and circuit emergencies.",
                        "animation_url": f"{ANIMATION_BASE}/hd-complications.json",
                        "duration_seconds": 120,
                        "reference_ids": ["kdoqi-dialysis-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "During the first 90 minutes of a routine hemodialysis session, a 70-year-old with diastolic heart failure becomes lightheaded and diaphoretic, then develops a systolic BP of 78 mmHg. He is given 200 mL saline, which helps for 5 minutes. Ultrafiltration is 3.2 L at 10 mL/kg/hr and the dialysate potassium is 1 mEq/L.",
                        "labs": {"pre_bp": "112/58", "nadir_bp": "78 systolic", "uf_rate": "10 mL/kg/hr", "dialysate_k": "1 mEq/L", "session": "90 min"},
                        "question_text": "Which intervention is most likely to prevent recurrence?",
                        "explanation": "Intradialytic hypotension results from an inadequate compensatory response to ultrafiltration, aggravated by a high ultrafiltration rate, low dialysate sodium, autonomic dysfunction, and cardiac disease. Prevention targets the modifiable drivers: reassess dry weight and volume status, reduce the ultrafiltration rate (rates around 13 mL/kg/hr and above are associated with hypotension), lengthen the session or increase frequency so the same volume is removed over more time, use individualized higher sodium or glucose profiling, and avoid an unnecessarily low dialysate potassium. The immediate response to an established episode is to stop ultrafiltration, reduce the blood pump, and give saline.",
                        "clinical_pearl": "Intradialytic hypotension is a volume-targeting problem: lower the UF rate, lengthen or add sessions, and raise dialysate sodium.",
                        "reference_ids": ["kdoqi-dialysis-2015"],
                        "lesson_slug": "hemodialysis-complications",
                        "choices": [
                            ("A", "Stop ultrafiltration, reduce the blood pump rate, give saline, then reassess dry weight and lower the ultrafiltration rate with longer or more frequent sessions", True, None),
                            ("B", "Increase the ultrafiltration rate to complete the prescribed fluid removal faster", False, "Accelerating ultrafiltration is the direct cause of the hypotension and will make it worse."),
                            ("C", "Lower the dialysate potassium from 1 mEq/L to 0.5 mEq/L to improve hemodynamic stability", False, "A very low dialysate potassium predisposes to hypotension and arrhythmia; raising dialysate potassium is sometimes used to help."),
                            ("D", "Reduce the treatment time to 2 hours to limit intradialytic stress", False, "Shortening the session forces the same volume removal into less time and raises the ultrafiltration rate, worsening hypotension."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A patient on high-flux hemodialysis presents 4 hours after a session with headache, nausea, myoclonus, and confusion. He had not been dialyzed for 18 months before starting thrice-weekly treatment.",
                        "labs": {"time_after_dialysis": "4 h", "history": "long interdialytic gap", "dialyzer": "high flux"},
                        "question_text": "What is the most likely diagnosis and correct management of this post-dialysis neurologic deterioration?",
                        "explanation": "Dysequilibrium syndrome is neurologic deterioration occurring during or shortly after a first or unusually intense dialysis session, most often after a long interdialytic interval in a patient with a high urea burden. Urea removal from the blood faster than from the brain creates an osmotic gradient that draws water into the brain, causing cerebral edema; rapid urea removal with a high-flux dialyzer adds to the risk. Management is to stop or reduce the session, rehydrate carefully, and give hypertonic saline or mannitol to restore the osmotic gradient, then resume dialysis at a lower intensity with a longer, gentler schedule.",
                        "clinical_pearl": "Headache, myoclonus, and confusion after the first intense session = dialysis disequilibrium: stop dialysis, rehydrate, and give hypertonic saline or mannitol.",
                        "reference_ids": ["kdoqi-dialysis-2015"],
                        "lesson_slug": "hemodialysis-complications",
                        "choices": [
                            ("A", "Antibacterial therapy for dialysis-related infection", False, "The timing after the first intensive session with neurologic signs is classic for disequilibrium syndrome, not infection."),
                            ("B", "Stop or shorten the session, rehydrate, and give hypertonic saline or mannitol, then resume a gentler schedule", True, None),
                            ("C", "Increase the blood flow rate and continue the same prescription to clear urea faster", False, "Faster urea removal worsens the cerebral edema driving disequilibrium syndrome."),
                            ("D", "Switch immediately to continuous kidney replacement therapy in the intensive care unit", False, "The syndrome is managed with cessation, rehydration, and osmotherapy; ICU CRRT is not the primary treatment."),
                        ],
                    },
                ],
            },
            {
                "title": "Vascular Access",
                "slug": "vascular-access",
                "description": "Arteriovenous fistulas, grafts, and access dysfunction.",
                "lessons": [
                    {
                        "title": "Vascular Access",
                        "lesson_slug": "vascular-access",
                        "lesson_type": "article",
                        "summary": "Physical examination findings, stenosis, and thrombosis in fistulas and grafts.",
                        "content_md": (
                            "# Vascular access for hemodialysis\n\n"
                            "## Options\n"
                            "- Native arteriovenous fistula: autogenous, lowest infection and thrombosis rates, requires "
                            "maturation time (6 weeks or more) and appropriate vessels\n"
                            "- Arteriovenous graft: faster to use, but higher infection and thrombosis rates\n"
                            "- Central venous catheter: for urgent dialysis or when no other access is feasible; highest "
                            "infection and thrombosis risk and lowest patency\n\n"
                            "## Physical examination\n"
                            "- Thrill: palpable, indicates flowing blood and patency\n"
                            "- Bruit: audible turbulent flow; a harsh, high-pitched bruit suggests a stenosis\n"
                            "- A normal, diffusely soft access without a thrill is thrombosed\n"
                            "- A diminished thrill with a high-pitched bruit indicates a flow-limiting stenosis at the "
                            "arterial anastomosis, or outflow stenosis in a graft\n\n"
                            "## Intervention\n"
                            "Refer early for angiographic evaluation when the bruit becomes harsh, when flow falls, when "
                            "adequacy drops, or when dialysis cannot achieve the needed blood flow. Angioplasty treats "
                            "stenosis; thrombectomy, thrombectomy with angioplasty, or a jump graft treats occlusion."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["kdoqi-dialysis-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 58-year-old on in-center hemodialysis has a radiocephalic fistula. Two weeks ago a thrill was present throughout. Now the dialysis nurse notes the thrill is faint and only felt in the forearm, and a continuous high-pitched bruit is audible. The delivered Kt/V has fallen from 1.35 to 1.05, and two sessions ended early for inadequate flow.",
                        "labs": {"ktv_previous": "1.35", "ktv_current": "1.05", "bruit": "high pitched", "thrill": "faint, proximal only"},
                        "question_text": "What is the most likely diagnosis and next step?",
                        "explanation": "A fistula that previously had a diffuse thrill and now has a weak thrill confined proximally, with a high-pitched continuous bruit, falling Kt/V, and repeated sessions lost to inadequate flow, indicates a flow-limiting stenosis causing access recirculation. Venous outflow stenosis in a native fistula typically occurs near the anastomosis and presents as declining adequacy. The next step is referral for angiographic evaluation and angioplasty, ideally before complete thrombosis, because once thrombosed, patency falls and a jump graft or new access may be required.",
                        "clinical_pearl": "Faint localized thrill plus a high-pitched bruit plus falling Kt/V equals outflow stenosis: angioplasty early, before thrombosis.",
                        "reference_ids": ["kdoqi-dialysis-2015"],
                        "lesson_slug": "vascular-access",
                        "choices": [
                            ("A", "Increase the prescribed blood flow rate to compensate for the loss of access flow", False, "The access itself is stenotic; raising the prescription will not overcome the lesion and will cause more sessions to end early."),
                            ("B", "Refer for angiographic assessment and angioplasty before thrombosis occurs", True, None),
                            ("C", "Repuncture more proximally and continue the current prescription for 4 weeks", False, "Repuncturing more proximally does not treat the outflow lesion, and the adequacy decline needs intervention now."),
                            ("D", "Exchange the catheter for a new tunneled dialysis catheter", False, "The fistula is failing but not thrombosed; angioplasty preserves the functioning native access."),
                        ],
                    },
                ],
            },
            {
                "title": "Peritoneal Dialysis",
                "slug": "peritoneal-dialysis",
                "description": "PD principles, adequacy, and peritonitis management.",
                "lessons": [
                    {
                        "title": "Peritoneal Dialysis",
                        "lesson_slug": "peritoneal-dialysis",
                        "lesson_type": "article",
                        "summary": "PD physiology, modality advantages, adequacy measures, and peritonitis treatment.",
                        "content_md": (
                            "# Peritoneal dialysis\n\n"
                            "## Principles\n"
                            "Dialysis occurs across the peritoneal membrane using dialysate instilled into the peritoneal "
                            "cavity. Solute transport is by diffusion and fluid is removed by the osmotic gradient (glucose, "
                            "or icodextrin for long dwells) plus net ultrafiltration. The main clearance pathways are "
                            "diffusive transport (about 80%) and convective transport via residual peritoneal membrane "
                            "hydraulic conductance (about 20%).\n\n"
                            "## Advantages\n"
                            "Home based, better preservation of residual function, better early survival and cardiovascular "
                            "outcomes, no vascular access or anticoagulation, and no dietary potassium or fluid restriction. "
                            "Disadvantages are peritonitis, exit-site infection, protein loss, glucose load, weight gain, "
                            "and hernia risk.\n\n"
                            "## Adequacy\n"
                            "Assess with weekly Kt/V (peritoneal and total) and residual renal function. Targets are at "
                            "least 1.7 weekly Kt/V and 50 L/week ultrafiltration in CAPD, with at least one long dwell using "
                            "icodextrin. Adjust by increasing dwell time, glucose or icodextrin concentration, or the number "
                            "of exchanges.\n\n"
                            "## Peritonitis\n"
                            "Cloudy effluent with a polymorphonuclear cell count above 100/mm3. Obtain effluent Gram stain "
                            "and culture before antibiotics when possible. Treat empirically with intraperitoneal antibiotics "
                            "covering Gram-positive organisms, add Gram-negative coverage for risk factors, and adjust to "
                            "culture results for about 2 weeks. Do not routinely stop PD; remove the catheter only for "
                            "unresponsive or fungal infection, or after recurrent episodes."
                        ),
                        "duration_seconds": 270,
                        "reference_ids": ["kdoqi-dialysis-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 55-year-old on continuous ambulatory peritoneal dialysis presents with abdominal pain and cloudy effluent. The effluent white cell count shows 85% neutrophils with 320 cells/mm3, and a Gram stain is negative. She is afebrile.",
                        "labs": {"pmn_pct": "85%", "wbc": "320 cells/mm3", "gram_stain": "negative", "temp": "36.8 C"},
                        "question_text": "What is the most appropriate next step for this peritoneal dialysis patient with peritonitis?",
                        "explanation": "Abdominal pain with cloudy effluent and a neutrophil count above 100 cells/mm3 meets diagnostic criteria for peritonitis even when the Gram stain is negative and the patient is afebrile, because Gram stain sensitivity is limited. Management is to obtain an effluent culture, then start empiric intraperitoneal antibiotics covering Gram-positive organisms, adding Gram-negative coverage when risk factors such as constipation, diarrhea, or immunosuppression are present, with later adjustment to culture and sensitivity results for a total of about 2 weeks. Peritoneal dialysis should not be routinely stopped, because continued drainage helps resolve the infection.",
                        "clinical_pearl": "PMN above 100 cells/mm3 plus cloudy effluent equals peritonitis: culture first, then intraperitoneal antibiotics, and keep the catheter in place.",
                        "reference_ids": ["kdoqi-dialysis-2015"],
                        "lesson_slug": "peritoneal-dialysis",
                        "choices": [
                            ("A", "Repeat the peritoneal fluid cell count in 1 week before treating, since she is afebrile", False, "The neutrophil criterion is diagnostic; waiting risks rapid progression of infection and technique failure."),
                            ("B", "Obtain an effluent culture and start empiric intraperitoneal antibiotics covering Gram-positive organisms, adjusting to culture results for about 2 weeks", True, None),
                            ("C", "Remove the peritoneal catheter immediately and start intravenous antibiotics", False, "Immediate catheter removal is reserved for fungal peritonitis, refractory infection, or repeated episodes."),
                            ("D", "Increase the glucose concentration of the dialysate to sterilize the peritoneum", False, "Hypertonic glucose has no antimicrobial role and would worsen the osmotic gradient and glucose load."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Tubulointerstitial & Cystic Disorders",
        "slug": "tubulointerstitial-cystic",
        "order_index": 7,
        "description": "Acute and chronic tubulointerstitial nephritis, analgesic nephropathy, renal tubular acidosis patterns, and autosomal dominant polycystic kidney disease.",
        "icon": "BoxIcon",
        "category_slug": "tubulointerstitial-diseases",
        "topics": [
            {
                "title": "Acute Tubulointerstitial Nephritis",
                "slug": "acute-tubulointerstitial-nephritis",
                "description": "Drug-induced interstitial nephritis: recognition, urine findings, and management.",
                "lessons": [
                    {
                        "title": "Acute Tubulointerstitial Nephritis",
                        "lesson_slug": "acute-tubulointerstitial-nephritis",
                        "lesson_type": "animation",
                        "summary": "Step animation of drug-induced interstitial inflammation, urinalysis, and recovery.",
                        "animation_url": f"{ANIMATION_BASE}/tubulointerstitial-cystic.json",
                        "duration_seconds": 110,
                        "image_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/granulomatous-interstitial-nephritis.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/granulomatous-interstitial-nephritis-thumb.webp",
                        "reference_ids": ["kdigo-ckd-2024"],
                    },
                    {
                        "title": "AIN Clinical Management",
                        "lesson_slug": "ain-clinical-management",
                        "lesson_type": "article",
                        "summary": "Drug culprits, diagnostic criteria, role of biopsy, and when to use corticosteroids.",
                        "content_md": (
                            "# Acute tubulointerstitial nephritis\n\n"
                            "## Pattern of injury\n"
                            "An inflammatory infiltrate of the interstitium with tubular injury, most often caused by a drug. "
                            "Classic triad of fever, rash, and eosinophilia is present in only about 10-15% of adults, so a "
                            "normal urinalysis and absence of the triad do not exclude the diagnosis.\n\n"
                            "## Common culprits\n"
                            "- Beta-lactam antibiotics (most common overall)\n"
                            "- NSAIDs, including COX-2 selective agents: later onset, weeks to months, minimal rash and "
                            "eosinophilia, and prominent proteinuria\n"
                            "- Proton pump inhibitors, rifampin, allopurinol, sulfonamides, thiazides, phenytoin, "
                            "indinavir, checkpoint inhibitors\n\n"
                            "## Findings\n"
                            "A rising creatinine, sterile pyuria, white cell casts, mild proteinuria (usually under 1 g/day), "
                            "eosinophiluria, and sometimes a bland urinalysis. Distinguish from acute tubular necrosis by "
                            "urinary eosinophils and white cell casts, and from glomerulonephritis by the absence of marked "
                            "albuminuria, dysmorphic red cells, or red cell casts.\n\n"
                            "## Management\n"
                            "Stop the offending drug; kidney function often recovers partially within days and fully within "
                            "weeks. Biopsy is unnecessary in a classic presentation but indicated with atypical features, no "
                            "improvement after drug withdrawal, severe AKI or dialysis need, or suspected other diagnoses. "
                            "Corticosteroids are used in biopsy-proven AIN or when a severe presentation is likely and the "
                            "drug cannot be stopped; evidence is from observational data, with a trend toward faster renal "
                            "recovery and less dialysis dependence."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-ckd-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 72-year-old with chronic kidney disease is admitted for pneumonia and treated with ampicillin. Five days into therapy, creatinine rises from 1.4 to 3.2 mg/dL. Urinalysis shows 20-30 white cells per high power field with white cell casts, 1+ protein, and no dysmorphic red cells. He has no rash and no fever.",
                        "labs": {"cr_before": "1.4 mg/dL", "cr_now": "3.2 mg/dL", "ua": "sterile pyuria, WBC casts", "drug": "ampicillin"},
                        "question_text": "What is the most likely diagnosis and the immediate step?",
                        "explanation": "A rising creatinine beginning within days of starting a beta-lactam antibiotic, with sterile pyuria and white cell casts, mild proteinuria, and no dysmorphic red cells, is classic for drug-induced acute tubulointerstitial nephritis. The classic fever, rash, and eosinophilia triad is present in only about 10-15% of adults, so its absence does not exclude the diagnosis. The immediate step is to stop the offending drug, which is the single most important intervention and may be sufficient. A urinalysis that is completely bland and a lack of eosinophiluria do not rule it out, and glomerulonephritis is unlikely without albuminuria and dysmorphic red cells.",
                        "clinical_pearl": "AKI starting days after a beta-lactam with sterile pyuria and white cell casts, no rash, is AIN: stop the drug first.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "ain-clinical-management",
                        "choices": [
                            ("A", "Acute tubulointerstitial nephritis from ampicillin; stop the drug immediately and reassess renal function", True, None),
                            ("B", "Acute tubular necrosis from sepsis; continue ampicillin and add fluid challenge", False, "The urinary sediment with white cell casts and the timing after the drug started point to interstitial nephritis, not an ischemic tubular injury with muddy brown casts."),
                            ("C", "Acute glomerulonephritis; obtain a serologic panel and prepare for plasmapheresis", False, "There is only mild proteinuria, no dysmorphic red cells, and no red cell casts, so an active glomerular sediment is absent."),
                            ("D", "Acute interstitial nephritis; continue ampicillin until the creatinine peaks, then stop", False, "Continuing the causative drug worsens injury; the drug must be stopped immediately."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 66-year-old with osteoarthritis and CKD has taken naproxen 500 mg twice daily for 8 months. Over the last 3 weeks he developed edema with 2.5 g/day of proteinuria, a rising creatinine, and a urinalysis with 10-20 white cells per high power field. There is no rash, no eosinophilia, and no fever.",
                        "labs": {"proteinuria": "2.5 g/day", "duration": "8 months of NSAID", "rash": "absent", "eosinophilia": "absent"},
                        "question_text": "Which feature of this presentation is most distinctive of NSAID-associated interstitial nephritis?",
                        "explanation": "NSAID-associated AIN has a distinctly longer latency than antibiotic-associated AIN, often weeks to months of exposure, and it is usually not accompanied by fever, rash, or eosinophilia. Another distinctive feature is prominent proteinuria, occasionally in the nephrotic range, thought to reflect minimal change disease or podocyte injury superimposed on the interstitial inflammation. The practical consequence is that NSAID-associated AIN is frequently missed because the presentation lacks the classic triad and the drug history is not revisited; recognizing the longer latency and the nephrotic-range proteinuria should prompt drug withdrawal and, in atypical or severe cases, biopsy.",
                        "clinical_pearl": "NSAID-AIN: months of exposure, no rash or eosinophilia, and nephrotic-range proteinuria from superimposed podocyte injury.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "ain-clinical-management",
                        "choices": [
                            ("A", "A latency of months without fever, rash, or eosinophilia, with prominent proteinuria", True, None),
                            ("B", "A latency of 3-5 days with fever, rash, and eosinophilia", False, "That is the classic pattern of antibiotic-associated AIN, not the NSAID pattern."),
                            ("C", "Severe hypokalemia with a normal anion gap metabolic acidosis at presentation", False, "Hypokalemic distal RTA can accompany AIN but is not the feature that distinguishes NSAID-associated disease."),
                            ("D", "Fever within 48 hours of the first dose with bacteremia", False, "Fever with bacteremia suggests infection, not a drug hypersensitivity interstitial nephritis."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 76-year-old developed biopsy-proven acute interstitial nephritis after 10 days of piperacillin-tazobactam. Creatinine is 5.8 mg/dL and he requires intermittent hemodialysis. Cultures are negative and there is no evidence of sepsis.",
                        "labs": {"cr": "5.8 mg/dL", "rxrt": "yes", "biopsy": "AIN", "sepsis": "no"},
                        "question_text": "Which treatment is most appropriate for this severe biopsy-proven acute interstitial nephritis?",
                        "explanation": "This is severe, biopsy-proven AIN requiring dialysis, with no ongoing infection to explain the renal failure. The causative drug has been stopped, and corticosteroid therapy is indicated because severe AIN with dialysis dependence or no expected recovery is precisely the group most likely to benefit; observational data suggest faster recovery and less progression to permanent kidney failure. Supportive care includes adequate hydration, avoidance of further nephrotoxins, and dialysis as needed. Plasma exchange and cytotoxic therapy are not indicated for AIN, and the absence of a classic triad does not change the decision once the biopsy confirms the diagnosis.",
                        "clinical_pearl": "Biopsy-proven AIN needing dialysis: stop the drug, give corticosteroids, and support with dialysis. No role for plasmapheresis.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "ain-clinical-management",
                        "choices": [
                            ("A", "Continue piperacillin-tazobactam and add corticosteroids", False, "The causative antibiotic must be stopped; continuing it perpetuates the injury."),
                            ("B", "Start high-dose corticosteroids after stopping the drug, with supportive care and dialysis as needed", True, None),
                            ("C", "Start cyclophosphamide and plasmapheresis as for anti-GBM disease", False, "Those treatments apply to severe anti-GBM glomerulonephritis, not to interstitial nephritis."),
                            ("D", "Observe only, because recovery is expected within 48 hours of drug withdrawal in all cases", False, "In severe AIN requiring dialysis, waiting risks irreversible cortical necrosis-like damage; corticosteroids are indicated."),
                        ],
                    },
                ],
            },
            {
                "title": "Chronic Tubulointerstitial Disease",
                "slug": "chronic-tubulointerstitial-nephritis",
                "description": "Chronic interstitial nephritis, analgesic nephropathy, and chronic tubulointerstitial patterns.",
                "lessons": [
                    {
                        "title": "Chronic Tubulointerstitial Disease",
                        "lesson_slug": "chronic-tubulointerstitial-disease",
                        "lesson_type": "animation",
                        "summary": "Step animation of chronic interstitial fibrosis, tubular atrophy, and declining concentrating ability.",
                        "animation_url": f"{ANIMATION_BASE}/tubulointerstitial-cystic.json",
                        "duration_seconds": 100,
                        "reference_ids": ["kdigo-ckd-2024"],
                    },
                    {
                        "title": "Chronic Tubulointerstitial Nephritis",
                        "lesson_slug": "chronic-tubulointerstitial-nephritis",
                        "lesson_type": "article",
                        "summary": "Causes, imaging, and clinical pattern of chronic tubulointerstitial disease.",
                        "content_md": (
                            "# Chronic tubulointerstitial nephritis\n\n"
                            "## Pattern\n"
                            "Progressive tubulointerstitial fibrosis and tubular atrophy with relatively bland urine: mild "
                            "proteinuria (usually under 1.5 g/day), absent or minimal hematuria, sterile pyuria, and a "
                            "concentrating defect with polyuria and nocturia. Small kidneys with reduced corticomedullary "
                            "differentiation on ultrasound or CT support the diagnosis.\n\n"
                            "## Causes\n"
                            "- Drugs: chronic analgesic (phenacetin, aspirin, NSAID) use, lithium, calcineurin "
                            "inhibitors, some chemotherapeutic agents, and checkpoint inhibitors\n"
                            "- Metabolic: chronic hypercalcemia, hypokalemia, and the consequences of chronic obstruction\n"
                            "- Infection: chronic pyelonephritis with vesicoureteral reflux\n"
                            "- Autoimmune: Sjögren syndrome, systemic lupus, sarcoidosis, IgG4-related disease\n"
                            "- Genetic: medullary cystic disease, nephronophthisis, mitochondrial disorders\n"
                            "- Systemic: sickle cell disease, amyloidosis restricted to the interstitium\n\n"
                            "## Diagnosis\n"
                            "Biopsy is often needed to exclude glomerular and vascular disease. Imaging looks for reflux, "
                            "obstruction, medullary cysts, and stones. Analgesic nephropathy is associated with papillary "
                            "necrosis and calcification on imaging and often a sterile pyuria or hematuria."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["kdigo-ckd-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 70-year-old who has taken combination analgesics daily for 20 years presents with CKD G3b, sterile pyuria, 0.8 g/day proteinuria, and nocturia. Non-contrast CT shows small kidneys with bilateral papillary calcifications and irregular calyces.",
                        "labs": {"egfr": "34 mL/min/1.73m2", "proteinuria": "0.8 g/day", "ct": "papillary calcification", "ua": "sterile pyuria"},
                        "question_text": "What is the most likely diagnosis?",
                        "explanation": "The combination of decades of analgesic exposure, chronic tubulointerstitial kidney disease with mild proteinuria and sterile pyuria, and imaging showing papillary necrosis with calcification is characteristic of analgesic nephropathy. The chronic tubulointerstitial pattern differs from glomerular disease in that proteinuria is modest and the sediment is not active, and imaging evidence of papillary injury confirms the cause. Management includes stopping the analgesics, optimizing blood pressure, avoiding further nephrotoxins, and treating obstruction or infection if present; there is no specific therapy to reverse established fibrosis.",
                        "clinical_pearl": "Analgesic nephropathy: combination analgesic use, sterile pyuria, modest proteinuria, and papillary calcification on non-contrast CT.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "chronic-tubulointerstitial-nephritis",
                        "choices": [
                            ("A", "Analgesic nephropathy (chronic tubulointerstitial nephritis from analgesic injury)", True, None),
                            ("B", "IgA nephropathy", False, "IgA nephropathy shows glomerular hematuria with dysmorphic red cells, which is absent here."),
                            ("C", "Membranous nephropathy", False, "Membranous nephropathy causes nephrotic-range proteinuria, not modest proteinuria with papillary calcifications."),
                            ("D", "Chronic pyelonephritis from vesicoureteral reflux", False, "Reflux nephropathy causes clubbing and calyceal scarring related to reflux, not the papillary calcification pattern of analgesic injury."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 40-year-old has CKD G3a with polyuria and nocturia, concentrating defect on water deprivation, 0.6 g/day proteinuria, and no hematuria. Potassium is 2.8 mEq/L, bicarbonate 14 mEq/L, and urine pH is 5.6 despite systemic acidosis. Serum calcium is 9.8 mg/dL and PTH is normal.",
                        "labs": {"k": "2.8 mEq/L", "hco3": "14 mEq/L", "urine_ph": "5.6", "ca": "9.8 mg/dL", "pth": "normal"},
                        "question_text": "Which diagnosis best unifies these findings?",
                        "explanation": "A normal anion gap acidosis (bicarbonate 14) with hypokalemia and an inappropriately alkaline urine (pH 5.6 despite systemic acidosis, so the distal nephron cannot acidify) indicates distal (type 1) renal tubular acidosis. The concentrating defect, polyuria, and nocturia localize the problem to the tubulointerstitial region rather than the glomeruli, and the normal calcium with normal PTH argues against hypercalcemic nephropathy. Most often distal RTA in this setting is autoimmune (Sjögren syndrome, rheumatoid arthritis) or drug induced; confirming a normal anion gap and checking for Sjögren serologies, plus urinary anion gap to confirm low ammonium excretion, completes the evaluation.",
                        "clinical_pearl": "Urine pH above 5.5 in a patient with a normal anion gap acidosis and hypokalemia equals distal (type 1) RTA.",
                        "reference_ids": ["statpearls-rta", "ajkd-rta-core-2025"],
                        "lesson_slug": "chronic-tubulointerstitial-disease",
                        "choices": [
                            ("A", "Distal (type 1) renal tubular acidosis from tubulointerstitial disease, most often autoimmune or drug induced", True, None),
                            ("B", "Proximal (type 2) renal tubular acidosis", False, "In proximal RTA the distal acidification is intact, so urine pH falls below 5.5 once serum bicarbonate is depleted; here urine pH remains inappropriately high."),
                            ("C", "Type 4 renal tubular acidosis from hyporeninemic hypoaldosteronism", False, "Type 4 RTA causes hyperkalemia, not hypokalemia, and typically occurs in diabetic or obstructive uropathy."),
                            ("D", "Diabetic nephropathy from hyperfiltration", False, "Diabetic nephropathy produces albumin-predominant proteinuria and a progressive eGFR decline, not a urine pH of 5.6 with a concentrating defect."),
                        ],
                    },
                ],
            },
            {
                "title": "Autosomal Dominant Polycystic Kidney Disease",
                "slug": "adpkd",
                "description": "Diagnosis by age-based imaging criteria, natural history, and disease-modifying therapy.",
                "lessons": [
                    {
                        "title": "ADPKD Diagnosis and Management",
                        "lesson_slug": "adpkd-diagnosis-and-management",
                        "lesson_type": "article",
                        "summary": "Age-based ultrasound criteria, extrarenal findings, renal volume, blood pressure, and tolvaptan.",
                        "content_md": (
                            "# ADPKD\n\n"
                            "## Genetics\n"
                            "Autosomal dominant polycystic kidney disease is caused most often by PKD1 (about 85%) and PKD2 "
                            "(about 15%). PKD1 disease progresses faster, with kidney failure typically in the fourth decade "
                            "compared with the fifth decade for PKD2.\n\n"
                            "## Diagnosis\n"
                            "Age-based ultrasound criteria for a person without a family history:\n"
                            "- 15-39 years: 3 or more cysts in total across both kidneys\n"
                            "- 40-59 years: 2 or more cysts in each kidney\n"
                            "- 60 years or older: 4 or more cysts in each kidney\n"
                            "Height-adjusted criteria exist for shorter adults. MRI is more sensitive for equivocal cases. In a "
                            "known PKD1 or PKD2 carrier, the diagnosis is clinical, and imaging is not required.\n\n"
                            "## Extrarenal findings\n"
                            "Hepatic cysts (the most common extrarenal finding), cysts in the pancreas and seminal vesicles, "
                            "cardiac valvular abnormalities, intracranial berry aneurysms (5-10%), and hernias.\n\n"
                            "## Management\n"
                            "- Blood pressure control, with ACE inhibitor or ARB first-line, reduces total kidney volume "
                            "growth and proteinuria\n"
                            "- Restrict sodium, avoid NSAIDs, treat UTIs promptly, avoid smoking and estrogen exposure\n"
                            "- Tolvaptan slows eGFR decline by about 30-35% in the TEMPO trial; it requires polyuria "
                            "(eGFR above 25 mL/min/1.73 m2), and liver function testing at baseline and 2 and 4 weeks, "
                            "then every 3 months. Risks are thirst, polyuria, and hepatotoxicity. Avoid in pregnancy, "
                            "significant liver disease, and inability to manage polyuria\n"
                            "- Nephrectomy is reserved for pain, infection, hemorrhage, stones, or malignancy suspicion\n"
                            "- Screen at-risk relatives for blood pressure control and offer genetic counselling"
                        ),
                        "duration_seconds": 270,
                        "image_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/adpkd-progression.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/adpkd-progression-thumb.webp",
                        "reference_ids": ["kdigo-adpkd-2025", "kdigo-ckd-2024"],
                    },
                    {
                        "title": "Tuberous Sclerosis: Renal Angiomyolipoma",
                        "lesson_slug": "tuberous-sclerosis-renal-angiomyolipoma",
                        "lesson_type": "article",
                        "summary": "Renal angiomyolipoma, skin findings, and surveillance in tuberous sclerosis complex.",
                        "content_md": "Tuberous sclerosis complex is an autosomal dominant disorder of TSC1 (hamartin) or TSC2 (tuberin) that causes hamartomas in multiple organs.\n\nKidney: angiomyolipomas occur in up to 80 percent of adults with TSC, and renal cysts are also common. Angiomyolipoma is a triphasic tumor of vessels, smooth muscle, and fat, so it is fat containing on CT and prone to retroperitoneal hemorrhage. Bleeding risk rises with size above 4 cm, and growth is faster in children and adults than in children alone.\n\nExtrarenal clues: hypomelanotic ash-leaf macules, shagreen patch, facial angiofibromas, periungual fibromas, cortical tubers, and subependymal giant cell astrocytoma. Cardiac rhabdomyomas are common in infancy.\n\nManagement: monitor with periodic imaging, control blood pressure and lipids, treat epilepsy, and consider embolization or nephron-sparing resection for large or symptomatic angiomyolipomas. mTOR inhibitors such as everolimus reduce angiomyolipoma size in patients who are not candidates for surgery.\n\nAsk about family history, seizures, and skin findings in any young patient with unexplained renal masses or hematuria.",
                        "duration_seconds": 90,
                        "image_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/tuberous-sclerosis-angiomyolipoma.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/tubulointerstitial-cystic/tuberous-sclerosis-angiomyolipoma-thumb.webp",
                        "reference_ids": ["kdigo-adpkd-2025", "abim-nephrology-blueprint-2026"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 35-year-old with an affected father and no prior diagnosis undergoes renal ultrasound for hematuria evaluation. The kidneys measure 16.5 and 16.0 cm with multiple cysts in both. Blood pressure is 142/92 mmHg and eGFR is 84 mL/min/1.73 m2.",
                        "labs": {"kidney_cm": "16.5 and 16.0", "bp": "142/92", "egfr": "84 mL/min/1.73m2", "age": "35"},
                        "question_text": "What is the most appropriate next step in managing this newly diagnosed ADPKD?",
                        "explanation": "In a 35-year-old, the presence of 3 or more renal cysts in total across both kidneys on ultrasound is diagnostic of ADPKD when there is no family history, and imaging findings are consistent when a compatible family history exists. Management at this stage is risk-factor modification rather than cyst-directed therapy: tight blood pressure control with an ACE inhibitor or ARB first, which slows total kidney volume growth, sodium restriction, NSAID avoidance, and prompt treatment of urinary infection. Tolvaptan is not yet indicated because eGFR is normal and he is not polyuric; it is reserved for patients with eGFR above 25 mL/min/1.73 m2 who are already polyuric. Screening for intracranial aneurysm is reserved for family history of aneurysm or subarachnoid hemorrhage, prior rupture, high-risk occupations, or pre-transplant planning.",
                        "clinical_pearl": "In ADPKD, treat blood pressure aggressively with RAAS blockade early; aneurysm screening is reserved for defined high-risk groups.",
                        "reference_ids": ["kdigo-adpkd-2025"],
                        "lesson_slug": "adpkd-diagnosis-and-management",
                        "choices": [
                            ("A", "Start an ACE inhibitor, restrict sodium, avoid NSAIDs, and offer genetic counselling plus family screening; reserve aneurysm imaging for high-risk patients", True, None),
                            ("B", "Start tolvaptan immediately to prevent cyst growth", False, "Tolvaptan is indicated for patients who are already polyuric with eGFR above 25 mL/min/1.73 m2; a normokalemic patient with normal eGFR is not a candidate."),
                            ("C", "Perform magnetic resonance angiography of the brain in every patient at diagnosis", False, "Routine intracranial aneurysm screening is not recommended in all ADPKD patients; it is limited to family history of aneurysm or subarachnoid hemorrhage, prior rupture, and a few high-risk scenarios."),
                            ("D", "Perform bilateral nephrectomy to prevent kidney failure", False, "Prophylactic nephrectomy is not indicated; nephrectomy is reserved for intractable pain, infection, hemorrhage, or malignancy suspicion."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 48-year-old with ADPKD has eGFR 38 mL/min/1.73 m2, urine output 3.5 L/day, blood pressure 148/88 on amlodipine, and persistent flank pain. Liver enzymes are normal. He asks about a disease-modifying drug.",
                        "labs": {"egfr": "38 mL/min/1.73m2", "uo": "3.5 L/day", "alt": "normal", "bp": "148/88"},
                        "question_text": "Which statement about tolvaptan is most accurate for this patient?",
                        "explanation": "Tolvaptan is a vasopressin V2 receptor antagonist that reduces cAMP-mediated cyst growth and slowed eGFR decline by roughly 30-35% over 3-5 years in the TEMPO trial, and it is recommended for adults at risk of rapidly progressive disease. It requires the ability to drink and urinate in response to thirst, so a polyuric patient with eGFR above 25 mL/min/1.73 m2 is a typical candidate, and this patient meets those criteria. It requires ALT, AST, and bilirubin at baseline and again at 2 and 4 weeks, then every 3 months, because of idiosyncratic hepatotoxicity. Adverse effects include thirst, polyuria, and volume depletion, so his blood pressure medication should be reduced in parallel.",
                        "clinical_pearl": "Tolvaptan: polyuric ADPKD with eGFR above 25; never start without a normal baseline LFT and a 2- and 4-week recheck, then every 3 months.",
                        "reference_ids": ["kdigo-adpkd-2025"],
                        "lesson_slug": "adpkd-diagnosis-and-management",
                        "choices": [
                            ("A", "Tolvaptan is a reasonable option because he is polyuric with eGFR above 25 mL/min/1.73 m2, but requires liver function monitoring at baseline, 2 and 4 weeks, and then every 3 months, and his antihypertensives may need reduction", True, None),
                            ("B", "Tolvaptan should be avoided because any patient with eGFR below 60 cannot receive it", False, "The renal threshold is eGFR above 25 mL/min/1.73 m2, not 60; his eGFR of 38 qualifies."),
                            ("C", "Tolvaptan requires monitoring of drug levels and should never be used with a thiazide diuretic", False, "Tolvaptan has no routine therapeutic drug level requirement; the key requirement is liver function monitoring and the ability to handle polyuria."),
                            ("D", "Tolvaptan is contraindicated in patients with normal liver enzymes but persistent flank pain", False, "Flank pain is an indication for cyst intervention, not a contraindication; the main exclusions are inability to handle polyuria, significant liver disease, and pregnancy."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Glomerular & Vascular Disorders",
        "slug": "glomerular-vascular",
        "order_index": 8,
        "description": "Nephrotic syndrome, nephritic syndrome and rapidly progressive glomerulonephritis, IgA nephropathy, ANCA vasculitis, and thrombotic microangiopathies.",
        "icon": "FilterIcon",
        "category_slug": "glomerular-diseases",
        "topics": [
            {
                "title": "Nephrotic Syndrome",
                "slug": "nephrotic-syndrome",
                "description": "Minimal change disease, FSGS, membranous nephropathy, and syndrome complications.",
                "lessons": [
                    {
                        "title": "Nephrotic versus Nephritic",
                        "lesson_slug": "nephrotic-versus-nephritic",
                        "lesson_type": "animation",
                        "summary": "Step animation contrasting nephrotic and nephritic presentations at the glomerulus.",
                        "animation_url": f"{ANIMATION_BASE}/nephrotic-nephritic.json",
                        "duration_seconds": 110,
                        "image_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/light-chains-immunoglobulin.svg",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/light-chains-immunoglobulin.svg",
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/lightchain-nephropathy.html",
                        "reference_ids": ["kdigo-glomerular-2021"],
                    },
                    {
                        "title": "Nephrotic Syndrome Management",
                        "lesson_slug": "nephrotic-syndrome-management",
                        "lesson_type": "article",
                        "summary": "Definition, complications, and treatment principles for nephrotic syndrome across causes.",
                        "content_md": (
                            "# Nephrotic syndrome\n\n"
                            "## Definition\n"
                            "Adults: proteinuria above 3.5 g/day plus hypoalbuminemia (below 3.0 g/dL), with edema. "
                            "Children: proteinuria above 40 mg/m2/hour or a urine protein-to-creatinine ratio above 2 g/g, "
                            "with hypoalbuminemia. The urinalysis shows 3-4+ protein, lipiduria, and oval fat bodies.\n\n"
                            "## Complications\n"
                            "- Venous thromboembolism: risk is highest with membranous nephropathy and albumin below 2.5 g/dL; "
                            "anticoagulation is considered in selected high-risk patients\n"
                            "- Infection: loss of immunoglobulins, particularly IgG, and of complement in some diseases; "
                            "pneumococcal and other vaccines are important\n"
                            "- Loss of vitamin D-binding protein causing low 25-OH vitamin D and hypocalcemia\n"
                            "- Hypoalbuminemia-driven edema, hyperlipidemia, and loss of antithrombin III\n\n"
                            "## Causes\n"
                            "Minimal change disease (most common in children, and the cause of about 90% of childhood cases), "
                            "focal segmental glomerulosclerosis, membranous nephropathy (most common in adults in developed "
                            "countries), and secondary causes: diabetes, lupus, amyloidosis, infection such as hepatitis B, "
                            "HIV, and drugs.\n\n"
                            "## Treatment principles\n"
                            "Treat the cause: corticosteroids for minimal change disease, rituximab or cyclophosphamide plus "
                            "glucocorticoids for primary membranous nephropathy or steroid-resistant FSGS, and disease-specific "
                            "therapy for secondary causes. Supportive therapy includes sodium restriction, moderate protein "
                            "intake, ACE inhibitor or ARB for proteinuria, and statin therapy for hyperlipidemia."
                        ),
                        "duration_seconds": 270,
                        "image_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/renal-biopsy-al-vs-lcdd.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/renal-biopsy-al-vs-lcdd-thumb.webp",
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/fsgs-advanced.html",
                        "reference_ids": ["kdigo-glomerular-2021", "kdigo-nephrotic-peds-2025"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "medium",
                        "case_text": "A 7-year-old boy has periorbital edema, frothy urine, and 4+ proteinuria. Serum albumin is 2.0 g/dL, blood pressure is normal, and there is no hematuria. Serum creatinine is normal.",
                        "labs": {"albumin": "2.0 g/dL", "ua": "4+ protein, no blood", "bp": "normal", "age": "7"},
                        "question_text": "What is the most appropriate initial management of this child with typical nephrotic syndrome?",
                        "explanation": "A child with periorbital edema, heavy proteinuria, hypoalbuminemia, normal blood pressure, and a bland sediment has nephrotic syndrome, and the most likely cause is minimal change disease, which accounts for about 80-90% of childhood cases. Initial management is empiric corticosteroids, which induce remission in about 80-90% of children, and kidney biopsy is not indicated at presentation unless there are atypical features such as hematuria, hypertension, low complement, or a slow response to steroids. Immunizations, particularly pneumococcal vaccine, and vitamin D repletion should be addressed, and families counseled about relapse.",
                        "clinical_pearl": "A typical child with nephrotic syndrome gets empiric steroids and no biopsy; atypical features or steroid resistance are the biopsy triggers.",
                        "reference_ids": ["kdigo-nephrotic-peds-2025", "kdigo-glomerular-2021"],
                        "lesson_slug": "nephrotic-syndrome-management",
                        "choices": [
                            ("A", "Begin empiric corticosteroid therapy without kidney biopsy", True, None),
                            ("B", "Perform a kidney biopsy immediately before any treatment", False, "In a typical child with nephrotic syndrome, biopsy is deferred because minimal change disease is highly likely and highly steroid responsive."),
                            ("C", "Start cyclosporine because childhood nephrotic syndrome is usually steroid resistant", False, "Most childhood nephrotic syndrome is steroid responsive; cyclosporine is used for steroid dependence, dependence, or resistance."),
                            ("D", "Begin angiotensin receptor blockade only and defer immunosuppression", False, "ACEi or ARB is appropriate adjunctive therapy for proteinuria, but the underlying disease in a typical child is treated with corticosteroids."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 62-year-old presents with nephrotic syndrome: 6 g/day proteinuria, albumin 1.9 g/dL, and worsening back pain. Serum creatinine is normal, ANA and hepatitis serologies are negative, and complement levels are normal. Anti-PLA2R antibody is strongly positive. He has no history of thrombosis.",
                        "labs": {"proteinuria": "6 g/day", "albumin": "1.9 g/dL", "anti_pla2r": "strongly positive", "cr": "normal", "platelets": "310 K/uL"},
                        "question_text": "Which is the most appropriate treatment plan?",
                        "explanation": "Strong anti-PLA2R positivity with normal complement, negative serologies, and nephrotic syndrome identifies primary membranous nephropathy, and the age and back pain raise concern for an associated malignancy. Current KDIGO-directed care in primary membranous nephropathy uses rituximab, or alternatively cyclophosphamide with glucocorticoids, with ACE inhibitor or ARB for proteinuria and supportive therapy; older regimens of alternating cyclosporine and dexamethasone are less favored. Because membranous nephropathy carries the highest thromboembolic risk of the nephrotic causes, assessment of venous thrombosis risk is important; anticoagulation is considered when the risk is highest, particularly with albumin below 2.0-2.5 g/dL, and must be balanced against bleeding risk.",
                        "clinical_pearl": "Anti-PLA2R positivity with normal complement equals primary membranous nephropathy: treat with rituximab or cyclophosphamide plus steroids, and think about malignancy and VTE risk.",
                        "reference_ids": ["kdigo-glomerular-2021"],
                        "lesson_slug": "nephrotic-syndrome-management",
                        "choices": [
                            ("A", "Treat the membranous nephropathy with rituximab or cyclophosphamide plus glucocorticoids, add ACEi/ARB, and assess thrombotic and malignancy risk", True, None),
                            ("B", "Optimize blood pressure and follow without immunosuppression, since membranous nephropathy is often self-limited", False, "Although spontaneous remission occurs, persistent nephrotic-range proteinuria with low albumin in an older adult warrants immunosuppression rather than observation alone."),
                            ("C", "Start hemodialysis to control proteinuria", False, "Dialysis is not a treatment for proteinuria; this patient has normal renal function."),
                            ("D", "Treat with long-term corticosteroids alone at high dose", False, "Monotherapy with glucocorticoids is ineffective in membranous nephropathy and exposes the patient to significant toxicity."),
                        ],
                    },
                ],
            },
            {
                "title": "Nephritic Syndrome and RPGN",
                "slug": "nephritic-rpgn",
                "description": "Nephritic presentations, serologic classification, and treatment of rapidly progressive glomerulonephritis.",
                "lessons": [
                    {
                        "title": "Nephritic Syndrome and RPGN",
                        "lesson_slug": "nephritic-syndrome-and-rpgn",
                        "lesson_type": "article",
                        "summary": "Nephritic features, the three serologic types of RPGN, and treatment by type.",
                        "content_md": (
                            "# Nephritic syndrome and RPGN\n\n"
                            "## Nephritic features\n"
                            "Hematuria with dysmorphic red cells and red cell casts, proteinuria that is often subnephrotic, "
                            "hypertension, azotemia, and edema with periorbital emphasis.\n\n"
                            "## Three serologic types of rapidly progressive glomerulonephritis\n"
                            "1. Type I, anti-GBM: linear IgG on immunofluorescence, with or without anti-GBM antibodies in "
                            "serum; Goodpasture syndrome when there is pulmonary hemorrhage\n"
                            "2. Type II, immune complex: granular deposits; lupus nephritis, IgA nephropathy, "
                            "post-infectious glomerulonephritis, and cryoglobulinemia\n"
                            "3. Type III, pauci-immune: little or no immunoglobulin on immunofluorescence; usually ANCA "
                            "associated vasculitis or anti-GBM negative ANCA disease\n\n"
                            "## Evaluation\n"
                            "Serology: ANCA (PR3 and MPO), anti-GBM, ANA, dsDNA, complement C3 and C4, hepatitis B and C, "
                            "HIV, ASO titer, and cryoglobulin as indicated. Kidney biopsy is required in almost all cases of "
                            "RPGN to define the type and guide therapy.\n\n"
                            "## Treatment\n"
                            "- Anti-GBM disease: plasma exchange, corticosteroids, and cyclophosphamide; prognosis is best when "
                            "treatment begins before dialysis dependence\n"
                            "- Pauci-immune ANCA vasculitis: glucocorticoids plus rituximab or cyclophosphamide for induction, "
                            "then maintenance with rituximab, azathioprine, or methotrexate; plasma exchange for severe renal "
                            "disease (creatinine above about 3.4 mg/dL, rapidly rising, or dialysis dependent) or "
                            "diffuse alveolar hemorrhage\n"
                            "- Immune complex disease: treat the underlying cause, with steroids and mycophenolate or "
                            "cyclophosphamide for lupus nephritis"
                        ),
                        "duration_seconds": 270,
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/lupus-nephritis.html",
                        "reference_ids": ["kdigo-anca-aav-2024", "kdigo-glomerular-2021"],
                    },
                    {
                        "title": "HIV-Associated Nephropathy: Biopsy Patterns",
                        "lesson_slug": "hiv-associated-nephropathy-biopsy-patterns",
                        "lesson_type": "article",
                        "summary": "Light microscopy, immunofluorescence, and electron microscopy patterns of HIV kidney disease.",
                        "content_md": "HIV-associated kidney disease has three distinct patterns that must be separated on biopsy.\n\nHIV-associated nephropathy (HIVAN): collapsing focal segmental glomerulosclerosis with podocyte proliferation and microcystic tubular dilation. Immunofluorescence is negative or shows only nonspecific trapped immunoglobulin, and electron microscopy shows tubuloreticular inclusions. It occurs most often in patients of African ancestry with low CD4 counts, untreated HIV, and often normal or only mildly reduced renal function with a rapid decline.\n\nHIV immune complex kidney disease (HIVICK): immune complex deposition, most often IgM and C3 with a full-house pattern, resembling lupus nephritis or post-infectious glomerulonephritis.\n\ncART nephrotoxicity: tenofovir disoproxil causes proximal tubular injury with a Fanconi pattern, phosphate wasting, and low molecular weight proteinuria, while boosted protease inhibitors and cobicistat raise the risk of crystal nephropathy and hyperuricemia.\n\nPractical points: start antiretroviral therapy in HIVAN, which often stabilizes kidney function, and use tenofovir alafenamide or an alternative agent when cART nephrotoxicity is present.",
                        "duration_seconds": 120,
                        "image_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/hiv-associated-nephropathy.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/hiv-associated-nephropathy-thumb.webp",
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/glomerular-vascular/hiv-associated-nephropathy.html",
                        "reference_ids": ["kdigo-glomerular-2021", "abim-nephrology-blueprint-2026"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 62-year-old presents with 3 weeks of hematuria with red cell casts, 2.5 g/day proteinuria, and a creatinine that rose from 1.0 to 3.8 mg/dL in three weeks. He has had no infection and no lung symptoms.",
                        "labs": {"cr": "1.0 to 3.8 mg/dL in 3 weeks", "ua": "RBC casts", "proteinuria": "2.5 g/day"},
                        "question_text": "Which set of studies is most appropriate as the immediate next step?",
                        "explanation": "A creatinine that more than doubles within three weeks with an active glomerular sediment defines rapidly progressive glomerulonephritis. The immediate workup is serologic: ANCA (PR3 and MPO), anti-GBM antibodies, ANA with dsDNA, complement C3 and C4, hepatitis B and C, HIV, and ASO titer, and kidney biopsy to classify the type. Complement patterns help narrow the differential: normal complement is typical of pauci-immune and anti-GBM disease, low C3 with normal C4 suggests post-infectious disease, and low C3 and C4 suggests lupus or cryoglobulinemia. Waiting for serology before biopsy risks irreversible loss of renal function in a treatable disease.",
                        "clinical_pearl": "RPGN = double the creatinine in under 3 weeks with an active sediment. Order ANCA, anti-GBM, ANA/dsDNA, C3/C4, and get a biopsy promptly.",
                        "reference_ids": ["kdigo-anca-aav-2024", "kdigo-glomerular-2021"],
                        "lesson_slug": "nephritic-syndrome-and-rpgn",
                        "choices": [
                            ("A", "Serologic panel (ANCA, anti-GBM, ANA with dsDNA, C3 and C4, hepatitis serologies) plus kidney biopsy to classify the RPGN type", True, None),
                            ("B", "Renal ultrasound and cystography to exclude obstruction", False, "There is no obstruction with an active glomerular sediment and a rapidly rising creatinine; the priority is serology and biopsy."),
                            ("C", "Empiric antibiotics for presumed post-streptococcal glomerulonephritis", False, "Antibiotics are not the treatment of RPGN; the type must be defined by serology and biopsy before immunosuppression is chosen."),
                            ("D", "Observation with repeat creatinine in 2 weeks to see if the creatinine stabilizes", False, "Delayed evaluation risks irreversible renal failure in anti-GBM and ANCA-associated disease."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 24-year-old man presents with hemoptysis, dyspnea, hemoglobin 7.4 g/dL, hematuria with red cell casts, and creatinine 5.2 mg/dL. He requires intubation. ANCA is negative, ANA is negative, C3 is normal, and serum anti-GBM antibody is 142 IU/mL.",
                        "labs": {"hgb": "7.4 g/dL", "cr": "5.2 mg/dL", "anti_gbm": "142 IU/mL", "anca": "negative", "c3": "normal"},
                        "question_text": "Which treatment is most appropriate for this pulmonary-renal syndrome with circulating anti-GBM antibodies?",
                        "explanation": "Pulmonary hemorrhage plus rapidly progressive glomerulonephritis with high-titer circulating anti-GBM antibodies and negative ANCA is anti-GBM disease (Goodpasture syndrome), the most rapidly destructive of the RPGN types. Treatment is plasma exchange to remove circulating antibodies, high-dose corticosteroids, and cyclophosphamide to suppress new antibody production, initiated immediately; treatment is most effective before the need for dialysis, so a lung-saving indication also mandates treatment even with advanced renal failure. Rituximab is an accepted alternative in some protocols. Failure to remove antibodies and halt production allows crescent formation and irreversible sclerosis within weeks.",
                        "clinical_pearl": "Anti-GBM disease with pulmonary hemorrhage: plasma exchange, steroids, and cyclophosphamide started immediately, even if already on dialysis.",
                        "reference_ids": ["kdigo-anca-aav-2024"],
                        "lesson_slug": "nephritic-syndrome-and-rpgn",
                        "choices": [
                            ("A", "Urgent plasma exchange, corticosteroids, and cyclophosphamide", True, None),
                            ("B", "Rituximab monotherapy with supportive care", False, "Anti-GBM disease requires removal of circulating antibody with plasma exchange plus suppression of new production; rituximab monotherapy is not the standard for this indication."),
                            ("C", "ACE inhibitor and ARB combination to reduce intraglomerular pressure", False, "Dual RAAS blockade causes hyperkalemia and acute kidney injury and does not treat the underlying disease."),
                            ("D", "Watchful waiting until the creatinine stabilizes, since anti-GBM disease often resolves spontaneously", False, "Anti-GBM disease is relentlessly progressive; delaying treatment forfeits renal recovery."),
                        ],
                    },
                ],
            },
            {
                "title": "IgA Nephropathy",
                "slug": "iga-nephropathy",
                "description": "KDIGO 2025 approach to supportive care, risk stratification, and immunosuppression.",
                "lessons": [
                    {
                        "title": "IgA Nephropathy",
                        "lesson_slug": "iga-nephropathy",
                        "lesson_type": "article",
                        "summary": "Diagnosis, supportive care first, risk-based immunosuppression, and post-transplant recurrence.",
                        "content_md": (
                            "# IgA nephropathy\n\n"
                            "## Diagnosis\n"
                            "The most common glomerulonephritis worldwide. Presentation ranges from asymptomatic microscopic "
                            "hematuria to episodic gross hematuria within 1-2 days of an upper respiratory infection "
                            "(synpharyngitic), to nephrotic syndrome or rapidly progressive disease. Biopsy is required for "
                            "diagnosis, showing mesangial IgA-dominant staining on immunofluorescence.\n\n"
                            "## Supportive care first\n"
                            "Optimized supportive care is the foundation of treatment and should be optimized for at least "
                            "3 months before immunosuppression is considered: blood pressure control below 130/80 mmHg, "
                            "renin-angiotensin system blockade with an ACE inhibitor or ARB (which may be combined with a "
                            "sodium-glucose cotransporter 2 inhibitor), sodium restriction, and avoidance of NSAIDs.\n\n"
                            "## When to immunosuppress\n"
                            "Immunosuppression is reserved for patients at risk of progression, generally those with proteinuria "
                            "above about 0.75-1.0 g/day despite optimized supportive care for at least 3 months, and is matched "
                            "to risk. Glucocorticoids are used in selected intermediate-risk patients; 6 months of "
                            "mycophenolate mofetil or cyclophosphamide with glucocorticoids is used in higher-risk patients "
                            "with proteinuria above about 1.0-1.5 g/day, and targeted budesonide or Nefecon is an option in "
                            "selected patients. Complement and other pathway-directed agents are under study.\n\n"
                            "## Prognosis\n"
                            "Recurrence in renal allografts occurs in up to 30-40% of patients and is an important cause of "
                            "late graft loss. IgA nephropathy is the most common primary glomerulonephritis leading to kidney "
                            "failure."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-igan-2025"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 32-year-old has biopsy-proven IgA nephropathy with proteinuria of 1.6 g/day, creatinine 1.1 mg/dL, and blood pressure 138/86 on amlodipine. He has had no ACE inhibitor or ARB and avoids NSAIDs.",
                        "libs": {"proteinuria": "1.6 g/day", "cr": "1.1 mg/dL", "bp": "138/86", "current_rx": "amlodipine only"},
                        "question_text": "What is the most appropriate initial management of this IgA nephropathy with proteinuria of 1.6 g/day?",
                        "explanation": "KDIGO 2025 recommends that all patients with IgA nephropathy at risk of progression first receive optimized supportive care for at least 3 months, with strict blood pressure control, renin-angiotensin system blockade using an ACE inhibitor or ARB, sodium restriction, and avoidance of NSAIDs, before immunosuppression is considered. Immunosuppression is reserved for proteinuria that remains above about 0.75-1.0 g/day despite this optimized care, and is then matched to progression risk. This patient has not had any antiproteinuric therapy, so starting an ACE inhibitor or ARB with blood pressure control and deferring immunosuppression for at least 3 months is the correct sequence, with repeat proteinuria assessment after the supportive-care period.",
                        "clinical_pearl": "IgA nephropathy: optimize supportive care (BP, ACEi/ARB, sodium, no NSAIDs) for at least 3 months before any immunosuppression.",
                        "reference_ids": ["kdigo-igan-2025"],
                        "lesson_slug": "iga-nephropathy",
                        "choices": [
                            ("A", "Start an ACE inhibitor or ARB with blood pressure control and sodium restriction, then reassess proteinuria after at least 3 months of optimized supportive care before considering immunosuppression", True, None),
                            ("B", "Start 6 months of cyclophosphamide and glucocorticoids immediately because proteinuria exceeds 1 g/day", False, "KDIGO requires a trial of optimized supportive care for at least 3 months before immunosuppression, which this patient has not had."),
                            ("C", "Start mycophenolate mofetil monotherapy for 3 years without blood pressure optimization", False, "Immunosuppression without optimized supportive care is premature, and mycophenolate monotherapy is not a recommended initial regimen."),
                            ("D", "Refer for kidney transplant because IgA nephropathy inevitably leads to kidney failure", False, "Many patients with IgA nephropathy do not progress; transplantation is reserved for advanced disease and recurrence is a later concern."),
                        ],
                    },
                ],
            },
            {
                "title": "ANCA-Associated Vasculitis",
                "slug": "anca-vasculitis",
                "description": "Granulomatosis with polyangiitis, microscopic polyangiitis, and induction and maintenance therapy.",
                "lessons": [
                    {
                        "title": "ANCA-Associated Vasculitis",
                        "lesson_slug": "anca-associated-vasculitis",
                        "lesson_type": "article",
                        "summary": "Clinical phenotypes, serology, and KDIGO 2024 induction and maintenance regimens.",
                        "content_md": (
                            "# ANCA-associated vasculitis\n\n"
                            "## Phenotypes\n"
                            "- Granulomatosis with polyangiitis: upper airway disease (sinusitis, otitis, nasal crusting, "
                            "subglottic stenosis) plus lung and kidney disease; usually PR3-ANCA\n"
                            "- Microscopic polyangiitis: pulmonary-renal and skin disease without granulomatous upper airway "
                            "involvement; usually MPO-ANCA\n"
                            "- Eosinophilic granulomatosis with polyangiitis: asthma, eosinophilia, and neuropathy; "
                            "ANCA in about 30-40%\n\n"
                            "## Serology and testing\n"
                            "ANCA by immunoassay with confirmatory immunofluorescence when negative MPO/PR3 are present, "
                            "because up to 20% of AAV patients are ANCA-negative. Urinalysis shows dysmorphic red cells and "
                            "red cell casts. Chest imaging may show nodules or alveolar hemorrhage.\n\n"
                            "## Induction\n"
                            "Glucocorticoids combined with rituximab or cyclophosphamide for new-onset severe disease; the "
                            "combination reduces cyclophosphamide exposure. Rituximab is favored in relapsing disease, in "
                            "those with prior cyclophosphamide, in fertility concerns, and in severe kidney disease where the "
                            "CYCLOPS regimen was effective. Plasma exchange is considered for severe renal disease "
                            "(creatinine above about 3.4 mg/dL, rapidly rising, or dialysis dependent) or diffuse alveolar "
                            "hemorrhage with hypoxemia, with the decision individualized as trial evidence has evolved.\n\n"
                            "## Maintenance\n"
                            "After remission, transition to rituximab, azathioprine, or methotrexate with a tapering "
                            "glucocorticoid regimen for 2-4 years, with monitoring of clinical activity, blood counts, and "
                            "liver function."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-anca-aav-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 68-year-old with hemoptysis, a falling hemoglobin, dysmorphic hematuria, and creatinine 4.1 mg/dL rising to 5.0 mg/dL over 2 weeks has nasal crusting and prior sinusitis. MPO-ANCA is positive at 128 AU/mL and PR3 is negative.",
                        "labs": {"cr": "4.1 rising to 5.0 mg/dL", "mpo_anca": "128 AU/mL", "pr3": "negative", "ua": "dysmorphic RBCs"},
                        "question_text": "Which induction regimen is most appropriate?",
                        "explanation": "The combination of pulmonary hemorrhage, rapidly progressive glomerulonephritis, upper airway disease, and MPO-ANCA positivity establishes ANCA-associated vasculitis with severe organ-threatening kidney involvement, which requires induction therapy with glucocorticoids combined with either rituximab or cyclophosphamide. Both are first-line, and the combination is selected on disease severity, relapse history, prior cyclophosphamide exposure, fertility considerations, and infection risk. Plasma exchange is considered when there is rapidly worsening kidney function or hypoxemic diffuse alveolar hemorrhage. Supportive care includes blood pressure management and pneumocystis prophylaxis, and treatment is not delayed pending biopsy when the clinical and serologic picture is this clear, though biopsy is still recommended.",
                        "clinical_pearl": "Severe AAV: glucocorticoids plus rituximab or cyclophosphamide; consider plasma exchange for rapidly rising creatinine or hypoxemic alveolar hemorrhage.",
                        "reference_ids": ["kdigo-anca-aav-2024"],
                        "lesson_slug": "anca-associated-vasculitis",
                        "choices": [
                            ("A", "Glucocorticoids plus rituximab or cyclophosphamide for induction, with plasma exchange considered for rapidly worsening renal function or hypoxemic alveolar hemorrhage", True, None),
                            ("B", "Azathioprine monotherapy for maintenance-quality remission", False, "Azathioprine is a maintenance agent; organ-threatening disease requires glucocorticoids plus rituximab or cyclophosphamide."),
                            ("C", "Cyclophosphamide monotherapy without glucocorticoids", False, "Cyclophosphamide is combined with glucocorticoids in induction regimens; glucocorticoids carry much of the early anti-inflammatory effect."),
                            ("D", "Observation with serial creatinine, since ANCA-associated glomerulonephritis often stabilizes spontaneously", False, "Untreated organ-threatening AAV progresses to irreversible kidney failure; immunosuppression is mandatory."),
                        ],
                    },
                ],
            },
            {
                "title": "Thrombotic Microangiopathies",
                "slug": "thrombotic-microangiopathy",
                "description": "TMA physiology, TTP and atypical HUS, and complement-mediated disease.",
                "lessons": [
                    {
                        "title": "Thrombotic Microangiopathies",
                        "lesson_slug": "thrombotic-microangiopathies",
                        "lesson_type": "article",
                        "summary": "Distinguishing TTP, complement-mediated aHUS, secondary TMA, and drug-induced TMA.",
                        "content_md": (
                            "# Thrombotic microangiopathies\n\n"
                            "## Definition\n"
                            "A triad of microangiopathic hemolytic anemia, thrombocytopenia, and organ injury (usually acute "
                            "kidney injury), caused by endothelial injury and platelet activation with platelet-rich "
                            "microthrombi. Renal-limited disease favors complement-mediated aHUS; neurologic and systemic "
                            "features favor TTP.\n\n"
                            "## TTP\n"
                            "Severe ADAMTS13 deficiency from an autoantibody causes large vWF multimers and platelet "
                            "microthrombi. Classic features are thrombocytopenia, microangiopathic hemolytic anemia, "
                            "neurologic symptoms, fever, and renal injury. Diagnosis rests on severe ADAMTS13 activity "
                            "deficiency (below 10%). Treatment is urgent plasma exchange, corticosteroids, and caplacizumab "
                            "(anti-vWF nanobody) with rituximab, and must begin before results return when the suspicion "
                            "is high.\n\n"
                            "## Complement-mediated aHUS\n"
                            "Alternative pathway dysregulation from complement gene variants or autoantibodies, frequently "
                            "triggered by infection, pregnancy, or surgery. Features are hemolytic anemia, thrombocytopenia, "
                            "and severe AKI with hypertension and neurologic involvement. Treat with eculizumab or "
                            "ravulizumab; do not stop complement blockade during pregnancy or aHUS flares.\n\n"
                            "## Secondary TMA\n"
                            "Shiga toxin-producing E. coli, Streptococcus pneumoniae, malignant hypertension, scleroderma "
                            "renal crisis, antiphospholipid syndrome, pregnancy, and drugs such as calcineurin inhibitors, "
                            "gemcitabine, VEGF inhibitors, and quinine. Treat the cause, and add plasma exchange for "
                            "Shiga toxin disease. Ticlopidine-associated TTP has the same treatment as TTP."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-ckd-2024", "kdigo-anca-aav-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 42-year-old presents with headache and confusion after a diarrheal illness. Platelets are 18 K/uL, hemoglobin 7.2 g/dL with schistocytes, creatinine 1.4 mg/dL, and LDH 2400 U/L. ADAMTS13 activity is pending.",
                        "labs": {"platelets": "18 K/uL", "hgb": "7.2 g/dL", "schistocytes": "present", "ldh": "2400 U/L", "cr": "1.4 mg/dL"},
                        "question_text": "What is the most appropriate immediate management?",
                        "explanation": "This is a thrombotic microangiopathy with the classic features of thrombotic thrombocytopenic purpura: severe thrombocytopenia, microangiopathic hemolytic anemia with schistocytes and high LDH, neurologic symptoms, and relatively mild kidney injury for the degree of hemolysis and platelet consumption. ADAMTS13 activity below 10% confirms TTP, but treatment must not wait for the result because mortality rises sharply with each hour of delay. The standard is therapeutic plasma exchange, corticosteroids, and caplacizumab, which is increasingly given alongside plasma exchange and rituximab rather than after a plasma exchange failure. Platelet transfusion is avoided unless life-threatening bleeding occurs.",
                        "clinical_pearl": "Suspected TTP: start plasma exchange, steroids, and caplacizumab immediately, without waiting for the ADAMTS13 result.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "thrombotic-microangiopathies",
                        "choices": [
                            ("A", "Begin therapeutic plasma exchange, corticosteroids, and caplacizumab without waiting for the ADAMTS13 result", True, None),
                            ("B", "Start eculizumab immediately, since bloody diarrhea after infection indicates complement-mediated aHUS", False, "The prominent neurologic features with mild kidney injury point to TTP; eculizumab is the treatment for complement-mediated aHUS, and the diarrhea alone does not establish it."),
                            ("C", "Transfuse two units of platelets to raise the platelet count above 50 K/uL", False, "Platelet transfusion in TTP is generally avoided because it may feed platelet-rich microthrombi unless there is life-threatening bleeding."),
                            ("D", "Await the ADAMTS13 result and treat only if activity is below 10%", False, "Waiting for the result raises mortality; empiric treatment should begin on clinical suspicion."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 3-year-old develops bloody diarrhea and then anuria with hemolytic anemia, thrombocytopenia, and a creatinine of 4.8 mg/dL. Blood pressure is 158/100 mmHg. There is no prior renal disease, and C3 is low at 55 mg/dL.",
                        "labs": {"cr": "4.8 mg/dL", "bp": "158/100", "c3": "55 mg/dL", "platelets": "22 K/uL"},
                        "question_text": "Which is the most appropriate treatment?",
                        "explanation": "A child with bloody diarrhea followed by acute kidney injury, microangiopathic hemolytic anemia, thrombocytopenia, hypertension, and low C3 is the classic presentation of Shiga toxin-producing E. coli hemolytic uremic syndrome, a secondary thrombotic microangiopathy. The primary treatment is supportive: meticulous fluid and electrolyte management, blood pressure control, and renal replacement therapy if indicated, with eculizumab reserved for atypical or complement-mediated cases and for severe disease requiring dialysis. Antibiotics are generally avoided in suspected Shiga toxin E. coli infection because antibiotic-induced bacterial lysis may release additional toxin and worsen hemolysis; antimotility agents and platelet transfusions are also avoided unless bleeding is severe.",
                        "clinical_pearl": "Bloody diarrhea plus AKI, hemolysis, and thrombocytopenia in a child = Shiga toxin HUS: supportive care, avoid antibiotics and antimotility drugs.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "thrombotic-microangiopathies",
                        "choices": [
                            ("A", "Supportive care with careful volume management, antihypertensive therapy, and dialysis if needed, while avoiding antibiotics and antimotility agents", True, None),
                            ("B", "Immediate plasma exchange for 2 weeks", False, "Plasma exchange is not the primary treatment of typical Shiga toxin HUS, which is managed supportively in children."),
                            ("C", "Start eculizumab as first-line therapy for all HUS", False, "Complement blockade is reserved for atypical complement-mediated HUS, atypical or severe cases, and situations in which Shiga toxin cannot be excluded confidently; typical childhood HUS responds to supportive care."),
                            ("D", "Transfuse platelets to keep the count above 50 K/uL and give an antidiarrheal agent", False, "Both are avoided: platelet transfusion may worsen microthrombi and antimotility agents can prolong toxin exposure."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Transplantation",
        "slug": "transplantation",
        "order_index": 9,
        "description": "Immunosuppression regimens, hyperacute, acute and chronic rejection, and post-transplant complications.",
        "icon": "ShuffleIcon",
        "category_slug": "transplantation",
        "topics": [
            {
                "title": "Immunosuppression",
                "slug": "immunosuppression",
                "description": "Induction and maintenance therapy, calcineurin inhibitor toxicity, and mTOR inhibitors.",
                "lessons": [
                    {
                        "title": "Immunosuppression Principles",
                        "lesson_slug": "immunosuppression-principles",
                        "lesson_type": "article",
                        "summary": "Induction agents, maintenance triple therapy, and the risks of each drug class.",
                        "content_md": (
                            "# Immunosuppression in kidney transplantation\n\n"
                            "## Induction\n"
                            "Given in the first days after transplant. Options:\n"
                            "- Anti-lymphocyte globulin (ATG): the most potent induction, used in high immunologic risk "
                            "(high panel reactive antibody, prior transplant, African descent) and in many low-risk programs\n"
                            "- Interleukin-2 receptor antagonist (basiliximab): standard for low immunologic risk, with lower "
                            "infection risk\n"
                            "- No induction: acceptable in very low-risk recipients when combined with modern maintenance\n\n"
                            "## Maintenance\n"
                            "Triple therapy: a calcineurin inhibitor (tacrolimus preferred) plus an antimetabolite (mycophenolate "
                            "mofetil) plus glucocorticoids. Tacrolimus and mycophenolate combination is associated with the "
                            "best graft survival. Steroid withdrawal after 3 months is acceptable in many low-risk recipients.\n\n"
                            "## Adverse effects\n"
                            "- Calcineurin inhibitors: nephrotoxicity with arteriolar hyalinosis and striped interstitial "
                            "fibrosis, hyperkalemia, hypertension, tremor, new-onset diabetes, and hypertrichosis\n"
                            "- Mycophenolate: marrow suppression, gastrointestinal intolerance, teratogenicity, and infection risk\n"
                            "- mTOR inhibitors (sirolimus, everolimus): hyperlipidemia, delayed wound healing, impaired tissue "
                            "healing, proteinuria, cytopenias, and pneumonitis; usually deferred until wound healing is complete\n"
                            "- Glucocorticoids: infection, hyperglycemia, bone disease, and cardiovascular risk\n\n"
                            "## Monitoring\n"
                            "Trough drug levels, CBC, and renal function, with protocol-based adjustments and drug interactions "
                            "reviewed carefully (calcineurin inhibitors are CYP3A substrates)."
                        ),
                        "duration_seconds": 270,
                        "reference_ids": ["kdigo-transplant-2009"],
                    },
                    {
                        "title": "Immunosuppression Drug Therapy",
                        "lesson_slug": "immunosuppression-drug-therapy",
                        "lesson_type": "animation",
                        "summary": "Step animation of induction and maintenance immunosuppression and its main toxicities.",
                        "animation_url": f"{ANIMATION_BASE}/nephrology-pharmacology.json",
                        "duration_seconds": 110,
                        "reference_ids": ["kdigo-transplant-2009"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 45-year-old with end-stage kidney disease from diabetic nephropathy receives a deceased-donor kidney transplant with panel reactive antibody 12%. He is discharged on tacrolimus, mycophenolate mofetil, and prednisone.",
                        "labs": {"pra": "12%", "donor": "deceased donor", "regimen": "tacrolimus, MMF, prednisone"},
                        "question_text": "Which statement about his induction and maintenance therapy is most accurate?",
                        "explanation": "For a recipient at low-to-moderate immunologic risk, induction with an interleukin-2 receptor antagonist such as basiliximab is standard, with anti-lymphocyte globulin reserved for high-risk recipients such as those with high panel reactive antibody, prior transplant, or African descent. Maintenance is triple therapy: a calcineurin inhibitor (tacrolimus preferred because of the tacrolimus-mycophenolate combination advantage) plus mycophenolate plus glucocorticoids, with therapeutic drug monitoring of tacrolimus troughs. The principle is adequate immunosuppression with the lowest effective exposure, since over-immunosuppression causes infection and malignancy and under-immunosuppression causes rejection.",
                        "clinical_pearl": "Low-risk recipients: basiliximab induction plus tacrolimus, mycophenolate, and prednisone. ATG for high immunologic risk.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "immunosuppression-principles",
                        "choices": [
                            ("A", "Induction with an IL-2 receptor antagonist such as basiliximab is appropriate at this risk level, and maintenance is tacrolimus, mycophenolate mofetil, and prednisone with trough monitoring", True, None),
                            ("B", "Induction with anti-lymphocyte globulin is mandatory for every recipient regardless of risk", False, "ATG is reserved for high immunologic risk; using it in low-risk recipients adds infection and malignancy risk without benefit."),
                            ("C", "Maintenance should use sirolimus and prednisone only to avoid calcineurin inhibitor nephrotoxicity", False, "CNI avoidance from the outset increases rejection rates; the standard is CNI plus mycophenolate plus steroids."),
                            ("D", "Mycophenolate should be stopped at 3 months in all stable recipients", False, "Mycophenolate is generally continued long term; it is one of the two agents most strongly associated with graft survival."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A recipient 8 months post-transplant has a stable creatinine of 1.4 mg/dL but a rising tacrolimus trough of 9.2 ng/mL and a gradual creatinine rise to 1.9 mg/dL. Graft biopsy shows arteriolar hyalinosis, striped interstitial fibrosis, and isometric vacuolization of tubular epithelium.",
                        "labs": {"tacrolimus_trough": "9.2 ng/mL", "cr": "1.4 to 1.9 mg/dL", "k": "5.4 mEq/L"},
                        "question_text": "What is the most likely diagnosis and best response?",
                        "explanation": "The biopsy pattern of arteriolar hyalinosis, striped interstitial fibrosis, and isometric tubular vacuolization is classic for chronic calcineurin inhibitor nephrotoxicity, driven by afferent arteriolar vasoconstriction and arteriolar hyalinosis. A rising trough level, hyperkalemia, hypertension, and a gradual creatinine decline support the diagnosis. Management is to reduce calcineurin inhibitor exposure, correct the excess drug level, review interacting medications such as azoles and grapefruit, and consider conversion to an alternative regimen or to an mTOR inhibitor once the acute wound-healing phase is long past. Acute rejection must always be excluded by biopsy interpretation, and other causes of graft dysfunction reviewed before attributing everything to CNI toxicity.",
                        "clinical_pearl": "Striped fibrosis, arteriolar hyalinosis, and tubular vacuolization mean chronic CNI toxicity: lower the trough, review interactions, consider conversion.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "immunosuppression-drug-therapy",
                        "choices": [
                            ("A", "Chronic calcineurin inhibitor nephrotoxicity; reduce tacrolimus exposure, review drug interactions, and consider regimen conversion while excluding rejection", True, None),
                            ("B", "Chronic active antibody-mediated rejection; add plasmapheresis and IVIG", False, "Antibody-mediated rejection requires donor-specific antibody and complement C4d or microvascular inflammation on biopsy; the described findings are those of CNI toxicity."),
                            ("C", "Acute T-cell-mediated rejection; give high-dose corticosteroids", False, "Acute rejection shows interstitial inflammation with tubulitis, not arteriolar hyalinosis and striped fibrosis."),
                            ("D", "Normal expected post-transplant change; no change is needed", False, "This is an abnormal, drug-related pattern that warrants exposure reduction and re-biopsy if function continues to decline."),
                        ],
                    },
                ],
            },
            {
                "title": "Transplant Rejection",
                "slug": "rejection",
                "description": "Hyperacute, acute cellular and antibody-mediated rejection, and chronic allograft dysfunction.",
                "lessons": [
                    {
                        "title": "Transplant Rejection",
                        "lesson_slug": "transplant-rejection",
                        "lesson_type": "animation",
                        "summary": "Step animation of hyperacute, acute cellular, and antibody-mediated rejection timelines.",
                        "animation_url": f"{ANIMATION_BASE}/transplant-rejection.json",
                        "duration_seconds": 120,
                        "image_url": f"{MEDICAL_ASSET_BASE}/transplantation/transplant-biopsy-acr-amr.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/transplantation/transplant-biopsy-acr-amr-thumb.webp",
                        "reference_ids": ["kdigo-transplant-2009"],
                    },
                    {
                        "title": "Rejection Management",
                        "lesson_slug": "rejection-management",
                        "lesson_type": "article",
                        "summary": "Diagnosis by biopsy and blood tests, with treatment for each type of rejection.",
                        "content_md": (
                            "# Transplant rejection\n\n"
                            "## Hyperacute rejection\n"
                            "Minutes to hours after reperfusion, from preformed anti-donor antibodies (ABO or HLA) acting on "
                            "the graft endothelium, causing thrombosis, ischemia, and graft loss. Prevented by ABO "
                            "compatibility, crossmatch screening, and desensitization protocols; treated by graft nephrectomy.\n\n"
                            "## Acute T-cell-mediated rejection\n"
                            "Days to months, or any time with non-adherence. Presentation is rising creatinine, fever, graft "
                            "tenderness, and proteinuria. Biopsy shows interstitial mononuclear inflammation, tubulitis, and in "
                            "severe cases intimal arteritis. Treated with high-dose intravenous corticosteroids, "
                            "anti-thymocyte globulin for steroid-resistant or Banff grade II-III, and correction of "
                            "non-adherence.\n\n"
                            "## Acute antibody-mediated rejection\n"
                            "Days to months, typically within 3 months, also seen late with non-adherence. Diagnostic criteria "
                            "include morphological evidence of microvascular inflammation, evidence of antibody interaction "
                            "with endothelium (C4d staining or moderate microvascular inflammation), and serologic evidence "
                            "of donor-specific antibodies. Treated with plasma exchange, intravenous immunoglobulin, "
                            "rituximab or other B-cell directed therapy, corticosteroids, and optimization of maintenance "
                            "immunosuppression.\n\n"
                            "## Chronic allograft dysfunction\n"
                            "Interstitial fibrosis and tubular atrophy with transplant glomerulopathy and vascular "
                            "intimal thickening, driven by antibody-mediated injury, CNI toxicity, BK virus, recurrent "
                            "disease, and rejection. Management is optimization of immunosuppression and treatment of "
                            "specific causes; established graft loss requires return to dialysis or re-transplantation."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["kdigo-transplant-2009"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A graft becomes mottled and flaccid in the recovery room, 30 minutes after reperfusion. The patient had a high panel reactive antibody of 85% and a weakly positive complement-dependent cytotoxicity crossmatch that was interpreted as acceptable because of urgency. Urine output is 5 mL/hr.",
                        "labs": {"pra": "85%", "crossmatch": "weakly positive CDC", "urine_output": "5 mL/hr", "timing": "30 min after reperfusion"},
                        "question_text": "What is the most likely diagnosis and correct management of this immediately failed graft?",
                        "explanation": "A flaccid, mottled graft with minimal urine output minutes after reperfusion in a highly sensitized recipient with a positive crossmatch is hyperacute rejection, caused by preformed anti-donor antibodies binding the graft endothelium and activating complement, leading to thrombosis and ischemia within minutes to hours. This cannot be reversed by immunosuppression or plasmapheresis once established. Management is urgent transplant nephrectomy to prevent systemic cytokine release and graft necrosis, and the patient returns to dialysis while the cause is addressed; future options include desensitization, paired exchange, or incompatible transplantation. The preventive failures were the positive crossmatch and the acceptance of a weakly positive result in an urgent setting.",
                        "clinical_pearl": "Hyperacute rejection: flaccid mottled graft minutes after reperfusion in a sensitized, crossmatch-positive patient. Nephrectomy; no medical rescue.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "rejection-management",
                        "choices": [
                            ("A", "Hyperacute rejection from preformed anti-donor antibodies; urgent graft nephrectomy is required because medical therapy cannot reverse established hyperacute rejection", True, None),
                            ("B", "Acute antibody-mediated rejection; start plasmapheresis and IVIG", False, "Plasmapheresis can treat acute antibody-mediated rejection, but a graft that is already flaccid and ischemic minutes after reperfusion has hyperacute rejection, which is not reversible."),
                            ("C", "Acute T-cell-mediated rejection; give methylprednisolone 500 mg for 3 days", False, "Hyperacute rejection occurs before any cellular immune process can develop and does not respond to corticosteroids."),
                            ("D", "Renal artery thrombosis; take the patient immediately to the operating room for thrombectomy", False, "Vascular thrombosis is part of the hyperacute process, and the systemic consequences of a necrotic graft require nephrectomy rather than thrombectomy alone."),
                        ],
                    },
                    {
                        "difficulty": "board",
                        "case_text": "Six weeks after transplant, a recipient has a creatinine rise from 1.3 to 2.4 mg/dL. Biopsy shows patchy interstitial mononuclear inflammation with focal tubulitis (Banff grade IA), and there is no donor-specific antibody, no C4d staining, and no glomerulitis.",
                        "labs": {"creatinine": "1.3 to 2.4 mg/dL", "dsa": "negative", "c4d": "negative", "banff": "IA tcmr"},
                        "question_text": "Which treatment is most appropriate for this Banff grade IA acute T-cell-mediated rejection?",
                        "explanation": "Interstitial inflammation with tubulitis and no evidence of antibody interaction with the endothelium or donor-specific antibody defines Banff grade IA acute T-cell-mediated rejection. First-line treatment is high-dose intravenous corticosteroids such as methylprednisolone 250-500 mg daily for 3 days, which reverses most grade IA rejections. Anti-lymphocyte globulin is reserved for steroid-resistant rejection or higher-grade (II to III) disease, and plasma exchange is reserved for antibody-mediated rejection. Contributing causes should be corrected at the same time, especially non-adherence, drug interactions lowering calcineurin inhibitor levels, infection, and inadequate maintenance dosing.",
                        "clinical_pearl": "Banff IA acute cellular rejection: steroid pulse first. ATG only for steroid resistance or grade II-III; plasmapheresis for ABMR.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "rejection-management",
                        "choices": [
                            ("A", "High-dose intravenous corticosteroids with correction of contributing factors such as non-adherence or drug interactions", True, None),
                            ("B", "Plasma exchange and intravenous immunoglobulin", False, "Those therapies treat antibody-mediated rejection, which is excluded here by absent DSA, absent C4d, and absent glomerulitis."),
                            ("C", "Anti-lymphocyte globulin as first-line therapy", False, "ATG is reserved for steroid-resistant rejection or higher-grade disease; it is not first-line for grade IA."),
                            ("D", "Return the patient to dialysis", False, "Acute cellular rejection at 6 weeks with a viable graft is highly treatable and dialysis is not indicated."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A recipient 3 months post-transplant presents with a creatinine rise from 1.2 to 2.6 mg/dL. Biopsy shows glomerulitis and peritubular capillaritis, diffuse C4d staining in peritubular capillaries, and a newly detectable class II donor-specific antibody at a high level (MFI 12,000).",
                        "labs": {"creatinine": "1.2 to 2.6 mg/dL", "c4d": "diffuse positive", "dsa_class2": "MFI 12000", "glomerulitis": "present"},
                        "question_text": "Which treatment is most appropriate for this active antibody-mediated rejection?",
                        "explanation": "This patient meets all three Banfi criteria for active antibody-mediated rejection: morphological evidence of acute tissue injury (glomerulitis and peritubular capillaritis), evidence of current antibody interaction with the endothelium (diffuse C4d in peritubular capillaries), and serologic evidence of a de novo high-level class II donor-specific antibody. Standard treatment combines plasmapheresis to remove circulating antibodies, intravenous immunoglobulin for immunomodulation and reduction of alloantibody, rituximab or other B-cell directed therapy, corticosteroids, and optimization of maintenance immunosuppression. Failure to treat leads to acute graft loss, and the vascular injury and C4d positivity predict higher long-term risk of chronic rejection.",
                        "clinical_pearl": "Active ABMR = injury + C4d or microvascular inflammation + DSA. Treat with plasmapheresis, IVIG, and rituximab, plus steroids.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "rejection-management",
                        "choices": [
                            ("A", "Plasma exchange, intravenous immunoglobulin, and anti-B-cell therapy with corticosteroids, plus optimization of maintenance immunosuppression", True, None),
                            ("B", "High-dose corticosteroids alone", False, "Corticosteroids alone do not remove circulating donor-specific antibody and are inadequate for antibody-mediated rejection."),
                            ("C", "Reduction of calcineurin inhibitor exposure to protect the graft", False, "Reducing immunosuppression during active antibody-mediated rejection risks irreversible graft loss; the graft needs more, not less, immunosuppression."),
                            ("D", "Immediate graft nephrectomy", False, "Nephrectomy is reserved for hyperacute rejection or a necrotic, infected graft; acute antibody-mediated rejection is treated medically."),
                        ],
                    },
                ],
            },
            {
                "title": "Post-Transplant Complications",
                "slug": "post-transplant-complications",
                "description": "BK polyomavirus, opportunistic infection, malignancy, and mTOR inhibitor complications.",
                "lessons": [
                    {
                        "title": "Post-Transplant Complications",
                        "lesson_slug": "post-transplant-complications",
                        "lesson_type": "article",
                        "summary": "BK virus nephropathy, opportunistic infection, PTLD, and mTOR inhibitor toxicity.",
                        "content_md": (
                            "# Post-transplant complications\n\n"
                            "## BK polyomavirus nephropathy\n"
                            "Asymptomatic viruria, then viremia, then graft nephropathy, driven by potent immunosuppression. "
                            "Risk factors include a negative pre-transplant BK serology, high tacrolimus exposure, African "
                            "descent, and rejection treatment. Diagnosis is by quantitative serum BK viral DNA; reduction or "
                            "withdrawal of mycophenolate, and substitution of leflunomide or sirolimus, are the main "
                            "strategies, alongside reduction of calcineurin inhibitor exposure. Screening protocols detect "
                            "viremia before nephropathy develops. Resistant cases may be treated with ciprofloxacin, "
                            "leflunomide, or reduction of immunosuppression with monitoring.\n\n"
                            "## Opportunistic infection\n"
                            "Risk follows the net state of immunosuppression. Important infections include cytomegalovirus, "
                            "Pneumocystis jirovecii pneumonia (prevented with prophylaxis for 6-12 months), EBV and "
                            "post-transplant lymphoproliferative disorder, fungal infection, and tuberculosis. Treat with "
                            "antimicrobial therapy and reduction of immunosuppression where feasible.\n\n"
                            "## Malignancy\n"
                            "Skin cancer is the most common; post-transplant lymphoproliferative disorder is "
                            "EBV-associated and is treated with reduction of immunosuppression, rituximab for CD20-positive "
                            "disease, and chemotherapy in aggressive cases.\n\n"
                            "## mTOR inhibitor complications\n"
                            "Sirolimus and everolimus impair wound healing and tissue repair, cause hyperlipidemia, "
                            "proteinuria, cytopenias, pneumonitis, and impaired wound healing, so they are typically started "
                            "later rather than immediately after transplant. Female patients should be counseled about the "
                            "high rate of ovarian cyst formation and the risk of wound complications."
                        ),
                        "duration_seconds": 240,
                        "image_url": f"{MEDICAL_ASSET_BASE}/transplantation/post-transplant-dsa.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/transplantation/post-transplant-dsa-thumb.webp",
                        "reference_ids": ["kdigo-transplant-2009"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A recipient 5 months post-transplant has a rising creatinine from 1.3 to 2.1 mg/dL. Serum BK viral DNA is 2.5 million copies/mL. Biopsy shows tubulointerstitial nephritis with viral cytopathic inclusions and SV40 immunostaining positive in tubular nuclei.",
                        "labs": {"bk_dna": "2,500,000 copies/mL", "sv40_ihc": "positive", "creatinine": "1.3 to 2.1 mg/dL"},
                        "question_text": "What is the most appropriate management of BK polyomavirus nephropathy?",
                        "explanation": "Rising serum BK viral DNA above 10,000 copies/mL, a decline in graft function, and SV40-positive tubular nuclei on biopsy establish BK polyomavirus nephropathy. The cornerstone of management is reduction of immunosuppression, most often reducing or withdrawing mycophenolate, lowering tacrolimus exposure, and substituting leflunomide or sirolimus where appropriate, with serial BK viral DNA monitoring to confirm viral clearance. Cidofovir, leflunomide, and ciprofloxacin are options for resistant cases, and a low threshold for graft nephrectomy applies if the virus is uncontrolled. Reducing immunosuppression is what distinguishes this from rejection, where immunosuppression must be increased.",
                        "clinical_pearl": "BK nephropathy = reduce immunosuppression (mycophenolate first), monitor BK DNA; increasing immunosuppression worsens it.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "post-transplant-complications",
                        "choices": [
                            ("A", "Reduce immunosuppression, most often withdrawing or reducing mycophenolate and lowering calcineurin inhibitor exposure, with serial BK viral DNA monitoring", True, None),
                            ("B", "Increase mycophenolate and treat presumed acute cellular rejection with methylprednisolone", False, "Increasing immunosuppression in BK nephropathy accelerates viral replication and graft loss; the biopsy pattern with SV40 positivity confirms BK, not rejection."),
                            ("C", "Start long-term ganciclovir and valacyclovir for the duration of the transplant", False, "Antiviral therapy may be used in selected cases, but the definitive treatment is reduction of immunosuppression."),
                            ("D", "Proceed directly to graft nephrectomy without a trial of immunosuppression reduction", False, "Nephrectomy is reserved for uncontrolled or fulminant infection; a trial of reduced immunosuppression with monitoring is standard first."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A recipient 4 months after transplant develops non-productive cough, fever, and hypoxemia requiring 4 L of oxygen. CT shows diffuse ground-glass opacities. He received a lymphocyte-depleting induction agent and has had two rejection episodes.",
                        "labs": {"oxygen": "4 L", "ct": "diffuse ground glass", "timing": "4 months post tx", "induction": "depleting"},
                        "question_text": "Which infection and treatment are most likely?",
                        "explanation": "Diffuse ground-glass opacities with hypoxemia in a recipient 4 months after transplant with potent immunosuppression and repeated rejection episodes is most consistent with Pneumocystis jirovecii pneumonia. Risk is greatest in the first 6-12 months, with lymphocyte-depleting induction, high-dose corticosteroids, and rejection treatment as major risk factors. Diagnosis is by induced sputum or bronchoscopy with silver or immunofluorescent staining, and treatment is intravenous trimethoprim-sulfamethoxazole with corticosteroids when the PaO2 is below 70 mmHg or when the A-a gradient exceeds 35 mmHg. Prophylaxis with trimethoprim-sulfamethoxazole is standard after transplant and also prevents urinary tract infection, toxoplasmosis, and nocardia.",
                        "clinical_pearl": "Ground-glass opacities with hypoxemia in the first transplant year = Pneumocystis jirovecii; treat with IV TMP-SMX plus steroids if hypoxemic.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "post-transplant-complications",
                        "choices": [
                            ("A", "Pneumocystis jirovecii pneumonia, treated with intravenous trimethoprim-sulfamethoxazole, adding corticosteroids when hypoxemia is present", True, None),
                            ("B", "Cytomegalovirus pneumonitis, treated with ganciclovir and valganciclovir", False, "CMV pneumonitis is an important differential, but diffuse ground-glass opacities with this risk profile are most typical of Pneumocystis, and ganciclovir carries marrow toxicity that should be avoided when the diagnosis is not established."),
                            ("C", "Bacterial pneumonia, treated empirically with ceftriaxone alone", False, "Bacterial pneumonia does not usually produce diffuse ground-glass opacities, and a single agent is inadequate for an opportunistic infection in this setting."),
                            ("D", "Pulmonary edema from volume overload, treated with diuresis", False, "Although possible, the fever, ground-glass opacities, and immunosuppression make an opportunistic infection the priority, and empiric TMP-SMX coverage is prudent while testing proceeds."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 58-year-old recipient 8 months post-transplant presents with fever, night sweats, and an enlarging cervical lymph node. Biopsy shows a monomorphic population of CD20-positive B cells positive for EBV-encoded RNA. Creatinine is stable.",
                        "labs": {"node": "cervical, enlarging", "cd20": "positive", "eber": "positive", "creatinine": "stable"},
                        "question_text": "What is the most appropriate management of this post-transplant lymphoproliferative disorder?",
                        "explanation": "A monomorphic CD20-positive B-cell proliferation that is EBV-encoded RNA positive in a transplant recipient is post-transplant lymphoproliferative disorder, an EBV-driven B-cell proliferation caused by impaired T-cell surveillance under immunosuppression. The first step is reduction of immunosuppression, which alone can produce regression in early, low-volume, monomorphic disease, and is always part of management. Rituximab targets CD20-positive B cells and is added for overt or persistent disease, with chemotherapy for aggressive or refractory disease and reduction of immunosuppression as tolerated. Reducing immunosuppression also helps control the underlying EBV drive.",
                        "clinical_pearl": "EBV-positive, CD20-positive monomorphic B-cell disease after transplant = PTLD: reduce immunosuppression first, then rituximab.",
                        "reference_ids": ["kdigo-transplant-2009"],
                        "lesson_slug": "post-transplant-complications",
                        "choices": [
                            ("A", "Reduce immunosuppression and add rituximab, escalating to chemotherapy for refractory disease", True, None),
                            ("B", "Increase immunosuppression with methylprednisolone to treat EBV", False, "Corticosteroids alone may transiently shrink the node but increase the risk of graft loss and progression; PTLD is treated by reducing immunosuppression and adding rituximab."),
                            ("C", "Start foscarnet and continue the current regimen", False, "Foscarnet treats CMV, not EBV-driven B-cell proliferation; the therapeutic axis for PTLD is reduced immunosuppression plus B-cell directed therapy."),
                            ("D", "Observe because most PTLD is self-limited and graft function is normal", False, "Early reduction of immunosuppression can be effective, but monomorphic EBV-positive PTLD is a malignancy and requires active treatment in most patients."),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "Nephrology Pharmacology",
        "slug": "nephrology-pharmacology",
        "order_index": 10,
        "description": "Dose adjustment by kidney function, diuretic prescribing, RAAS blockade with hyperkalemia, and avoiding nephrotoxins.",
        "icon": "PillIcon",
        "category_slug": "pharmacology",
        "topics": [
            {
                "title": "Drug Dosing in CKD",
                "slug": "drug-dosing-ckd",
                "description": "Renal elimination, dose adjustment principles, and high-risk drug classes.",
                "lessons": [
                    {
                        "title": "Renal Drug Dosing",
                        "lesson_slug": "renal-drug-dosing",
                        "lesson_type": "animation",
                        "summary": "Step animation of how declining GFR changes drug exposure and dosing intervals.",
                        "animation_url": f"{ANIMATION_BASE}/nephrology-pharmacology.json",
                        "duration_seconds": 110,
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025"],
                    },
                    {
                        "title": "Drug Dosing in CKD",
                        "lesson_slug": "drug-dosing-in-ckd",
                        "lesson_type": "article",
                        "summary": "Adjusting doses and intervals, monitoring, and the drugs that most need attention.",
                        "content_md": (
                            "# Drug dosing in CKD\n\n"
                            "## Core principle\n"
                            "Renally cleared drugs accumulate when GFR falls. The kidney is the only organ with significant "
                            "excretion for many drugs, so dose adjustment must accompany every eGFR change, especially during "
                            "acute kidney injury, on dialysis, or after a change in muscle mass.\n\n"
                            "## How to adjust\n"
                            "- Reduce dose or extend the interval, guided by drug monographs and dosing guides\n"
                            "- Remember that creatinine-based eGFR overestimates renal function in low muscle mass, frail, or "
                            "edematous patients, so use clinical judgment and consider cystatin C\n"
                            "- Cockcroft-Gault creatinine clearance is still used for many drug monographs; use actual body "
                            "weight for most drugs\n\n"
                            "## High-risk classes\n"
                            "- Aminoglycosides: extended interval dosing with therapeutic drug monitoring\n"
                            "- Vancomycin: interval extension, or loading dose plus hemodialysis when needed\n"
                            "- Gabapentin and pregabalin: reduce dose below CrCl 60 and further at CrCl below 30\n"
                            "- LMWH (enoxaparin): reduce dose below CrCl 30\n"
                            "- Opioids: morphine metabolites accumulate; use lower doses and monitor\n"
                            "- Digoxin: lower dose, monitor level and potassium\n"
                            "- Metformin: contraindicated below eGFR 30\n"
                            "- Bisphosphonates: avoid renally excreted agents below eGFR 30-35; use caution with all\n\n"
                            "## Dialysis\n"
                            "Consider drug removal by dialysis when the drug is small, water soluble, and not highly protein "
                            "bound, and time the dose after the session."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A 72-year-old woman with CKD G4 (eGFR 25 mL/min/1.73 m2) is admitted with cellulitis and started on vancomycin 1 g IV every 12 hours. On day 3 she has become confused and her creatinine is 2.8 mg/dL. She is not on dialysis.",
                        "labs": {"egfr": "25 mL/min/1.73m2", "vancomycin_regimen": "1 g IV q12h", "cr": "2.8 mg/dL"},
                        "question_text": "What is the most appropriate vancomycin strategy?",
                        "explanation": "Standard vancomycin dosing assumes an eGFR above 50 mL/min/1.73 m2. At an eGFR of 25, a 1 g dose every 12 hours causes accumulation, vancomycin-associated neurotoxicity (confusion is the classic presentation), and nephrotoxicity, as the rising creatinine partly reflects the drug itself. The correct approach is extended-interval dosing, often 1 g every 3 to 5 days for this degree of renal impairment, guided by a loading dose and by measured serum levels rather than a nomogram alone. Therapeutic drug monitoring is essential, and the strategy must be reassessed with every change in creatinine.",
                        "clinical_pearl": "Vancomycin at eGFR below 50 needs loading-dose extended-interval dosing with level monitoring; confusion on vancomycin is toxicity until proven otherwise.",
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "renal-drug-dosing",
                        "choices": [
                            ("A", "Give a loading dose, then extend the interval substantially and monitor trough vancomycin levels, reassessing with each change in creatinine", True, None),
                            ("B", "Continue 1 g every 12 hours and add an aminoglycoside for synergy", False, "Continuing the interval causes accumulation and toxicity, and adding an aminoglycoside adds nephrotoxicity."),
                            ("C", "Switch to oral vancomycin and stop intravenous therapy", False, "Oral vancomycin achieves negligible systemic concentrations and cannot treat a systemic infection."),
                            ("D", "Initiate hemodialysis to remove vancomycin", False, "Hemodialysis is not indicated for a drug toxicity without uremia or refractory infection; extended-interval dosing with monitoring is the standard response."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "An 80-year-old woman with diabetic CKD started gabapentin 1200 mg three times daily for neuropathic pain when her eGFR was 55 mL/min/1.73 m2. Her eGFR is now 28 mL/min/1.73 m2. She presents with myoclonus, ataxia, and somnolence.",
                        "labs": {"egfr": "28 mL/min/1.73m2", "gabapentin_dose": "1200 mg TID", "symptoms": "myoclonus, ataxia, somnolence"},
                        "question_text": "What is the most appropriate management of this gabapentin neurotoxicity?",
                        "explanation": "Gabapentin is eliminated unchanged by the kidneys, so renal function alone determines dosing, and at a creatinine clearance below 30 mL/min the total daily dose must fall sharply, typically to 200-700 mg once daily. This patient takes 3600 mg per day, a dose that was appropriate at an eGFR of 55 but is far too high at an eGFR of 28, and the myoclonus, ataxia, and somnolence are classic signs of gabapentin accumulation. Management is dose reduction to a once-daily renal regimen, a review of every other renally cleared drug, and monitoring; because dialysis removes only part of the drug, the dose still has to be reduced once a patient starts dialysis.",
                        "clinical_pearl": "Gabapentin is renally cleared unchanged: at CrCl below 30 reduce to 200-700 mg once daily, and re-check the dose whenever the eGFR changes.",
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "drug-dosing-in-ckd",
                        "choices": [
                            ("A", "Reduce gabapentin to a once-daily renal dosing regimen of about 200-700 mg and review all other renally cleared drugs", True, None),
                            ("B", "Continue the current dose and add baclofen for the myoclonus", False, "Continuing the current dose maintains accumulation; adding baclofen would worsen sedation and neuromuscular depression."),
                            ("C", "Increase gabapentin to 1800 mg every 8 hours to control escalating neuropathic pain", False, "Escalating a renally cleared drug in advanced CKD directly causes the toxicity being treated."),
                            ("D", "Switch to pregabalin at the same total daily dose without adjustment", False, "Pregabalin is also renally cleared and requires similar dose reduction, so switching agents at the same dose is unsafe."),
                        ],
                    },
                ],
            },
            {
                "title": "Diuretics",
                "slug": "diuretics",
                "description": "Loop diuretics, thiazides in low GFR, and diuretic complications.",
                "lessons": [
                    {
                        "title": "Loop Diuretics",
                        "lesson_slug": "loop-diuretics",
                        "lesson_type": "animation",
                        "summary": "Step animation of loop diuretic action, dose ceilings, and combination with thiazides.",
                        "animation_url": f"{ANIMATION_BASE}/nephrology-pharmacology.json",
                        "duration_seconds": 100,
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025", "kdigo-aki-2012"],
                    },
                    {
                        "title": "Diuretic Prescribing",
                        "lesson_slug": "diuretic-prescribing",
                        "lesson_type": "article",
                        "summary": "Site of action, thresholds, dosing in AKI and heart failure, and toxicity.",
                        "content_md": (
                            "# Diuretic prescribing\n\n"
                            "## Loop diuretics\n"
                            "Act at the thick ascending limb and increase sodium, potassium, chloride, and water excretion. "
                            "Furosemide has a ceiling intravenous dose of about 80 mg per dose; above that, response plateaus "
                            "until a combination with a thiazide-type diuretic is added. Give intravenously for acute "
                            "decompensated heart failure or AKI, because gut edema limits oral absorption. Doses are "
                            "significantly higher in acute kidney injury than in chronic kidney disease because delivery to "
                            "the tubule falls with GFR.\n\n"
                            "## Thiazide and thiazide-like diuretics\n"
                            "Act at the distal convoluted tubule. They remain effective at low GFR when given in high doses, and "
                            "metolazone and chlorthalidone are commonly used to break loop diuretic resistance in advanced "
                            "CKD. Hyponatremia, hypokalemia, and hyperuricemia are the main toxicities.\n\n"
                            "## Potassium-sparing diuretics\n"
                            "Spironolactone, eplerenone, amiloride, and triamterene act in the collecting duct and prevent "
                            "potassium wasting, at the cost of hyperkalemia; avoid them with other potassium-raising drugs.\n\n"
                            "## Complications\n"
                            "Volume depletion with AKI, hypokalemia with arrhythmia risk, metabolic alkalosis, hyponatremia "
                            "and hypomagnesemia, ototoxicity with high-dose intravenous furosemide, and the combination of "
                            "a diuretic, ACE inhibitor, and NSAID, the triple whammy that precipitates acute kidney injury."
                        ),
                        "duration_seconds": 240,
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025", "kdigo-aki-2012"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "board",
                        "case_text": "A patient with decompensated heart failure has a creatinine of 2.4 mg/dL and receives furosemide 200 mg IV with only 400 mL of urine output. The next day, euvolemia persists and creatinine is 2.6 mg/dL.",
                        "labs": {"cr": "2.4 mg/dL", "furosemide": "200 mg IV", "urine_output": "400 mL/day"},
                        "question_text": "What is the most appropriate next step for this patient with loop diuretic resistance?",
                        "explanation": "Furosemide has a ceiling effective intravenous dose of roughly 80 mg per dose, so going from 200 mg to 400 mg adds little, and the patient is clearly volume overloaded with an inadequate response. The correct next step is to add a thiazide-like diuretic acting at a different site, typically metolazone 2.5-5 mg orally 30-60 minutes before furosemide, which blocks compensatory sodium reabsorption in the distal convoluted tubule and restores diuresis. Electrolytes, creatinine, and blood pressure must be monitored closely because combining agents increases the risk of hypokalemia, hyponatremia, over-diuresis, and AKI.",
                        "clinical_pearl": "Furosemide plateaus above about 80 mg IV per dose. Break loop resistance with metolazone or chlorthalidone given before the loop diuretic.",
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025", "kdigo-aki-2012"],
                        "lesson_slug": "diuretic-prescribing",
                        "choices": [
                            ("A", "Add metolazone 2.5-5 mg orally before the furosemide dose and monitor electrolytes and renal function", True, None),
                            ("B", "Double furosemide to 400 mg IV", False, "Furosemide has a ceiling dose of about 80 mg IV; beyond that, increasing the dose adds toxicity, not diuresis."),
                            ("C", "Add spironolactone 50 mg daily", False, "Spironolactone helps if the problem is sodium retention, but with an inadequate response to a ceiling loop dose the priority is sequential nephron blockade with a thiazide-like agent."),
                            ("D", "Start intravenous saline to improve renal perfusion", False, "The patient is volume overloaded, not volume depleted; saline would worsen the congestion."),
                        ],
                    },
                    {
                        "difficulty": "hard",
                        "case_text": "A 79-year-old on ACE inhibitor, furosemide 40 mg daily, and intermittent NSAID use is admitted with community-acquired pneumonia. Creatinine rises from 1.5 to 3.0 mg/dL, and examination shows mild volume depletion with a jugular venous pressure that is low.",
                        "labs": {"cr": "1.5 to 3.0 mg/dL", "rx": "ACEi, furosemide, NSAID", "volume": "depleted"},
                        "question_text": "Which combination best explains and manages this AKI?",
                        "explanation": "This is the triple whammy: an ACE inhibitor reduces efferent arteriolar tone, a loop diuretic reduces perfusion by sodium and volume loss, and an NSAID inhibits prostaglandin-mediated afferent arteriolar dilation. The result is afferent constriction plus efferent dilation, which collapses glomerular filtration pressure and produces a marked creatinine rise. The management is to stop the NSAID, hold the diuretic during active volume depletion, and temporarily hold the ACE inhibitor, then reassess the trend; the ACE inhibitor can usually be restarted once creatinine returns toward baseline. Giving saline is appropriate for perfusion, and glucocorticoids are not indicated.",
                        "clinical_pearl": "Triple whammy (ACEi + diuretic + NSAID) causes hemodynamic AKI: stop the NSAID, hold the others briefly, give volume, then restart.",
                        "reference_ids": ["kdigo-aki-2012", "awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "loop-diuretics",
                        "choices": [
                            ("A", "The triple whammy of ACE inhibitor, diuretic, and NSAID; stop the NSAID, hold the diuretic, reassess after volume repletion, and then restart the ACE inhibitor", True, None),
                            ("B", "Acute tubular necrosis from sepsis; continue the current regimen and observe", False, "The pattern is hemodynamically mediated, not toxic tubular injury, and the contributing drugs must be changed."),
                            ("C", "Cardiorenal syndrome; increase furosemide and add a thiazide", False, "The patient is volume depleted with a low jugular venous pressure; forcing diuresis would worsen the kidney injury."),
                            ("D", "Chronic progression of heart failure; add an SGLT2 inhibitor and continue all current medications", False, "The AKI is hemodynamically mediated by a reversible drug combination and requires reversing that combination first."),
                        ],
                    },
                ],
            },
            {
                "title": "Nephrotoxicity",
                "slug": "nephrotoxicity",
                "description": "Aminoglycosides, contrast-associated AKI, and avoiding nephrotoxins.",
                "lessons": [
                    {
                        "title": "Avoiding Nephrotoxins",
                        "lesson_slug": "avoiding-nephrotoxins",
                        "lesson_type": "article",
                        "summary": "Contrast, aminoglycosides, NSAIDs, and other common nephrotoxins with prevention strategies.",
                        "content_md": (
                            "# Avoiding nephrotoxins\n\n"
                            "## Iodinated contrast\n"
                            "Contrast-associated AKI is usually non-oliguric AKI with a creatinine rise 24-72 hours after "
                            "exposure; it is generally reversible. Risk factors include pre-existing CKD, diabetes, "
                            "dehydration, heart failure, age, recent surgery, and concurrent nephrotoxins. Prevention relies "
                            "on limiting exposure, using the lowest effective contrast volume, avoiding concurrent NSAIDs, "
                            "and intravenous isotonic saline for at-risk patients. Sodium bicarbonate and N-acetylcysteine "
                            "have not shown consistent benefit and are not recommended as substitutes for hydration. "
                            "Prophylactic dialysis does not prevent contrast nephropathy.\n\n"
                            "## Aminoglycosides\n"
                            "Toxicity is predominantly proximal tubular injury, appearing 5-10 days into therapy as a "
                            "non-oliguric creatinine rise. Risk is increased by high trough levels, prolonged courses, "
                            "volume depletion, pre-existing kidney disease, and concurrent vancomycin, amphotericin, or "
                            "loop diuretics. Prevention: extended-interval dosing, trough monitoring, adequate hydration, "
                            "and limiting exposure.\n\n"
                            "## NSAIDs\n"
                            "Afferent arteriolar vasoconstriction, which precipitates AKI in volume depletion, heart failure, "
                            "CKD, and with ACEi or ARB use; they also cause minimal change disease with nephrotic syndrome, "
                            "papillary necrosis, and chronic interstitial nephritis.\n\n"
                            "## Others\n"
                            "Ifosfamide and platinum (tubular injury and magnesium wasting), tenofovir disoproxil "
                            "(proximal tubulopathy with phosphate wasting and Fanconi syndrome), lithium (chronic "
                            "interstitial nephritis, nephrogenic diabetes insipidus), calcineurin inhibitors, "
                            "indinavir, and gemcitabine. Also avoid dextrose-containing total parenteral nutrition without "
                            "thiamine in malnourished patients."
                        ),
                        "duration_seconds": 240,
                        "image_url": f"{MEDICAL_ASSET_BASE}/nephrology-pharmacology/toxic-alcohols-differential.webp",
                        "thumbnail_url": f"{MEDICAL_ASSET_BASE}/nephrology-pharmacology/toxic-alcohols-differential-thumb.webp",
                        "reference_ids": ["kdigo-ckd-2024", "kdigo-aki-2012"],
                    },
                    {
                        "title": "HIV and cART Nephrotoxicity",
                        "lesson_slug": "hiv-and-cart-nephrotoxicity",
                        "lesson_type": "article",
                        "summary": "Tenofovir and boosted protease inhibitor nephrotoxicity: tubular, crystal, and mitochondrial injury.",
                        "content_md": "Antiretroviral therapy can injure the kidney directly and through its metabolites, so drug toxicity belongs in the differential for any unexplained kidney disease in a patient with HIV.\n\nTenofovir disoproxil fumarate: the nucleotide analogue is preferentially concentrated in proximal tubular cells and causes mitochondrial DNA depletion. The presentation is a Fanconi-type tubulopathy with normoglycemic glycosuria, phosphate wasting, aminoaciduria, uricosuria, and a bland urine sediment, sometimes progressng to AKI.\n\nBoosted protease inhibitors and cobicistat: ritonavir and cobicistat inhibit tubular secretion, so they raise creatinine without reducing true GFR, and indinavir causes crystal nephropathy and painful colicky hematuria.\n\nPractical approach: confirm a true fall in GFR with cystatin C or a 24-hour creatinine clearance before labelling a stable rise as cART nephrotoxicity. Switch to tenofovir alafenamide or an alternative regimen when tubular injury is confirmed, and avoid the drug entirely in advanced CKD.",
                        "duration_seconds": 120,
                        "interactive_url": f"{MEDICAL_ASSET_BASE}/nephrology-pharmacology/hiv-cart-nephrotoxicity.html",
                        "reference_ids": ["awdishu-kdigo-ckd-pharm-2025", "kdigo-ckd-2024"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 68-year-old with baseline creatinine 2.6 mg/dL undergoes coronary angiography with 220 mL of contrast. Three days later the creatinine is 4.5 mg/dL with 1200 mL of urine output. He had been taking ibuprofen for osteoarthritis.",
                        "labs": {"cr_baseline": "2.6 mg/dL", "cr_post": "4.5 mg/dL", "urine_output": "1200 mL", "contrast": "220 mL"},
                        "question_text": "Which intervention is most appropriate?",
                        "explanation": "A creatinine rise 24-72 hours after contrast in a patient with pre-existing CKD, baseline creatinine above 2.5 mg/dL, and concurrent NSAID exposure is contrast-associated AKI, typically non-oliguric as here. It is generally reversible, so management is supportive: intravenous isotonic saline, avoidance of further contrast and of NSAIDs, withholding nephrotoxins, and monitoring to a nadir and recovery over 7-10 days. Diuretics do not prevent or treat it, and prophylactic hemodialysis is not indicated. Prevention for future procedures includes minimizing contrast volume, ensuring euvolemia, holding NSAIDs and ACE inhibitors around the procedure, and using the lowest necessary contrast dose.",
                        "clinical_pearl": "Contrast AKI is usually non-oliguric and reversible: isotonic saline, stop NSAIDs, no prophylactic dialysis, minimize future contrast.",
                        "reference_ids": ["kdigo-ckd-2024"],
                        "lesson_slug": "avoiding-nephrotoxins",
                        "choices": [
                            ("A", "Supportive care with intravenous isotonic saline, stopping ibuprofen, and monitoring; do not start prophylactic dialysis", True, None),
                            ("B", "Start furosemide to force diuresis and protect the kidney", False, "Diuretics neither prevent nor treat contrast-associated AKI, and forced diuresis in this setting can worsen the injury."),
                            ("C", "Begin a course of N-acetylcysteine for 3 days to prevent progression", False, "N-acetylcysteine has not shown consistent benefit and should not substitute for hydration and risk reduction."),
                            ("D", "Start intravenous hemodialysis because the creatinine has doubled", False, "Dialysis is reserved for standard indications; most contrast AKI recovers without it."),
                        ],
                    },
                    {
                        "difficulty": "medium",
                        "case_text": "A 79-year-old with a prosthetic hip infection is treated with vancomycin and gentamicin for 4 weeks. On day 8 his creatinine rises from 1.0 to 2.2 mg/dL with 1500 mL of urine output. Urinalysis shows granular casts and no eosinophiluria; gentamicin troughs have been 12 mg/L.",
                        "labs": {"cr": "1.0 to 2.2 mg/dL", "gent_trough": "12 mg/L", "uo": "1500 mL", "ua": "granular casts"},
                        "question_text": "Which statement about this kidney injury is most accurate?",
                        "explanation": "A non-oliguric creatinine rise 8 days into aminoglycoside therapy with granular casts and elevated troughs (12 mg/L, well above the target of under 2 mg/L for extended-interval dosing) is aminoglycoside-induced acute tubular necrosis. The toxicity is proximal tubular injury, which is usually reversible if recognized early; risk is increased by high trough levels, length of therapy, and concurrent vancomycin, an important interaction here. Management is to reduce or stop gentamicin, monitor levels and renal function, ensure hydration, and choose an alternative agent or extended-interval dosing. Distinguishing it from interstitial nephritis matters because the management is the same, but the non-oliguric course, timing, and elevated troughs favor tubular injury.",
                        "clinical_pearl": "Aminoglycoside ATN is non-oliguric, appears at 5-10 days, and is driven by high troughs and concurrent vancomycin.",
                        "reference_ids": ["kdigo-aki-2012", "awdishu-kdigo-ckd-pharm-2025"],
                        "lesson_slug": "avoiding-nephrotoxins",
                        "choices": [
                            ("A", "Aminoglycoside-induced acute tubular necrosis: stop or reduce gentamicin, use extended-interval dosing with level monitoring, and provide supportive care", True, None),
                            ("B", "Acute interstitial nephritis from vancomycin, requiring corticosteroids", False, "Vancomycin-associated AIN is less common and typically shows eosinophiluria and proteinuria; the non-oliguric course with high gentamicin troughs indicates tubular toxicity."),
                            ("C", "Prerenal azotemia from diarrhea, requiring oral fluids only", False, "The urinary output of 1500 mL/day and granular casts indicate intrinsic tubular injury rather than pure prerenal azotemia."),
                            ("D", "Volume overload from the saline load, requiring furosemide", False, "There is no evidence of volume overload; the injury is drug-induced tubular damage."),
                        ],
                    },
                ],
            },
            {
                "title": "RAAS Blockade and Hyperkalemia",
                "slug": "raas-hyperkalemia",
                "description": "Managing ACEi/ARB-associated hyperkalemia without abandoning renoprotection.",
                "lessons": [
                    {
                        "title": "RAAS Blockade and Hyperkalemia",
                        "lesson_slug": "raas-blockade-and-hyperkalemia",
                        "lesson_type": "article",
                        "summary": "Prevention and stepwise management of hyperkalemia on ACE inhibitors or ARBs.",
                        "content_md": (
                            "# RAAS blockade and hyperkalemia\n\n"
                            "## The tension\n"
                            "ACE inhibitors and ARBs reduce albuminuria and slow progression in albuminuric CKD, so "
                            "hyperkalemia is usually managed without stopping the drug. Potassium is also affected by pH, "
                            "with acidosis shifting potassium out of cells, and by medications that raise it: NSAIDs, "
                            "trimethoprim, calcineurin inhibitors, potassium supplements, and salt substitutes.\n\n"
                            "## Management ladder\n"
                            "1. Review diet and potassium-containing salt substitutes, supplements, and drugs such as "
                            "trimethoprim, NSAIDs, and potassium binders; also correct acidosis\n"
                            "2. Add a loop or thiazide diuretic if the patient is not volume overloaded and can tolerate it\n"
                            "3. Use a beta-2 agonist (albuterol) or a bicarbonate infusion for a temporary shift\n"
                            "4. Start a potassium binder: sodium zirconium cyclosilicate or patiromer for chronic control, "
                            "sodium polystyrene sulfonate as a short-term measure\n"
                            "5. Reduce the dose or stop the ACE inhibitor or ARB only if the above fail or if potassium is "
                            "persistently above about 6.0 mEq/L; consider substituting a nonsteroidal mineralocorticoid "
                            "receptor antagonist such as finerenone where appropriate\n\n"
                            "## Monitoring\n"
                            "Check potassium and creatinine 1-2 weeks after initiation and after each dose change."
                        ),
                        "duration_seconds": 210,
                        "reference_ids": ["kdigo-ckd-2024", "aha-hyperk-2015"],
                    },
                ],
                "mcqs": [
                    {
                        "difficulty": "hard",
                        "case_text": "A 70-year-old with CKD G3b and UACR 500 mg/g on lisinopril 20 mg has potassium rising to 5.9 mEq/L. He was recently prescribed trimethoprim for a urinary infection and takes a potassium-based salt substitute. ECG shows peaked T waves.",
                        "labs": {"k": "5.9 mEq/L", "uacr": "500 mg/g", "egfr": "38 mL/min/1.73m2", "ecg": "peaked T waves", "drugs": "trimethoprim, salt substitute"},
                        "question_text": "What is the most appropriate management of this hyperkalemia while preserving renoprotection?",
                        "explanation": "The patient has significant hyperkalemia with ECG changes, plus two reversible contributors: trimethoprim acts like a potassium-sparing diuretic and blocks tubular potassium excretion, and a potassium-based salt substitute adds a large potassium load. The immediate management is to stop both contributors, stabilize the cardiac membrane with intravenous calcium if the ECG changes are significant, shift potassium with insulin and glucose or a beta-2 agonist, and remove potassium with a loop diuretic, a potassium binder, or dialysis. Because albuminuric CKD needs RAAS blockade for renoprotection, the ACE inhibitor is reduced or temporarily held only after reversible causes are corrected, and a potassium binder such as patiromer or sodium zirconium cyclosilicate is started to allow continued therapy.",
                        "clinical_pearl": "Hyperkalemia on an ACEi: stop the culprits (trimethoprim, salt substitute, NSAIDs), stabilize, shift, remove potassium, then protect the ACEi with a binder.",
                        "reference_ids": ["kdigo-ckd-2024", "aha-hyperk-2015"],
                        "lesson_slug": "raas-blockade-and-hyperkalemia",
                        "choices": [
                            ("A", "Stop trimethoprim and the salt substitute, stabilize the membrane, shift and remove potassium, and start a potassium binder so lisinopril can be continued at the lowest effective dose", True, None),
                            ("B", "Stop lisinopril permanently and replace it with a calcium channel blocker", False, "Abandoning RAAS blockade in albuminuric CKD removes antiproteinuric benefit; reversible causes and potassium-lowering strategies should be used first."),
                            ("C", "Continue trimethoprim and start a potassium binder only", False, "Trimethoprim is a key reversible contributor; it should be stopped and the antibiotic changed."),
                            ("D", "Increase lisinopril to control the blood pressure and recheck potassium in 1 month", False, "Increasing an ACEi during hyperkalemia with ECG changes would be dangerous."),
                        ],
                    },
                ],
            },
        ],
    },
]
