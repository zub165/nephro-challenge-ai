# 🧠 Nephro Challenge AI — Medical Quiz & Learning Platform

**Nephro Challenge AI** is a full-stack medical quiz application designed for nephrologists, internal medicine physicians, residents, fellows, and medical students. It combines board-style questions with AI-powered explanations to make learning nephrology and internal medicine engaging and effective.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.2 + Django REST Framework |
| **Web Frontend** | React 18 + Vite + TypeScript + Tailwind CSS |
| **Mobile** | Flutter (Android & iOS) |
| **Database** | PostgreSQL |
| **Auth** | JWT (SimpleJWT) + Google/Apple OAuth |
| **AI** | OpenAI GPT API for explanations & question generation |
| **API Docs** | drf-spectacular (Swagger/OpenAPI) |
| **State (Web)** | Zustand + React Query |
| **State (Mobile)** | Provider |
| **Charts** | Recharts (web), fl_chart (mobile) |

---

## 📁 Project Structure

```
nephro-challenge-ai/
├── backend/                    # Django REST API
│   ├── nephro_challenge/       # Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                    # Main API app
│   │   ├── models.py           # User, Question, Category, QuizAttempt, etc.
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # ViewSets and APIViews
│   │   ├── urls.py             # API routes
│   │   ├── permissions.py      # Custom permissions
│   │   ├── admin.py            # Django admin config
│   │   ├── services/
│   │   │   └── ai_service.py   # OpenAI integration
│   │   └── management/commands/
│   │       └── seed_data.py    # Seed sample data
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── web/                        # React admin panel & web app
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── store/              # Zustand stores
│   │   ├── lib/                # Axios config
│   │   └── types/              # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── mobile/                     # Flutter mobile app
│   ├── lib/
│   │   ├── config/             # Theme, constants, routes
│   │   ├── models/             # Data models
│   │   ├── services/           # API services
│   │   ├── providers/          # State management
│   │   ├── screens/            # All screens
│   │   └── widgets/            # Reusable widgets
│   ├── pubspec.yaml
│   └── analysis_options.yaml
├── context.md                  # This file
└── README.md
```

---

## 🎮 Game Modes

### 1. Daily Case Challenge
One new case every day with a streak counter. Answer diagnosis, next step, treatment, and clinical reasoning questions.

### 2. Board Review Mode
Category-based question banks covering:
- Internal Medicine, Nephrology, Acid-Base, Electrolytes, Dialysis
- Hypertension, AKI/CKD, Glomerulonephritis, Transplant, Critical Care Nephrology

### 3. Case Duel Mode *(Future)*
Live head-to-head competition — accuracy, speed, and streak-based scoring.

### 4. Image / Lab Interpretation
BMP, ABG, Urinalysis, Microscopy, ECG, CXR, Renal Ultrasound.

### 5. AI Tutor Mode
After each question, ask AI to:
- Explain simpler
- Explain why other options are wrong
- Show a clinical pearl
- Generate a similar question
- Give a board-style summary

---

## 👥 User Roles

| Role | Access |
|------|--------|
| **Guest** | Limited daily questions, no progress saved |
| **Free** | Daily challenge, limited bank, basic AI, basic leaderboard |
| **Premium** | Unlimited questions, full AI tutor, full review, custom quizzes, duel mode, saved notes |
| **Admin/Editor** | Create/edit questions, review AI questions, manage categories, monitor flags |

---

## 🔐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login, returns JWT |
| GET | `/api/auth/profile/` | Get user profile |
| PATCH | `/api/auth/profile/` | Update profile |
| GET | `/api/categories/` | List categories |
| GET | `/api/questions/` | List questions (filterable) |
| GET | `/api/questions/random/` | Random question |
| GET | `/api/questions/daily/` | Daily challenge question |
| POST | `/api/quiz/` | Submit quiz attempt |
| GET | `/api/leaderboard/` | Get leaderboard |
| GET | `/api/leaderboard/my-rank/` | Get user's rank |
| POST | `/api/ai/explain/` | Get AI explanation |
| POST | `/api/ai/generate/` | Generate question via AI |
| GET | `/api/weaknesses/` | Get weak topics |
| GET | `/api/docs/` | Swagger API docs |

---

## 🧠 Data Models

- **User** — email, role (guest/free/premium/admin), specialty, streak, XP, rank
- **Category** — name, slug, icon, order (e.g., Nephrology, Acid-Base)
- **Question** — category, difficulty, case_text, labs (JSON), choices, explanation, clinical_pearl
- **Choice** — question FK, text, is_correct, order
- **QuizAttempt** — user FK, score, questions count, time taken
- **Answer** — attempt FK, question FK, chosen choice, correctness
- **Leaderboard** — user FK, score, period (daily/weekly/monthly/all)
- **Subscription** — user FK, plan, dates
- **AIGeneratedQuestion** — AI-drafted questions pending admin review
- **SavedPearl** — user-saved clinical pearls

---

## 🎨 Design

- **Colors**: Deep blue `#1e3a5f`, Teal `#0d9488`, White background
- **Feedback**: Green (correct), Red (incorrect), Amber (review)
- **Features**: Dark/light mode, large readable fonts, animations, responsive
- **Displays**: Progress badges, streaks, XP bars, performance charts

---

## ⚙️ Setup & Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Web Frontend
```bash
cd web
npm install
npm run dev
```

### Mobile (Flutter)
```bash
cd mobile
flutter pub get
flutter run
```

---

## 🛡️ Safety & Compliance

- **Disclaimer**: "For medical education only. Not medical advice." displayed throughout
- **PHI Warning**: Users warned not to submit identifiable patient information
- **Admin Review**: All AI-generated questions must be approved before publication
- **No PHI Stored**: Architecture designed to avoid protected health information

---

## 💰 Monetization

- **Free Tier**: Limited daily questions
- **Premium Monthly**: $6.99–$14.99
- **Annual**: Discounted subscription
- **Institutional**: Residency program plans
- **Future**: CME credit packages

---

> Built with ❤️ for the nephrology community.
