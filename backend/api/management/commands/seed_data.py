import random

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from api.models import Category, Choice, Question, User

CATEGORIES = [
    {
        "name": "Glomerular Diseases",
        "description": "Diseases affecting the glomeruli including nephrotic and nephritic syndromes.",
        "icon": "filter",
        "order": 1,
    },
    {
        "name": "Acute Kidney Injury",
        "description": "Sudden loss of kidney function, including prerenal, intrinsic, and postrenal causes.",
        "icon": "alert-triangle",
        "order": 2,
    },
    {
        "name": "Chronic Kidney Disease",
        "description": "Progressive loss of kidney function over months to years.",
        "icon": "clock",
        "order": 3,
    },
    {
        "name": "Electrolyte Disorders",
        "description": "Disorders of sodium, potassium, calcium, phosphate, and magnesium homeostasis.",
        "icon": "activity",
        "order": 4,
    },
    {
        "name": "Acid-Base Disorders",
        "description": "Metabolic and respiratory acid-base disturbances.",
        "icon": "thermometer",
        "order": 5,
    },
    {
        "name": "Hypertension",
        "description": "Primary and secondary hypertension, including renovascular disease.",
        "icon": "heart",
        "order": 6,
    },
    {
        "name": "Dialysis",
        "description": "Hemodialysis and peritoneal dialysis principles and complications.",
        "icon": "repeat",
        "order": 7,
    },
    {
        "name": "Transplantation",
        "description": "Kidney transplantation immunology, immunosuppression, and complications.",
        "icon": "shuffle",
        "order": 8,
    },
    {
        "name": "Tubulointerstitial Diseases",
        "description": "Diseases affecting renal tubules and interstitium.",
        "icon": "box",
        "order": 9,
    },
    {
        "name": "Pharmacology",
        "description": "Drug dosing in kidney disease, nephrotoxic medications, and diuretics.",
        "icon": "pill",
        "order": 10,
    },
]

SAMPLE_QUESTIONS = [
    {
        "category_name": "Glomerular Diseases",
        "subcategory": "Nephrotic Syndrome",
        "difficulty": "medium",
        "question_text": "A 6-year-old boy presents with periorbital edema and frothy urine. Urinalysis shows 3+ protein and no hematuria. Serum albumin is 2.0 g/dL. Which of the following is the most likely diagnosis?",
        "explanation": "Minimal change disease is the most common cause of nephrotic syndrome in children. It typically presents with heavy proteinuria, hypoalbuminemia, and edema without hematuria or hypertension. It usually responds well to corticosteroids.",
        "clinical_pearl": "Minimal change disease accounts for 80-90% of nephrotic syndrome in children under 10 years.",
        "choices": [
            ("Focal segmental glomerulosclerosis", False),
            ("Minimal change disease", True),
            ("Membranous nephropathy", False),
            ("IgA nephropathy", False),
            ("Membranoproliferative glomerulonephritis", False),
        ],
    },
    {
        "category_name": "Acute Kidney Injury",
        "subcategory": "Prerenal AKI",
        "difficulty": "easy",
        "question_text": "A 70-year-old man with CHF develops AKI after aggressive diuresis. Which of the following lab findings is most consistent with prerenal AKI?",
        "explanation": "Prerenal AKI shows a high BUN:Cr ratio (>20:1), low urine sodium (<20 mEq/L), high urine osmolality (>500 mOsm/kg), and low fractional excretion of sodium (FENa <1%). These findings indicate preserved tubular function with decreased renal perfusion.",
        "clinical_pearl": "FENa = (Urine Na × Plasma Cr / Plasma Na × Urine Cr) × 100. FENa <1% suggests prerenal cause.",
        "choices": [
            ("FENa > 3% and urine osmolality 300 mOsm/kg", False),
            ("FENa < 1% and urine osmolality > 500 mOsm/kg", True),
            ("FENa > 2% and urine sodium > 40 mEq/L", False),
            ("Urine sodium > 40 mEq/L and BUN:Cr ratio < 10:1", False),
            ("FENa 2-3% with muddy brown casts", False),
        ],
    },
    {
        "category_name": "Electrolyte Disorders",
        "subcategory": "Hyperkalemia",
        "difficulty": "hard",
        "question_text": "A 55-year-old diabetic patient on an ACE inhibitor presents with muscle weakness and ECG showing peaked T waves. Labs: K+ 6.8 mEq/L, Cr 2.5 mg/dL. Which of the following is the most appropriate initial treatment?",
        "explanation": "With life-threatening hyperkalemia (K+ >6.5 or ECG changes), the first step is to stabilize the cardiac membrane with IV calcium gluconate or calcium chloride. This does not lower potassium but protects the heart. Then shift potassium intracellularly with insulin + glucose, and ultimately remove potassium with dialysis or loop diuretics.",
        "clinical_pearl": "Calcium gluconate should be given first in hyperkalemia with ECG changes — it acts within 1-3 minutes and lasts 30-60 minutes.",
        "choices": [
            ("Intravenous calcium gluconate", True),
            ("Sodium polystyrene sulfonate", False),
            ("Hemodialysis", False),
            ("Albuterol nebulization", False),
            ("Intravenous furosemide", False),
        ],
    },
    {
        "category_name": "Acid-Base Disorders",
        "subcategory": "Metabolic Acidosis",
        "difficulty": "medium",
        "question_text": "A 30-year-old woman with type 1 diabetes presents with nausea, vomiting, and deep rapid breathing. ABG shows pH 7.15, PCO2 25 mmHg, HCO3 8 mEq/L. What is the appropriate interpretation?",
        "explanation": "The pH indicates acidemia (7.15). The primary disorder is metabolic acidosis (low HCO3 8). The expected respiratory compensation is PCO2 = (1.5 × HCO3) + 8 ± 2 = 20 ± 2. The actual PCO2 of 25 is slightly higher than expected, indicating a concurrent respiratory acidosis or incomplete compensation.",
        "clinical_pearl": "For metabolic acidosis, use Winter's formula: Expected PCO2 = (1.5 × HCO3) + 8 ± 2. If measured PCO2 is higher, there is concurrent respiratory acidosis.",
        "choices": [
            ("Metabolic alkalosis with respiratory compensation", False),
            ("Respiratory acidosis with renal compensation", False),
            ("Metabolic acidosis with appropriate respiratory compensation", False),
            ("Metabolic acidosis with concurrent respiratory acidosis", True),
            ("Respiratory alkalosis with metabolic compensation", False),
        ],
    },
    {
        "category_name": "Chronic Kidney Disease",
        "subcategory": "CKD-MBD",
        "difficulty": "hard",
        "question_text": "A 60-year-old man with CKD stage 4 has a serum phosphate of 6.5 mg/dL, calcium 8.2 mg/dL, and PTH 350 pg/mL. Which of the following is the most appropriate management?",
        "explanation": "In CKD-MBD, management begins with phosphate restriction and phosphate binders. Elevated PTH in the setting of high phosphate and low calcium suggests secondary hyperparathyroidism. First-line treatment includes dietary phosphate restriction and phosphate binders (calcium-based or non-calcium-based). Cinacalcet or calcitriol may be used if PTH remains elevated.",
        "clinical_pearl": "Targets in CKD-MBD: Phosphate 2.5-4.5 mg/dL, Calcium 8.4-9.5 mg/dL, PTH 2-9× upper normal for CKD stage 4.",
        "choices": [
            ("Immediate parathyroidectomy", False),
            ("Calcium carbonate and dietary phosphate restriction", True),
            ("Intravenous calcitriol", False),
            ("Sevelamer carbonate and phosphate supplementation", False),
            ("No intervention needed at this stage", False),
        ],
    },
    {
        "category_name": "Dialysis",
        "subcategory": "Hemodialysis Complications",
        "difficulty": "medium",
        "question_text": "A patient on hemodialysis develops headache, nausea, and confusion during the last hour of treatment. Blood pressure is 180/100 mmHg. What is the most likely diagnosis?",
        "explanation": "Dialysis disequilibrium syndrome occurs due to rapid removal of urea leading to cerebral edema. It typically presents near the end of dialysis with headache, nausea, vomiting, hypertension, and in severe cases, seizures and coma. It is more common in new dialysis patients or those with high BUN. Treatment is supportive; prevention includes shorter, more frequent sessions.",
        "clinical_pearl": "Dialysis disequilibrium syndrome is more common in new dialysis patients with BUN > 150-200 mg/dL. Use low-efficiency dialysis initially.",
        "choices": [
            ("Intradialytic hypotension", False),
            ("Dialysis disequilibrium syndrome", True),
            ("Air embolism", False),
            ("Hemolysis from dialyzer malfunction", False),
            ("First-use syndrome", False),
        ],
    },
    {
        "category_name": "Transplantation",
        "subcategory": "Immunosuppression",
        "difficulty": "hard",
        "question_text": "A renal transplant recipient develops acute rejection. Which of the following immunosuppressive agents works by inhibiting calcineurin?",
        "explanation": "Calcineurin inhibitors (CNIs) are cyclosporine and tacrolimus. They inhibit calcineurin, preventing NFAT activation and IL-2 production, thereby suppressing T-cell activation. Sirolimus is an mTOR inhibitor, mycophenolate mofetil inhibits inosine monophosphate dehydrogenase, and belatacept is a co-stimulation blocker.",
        "clinical_pearl": "Calcineurin inhibitors cause nephrotoxicity, hypertension, and hyperkalemia. Trough levels must be monitored carefully.",
        "choices": [
            ("Mycophenolate mofetil", False),
            ("Sirolimus", False),
            ("Belatacept", False),
            ("Tacrolimus", True),
            ("Rituximab", False),
        ],
    },
    {
        "category_name": "Hypertension",
        "subcategory": "Secondary Hypertension",
        "difficulty": "medium",
        "question_text": "A 35-year-old woman with hypertension and hypokalemia is found to have a renal artery bruit on exam. Which of the following is the most appropriate screening test?",
        "explanation": "Renovascular hypertension should be suspected in young patients with hypertension, hypokalemia, and an abdominal bruit. The best screening test is Doppler ultrasound of renal arteries or CT/MR angiography. Captopril renography can also be used but is less common now.",
        "clinical_pearl": "Think renovascular hypertension in: age <30 with hypertension, abrupt onset, refractory HTN, or unexplained hypokalemia.",
        "choices": [
            ("Plasma renin activity and aldosterone levels", False),
            ("Renal artery duplex ultrasound", True),
            ("Intravenous pyelogram", False),
            ("Renal biopsy", False),
            ("24-hour urine catecholamines", False),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the database with initial categories and sample questions."

    def handle(self, *args, **options):
        self._create_admin_user()
        self._create_categories()
        self._create_sample_questions()
        self.stdout.write(self.style.SUCCESS("Data seeded successfully!"))

    def _create_admin_user(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@nephrochallenge.com",
                password="admin123",
                role="admin",
            )
            self.stdout.write("Admin user created (admin / admin123)")

    def _create_categories(self):
        for cat_data in CATEGORIES:
            Category.objects.get_or_create(
                slug=slugify(cat_data["name"]),
                defaults=cat_data,
            )
        self.stdout.write(f"Created {len(CATEGORIES)} categories")

    def _create_sample_questions(self):
        for q_data in SAMPLE_QUESTIONS:
            category = Category.objects.filter(
                slug=slugify(q_data["category_name"])
            ).first()
            if not category:
                self.stdout.write(f"Skipping - category not found: {q_data['category_name']}")
                continue
            question, created = Question.objects.get_or_create(
                question_text=q_data["question_text"],
                defaults={
                    "category": category,
                    "subcategory": q_data["subcategory"],
                    "difficulty": q_data["difficulty"],
                    "explanation": q_data["explanation"],
                    "clinical_pearl": q_data["clinical_pearl"],
                    "is_published": True,
                },
            )
            if created:
                for i, (choice_text, is_correct) in enumerate(q_data["choices"]):
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct,
                        order=i + 1,
                    )
        self.stdout.write(f"Created {len(SAMPLE_QUESTIONS)} sample questions")
