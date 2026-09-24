
INSERT INTO chapters (title, slug, order_index, description)
VALUES
('Acid-Base Disorders', 'acid-base-disorders', 1, 'ABG interpretation and acid-base board questions.'),
('Electrolytes', 'electrolytes', 2, 'Sodium, potassium, calcium, phosphate, and magnesium.'),
('AKI', 'aki', 3, 'Prerenal, intrinsic, postrenal AKI and RRT.'),
('CKD', 'ckd', 4, 'CKD staging, anemia, MBD, and progression.'),
('Glomerular Diseases', 'glomerular-diseases', 5, 'Nephritic and nephrotic syndromes.'),
('Dialysis', 'dialysis', 6, 'Hemodialysis, PD, adequacy, access, and complications.');

WITH ch AS (
  SELECT id FROM chapters WHERE slug='electrolytes'
),
q AS (
  INSERT INTO mcqs (
    chapter_id, difficulty, question_stem, clinical_case, labs,
    correct_choice_key, explanation, clinical_pearl, reference
  )
  SELECT
    ch.id,
    'board',
    'A patient with ESRD presents with weakness and peaked T waves. Potassium is 6.9 mEq/L. What is the best immediate next step?',
    'A 64-year-old man on hemodialysis missed dialysis and presents with weakness. ECG shows peaked T waves.',
    '{"Na":"138","K":"6.9","HCO3":"18","BUN":"82","Cr":"9.4"}'::jsonb,
    'B',
    'Severe hyperkalemia with ECG changes requires immediate cardiac membrane stabilization with IV calcium before shifting or removing potassium.',
    'In hyperkalemia with ECG changes, give IV calcium first.',
    'Educational board-style reference'
  FROM ch
  RETURNING id
)
INSERT INTO mcq_choices (mcq_id, choice_key, choice_text, why_wrong)
SELECT id, 'A', 'Sodium polystyrene sulfonate', 'Too slow and not appropriate as immediate stabilization.' FROM q
UNION ALL SELECT id, 'B', 'IV calcium gluconate', NULL FROM q
UNION ALL SELECT id, 'C', 'Oral patiromer', 'Too slow for emergency hyperkalemia.' FROM q
UNION ALL SELECT id, 'D', 'Restrict dietary potassium only', 'Not adequate for life-threatening hyperkalemia.' FROM q;
