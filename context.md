# 🧠 Nephro Challenge AI — Medical Quiz & Learning Platform

**Nephro Challenge AI** is a full-stack medical quiz application designed for nephrologists, internal medicine physicians, residents, fellows, and medical students. It combines board-style MCQs with chapter-wise animated learning and AI-powered explanations to make nephrology review engaging and effective.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.2 + Django REST Framework |
| **Web Frontend** | React 18 + Vite + TypeScript + Tailwind CSS |
| **Mobile** | Flutter (Android & iOS) |
| **Database** | PostgreSQL |
| **Animation Storage** | Cloudflare R2 / AWS S3 / CDN (URLs only in DB) |
| **Auth** | JWT (SimpleJWT) + Google/Apple OAuth (mobile) |
| **AI** | LLaMA on GoDaddy VPS (Ollama) with optional OpenAI fallback |
| **API Docs** | drf-spectacular (Swagger/OpenAPI at `/api/docs/`) |
| **State (Web)** | Zustand (persisted auth) + TanStack React Query |
| **State (Mobile)** | Provider + flutter_secure_storage / shared_preferences |
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
│   │   ├── models.py           # User, Chapter, Topic, Lesson, Question, etc.
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── admin.py
│   │   ├── migrations/         # Django migrations (run makemigrations/migrate)
│   │   ├── data/
│   │   │   └── chapter_seed.py # Chapter-wise MCQ + animation seed data
│   │   ├── services/
│   │   │   └── ai_service.py
│   │   └── management/commands/
│   │       └── seed_data.py    # Categories, chapters, topics, lessons, MCQs
│   ├── docs/                   # Backend plan & reference
│   │   ├── README.md           # Django setup + API table
│   │   ├── schema.sql          # Raw PostgreSQL schema
│   │   ├── seed.sql            # SQL starter seed
│   │   ├── api-plan.md         # Frontend/backend API contract
│   │   └── sample-mcq.json     # Bulk MCQ import format
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── web/                        # React web app (v1.1.0)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/              # Dashboard, Chapters, Quiz, Admin, etc.
│   │   ├── store/              # Zustand auth (localStorage)
│   │   ├── lib/                # Axios + apiMappers
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts          # Dev proxy → localhost:8000
│   └── tailwind.config.js
├── mobile/                     # Flutter mobile app
│   ├── lib/
│   │   ├── config/
│   │   ├── models/
│   │   ├── services/           # API + hybrid local storage
│   │   ├── providers/
│   │   ├── screens/
│   │   └── widgets/
│   ├── pubspec.yaml
│   └── analysis_options.yaml
├── context.md                  # This file
└── README.md
```

---

## 🎮 Game Modes

### 1. Daily Case Challenge
One new case every day with a streak counter. Deterministic daily question seeded by date.

### 2. Board Review — Chapter-wise MCQs
Structured learning path:

**Chapter → Topic → Lesson (animation) → MCQ quiz**

Starter chapters (seeded):
- Acid-Base Disorders
- Electrolytes
- Acute Kidney Injury (AKI)
- Chronic Kidney Disease (CKD)
- Glomerular Diseases
- Dialysis

Legacy category-based practice remains available via `/categories`.

### 3. Practice / Category Quiz
Random questions filtered by category or chapter.

### 4. Case Duel Mode *(Future)*
Live head-to-head competition — accuracy, speed, and streak-based scoring.

### 5. Image / Lab Interpretation *(Future)*
BMP, ABG, Urinalysis, Microscopy, ECG, CXR, Renal Ultrasound.

### 6. AI Tutor Mode
After each question, ask AI to explain, show pearls, or generate similar questions.

---

## 👥 User Roles

| Role | Access |
|------|--------|
| **Guest** | Limited daily questions, no progress saved |
| **Free** | Daily challenge, chapter MCQs, basic leaderboard |
| **Premium** | Unlimited questions, full AI tutor, premium lessons |
| **Admin** | Create/edit content, import MCQs, review AI questions |

---

## 🗄️ Data Architecture

### PostgreSQL (source of truth)
Stores MCQs, chapters, topics, lesson metadata, quiz attempts, and user progress.

### Animation storage (external CDN)
**Do not store animation files in PostgreSQL.**

| Stored in DB | Stored on CDN (R2/S3) |
|--------------|------------------------|
| `animation_url` | Lottie JSON / MP4 files |
| `thumbnail_url` | Preview images |
| `title`, `summary`, `content_md` | — |

Example URL: `https://cdn.nephrochallenge.ai/animations/hyperkalemia-algorithm.json`

### Hybrid local storage (clients)

| Client | Local storage | Backend sync |
|--------|---------------|--------------|
| **Web** | JWT + user in `localStorage` (`nephro-auth` via Zustand persist) | Quiz attempts, stats, progress |
| **Mobile** | Secure tokens, preferences, daily challenge date | Quiz attempts, leaderboard, profile |

---

## 🧠 Data Models

### Content hierarchy
- **Category** — legacy topic grouping (name, slug, icon, order)
- **Chapter** — board-review chapter (title, slug, order_index, description, icon)
- **Topic** — sub-topic within a chapter (e.g. Hyperkalemia under Electrolytes)
- **Lesson** — learning unit (animation/article/video); `animation_url` points to CDN
- **Question** — MCQ linked to category + optional chapter/topic/lesson
- **Choice** — `choice_key` (A/B/C/D), `choice_text`, `why_wrong`, `is_correct`

### User & quiz
- **User** — username, email, role, specialty, streak, XP, rank
- **QuizAttempt** — mode (daily/practice/chapter/category), score, chapter/topic FKs
- **Answer** — per-question response with correctness and time taken
- **Leaderboard** — score by period (daily/weekly/monthly/all_time)
- **Subscription** — plan and dates
- **AIGeneratedQuestion** — AI drafts pending admin review
- **SavedPearl** — user-saved clinical pearls

### Django ↔ SQL schema mapping

| `backend/docs/schema.sql` | Django model |
|---------------------------|--------------|
| `chapters` | `Chapter` |
| `topics` | `Topic` |
| `lessons` | `Lesson` |
| `mcqs` | `Question` |
| `mcq_choices` | `Choice` |
| `quiz_attempts` | `QuizAttempt` |
| `user_answers` | `Answer` |

---

## 🔐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register; returns `access`, `refresh`, `token`, `user` |
| POST | `/api/auth/login/` | Login with `email` or `username`; returns JWT |
| GET/PATCH | `/api/auth/profile/` | User profile |

### Chapters & learning content
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chapters/` | All chapters with topic/lesson/MCQ counts |
| GET | `/api/chapters/:slug/` | Chapter detail + topics |
| GET | `/api/chapters/:slug/topics/` | Topics and lessons under chapter |
| GET | `/api/topics/:id/` | Topic detail + lessons |
| GET | `/api/topics/:id/lessons/` | Lessons with animation URLs |
| GET | `/api/lessons/:id/` | Single lesson + chapter context |

### Quiz & questions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| GET | `/api/questions/` | List published questions (filterable) |
| GET | `/api/questions/quiz/` | Frontend quiz loader (`daily`, `categoryId`, `chapterId`) |
| GET | `/api/quiz/daily/` | Today's MCQ |
| GET | `/api/quiz/chapter/:id/?limit=10` | Chapter MCQs |
| POST | `/api/quiz/answer/` | Check answer; returns explanation + pearl |
| GET | `/api/quiz/explanation/:id/` | Full explanation + why-wrong per choice |
| POST | `/api/attempts/` | Submit quiz attempt with `answers_data` |
| GET | `/api/daily-challenge/` | Daily challenge question |

### User progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/` | Dashboard stats (alias) |
| GET | `/api/users/me/progress/` | Accuracy, streak, weak chapters, activity |
| GET | `/api/weaknesses/` | Weak topics by incorrect count |

### Leaderboard & AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leaderboard/` | Rankings by period |
| GET | `/api/leaderboard/user_rank/` | Current user rank |
| POST | `/api/ai/explain/` | AI explanation (LLaMA on VPS or OpenAI) |
| POST | `/api/ai/generate/` | Generate draft question via AI |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/import-mcqs/` | Bulk import from `sample-mcq.json` format |
| Django Admin | `/admin/` | Full CRUD for chapters, topics, lessons, questions |

### Docs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI schema |

---

## 📦 Sample MCQ Import Format

See `backend/docs/sample-mcq.json`:

```json
{
  "chapter": "Electrolytes",
  "topic": "Hyperkalemia",
  "lesson": {
    "title": "Emergency Hyperkalemia Algorithm",
    "lesson_type": "animation",
    "summary": "Fast visual algorithm for stabilizing, shifting, and removing potassium.",
    "animation_url": "https://cdn.nephrochallenge.ai/animations/hyperkalemia-algorithm.json"
  },
  "mcq": {
    "difficulty": "board",
    "question_stem": "What is the best immediate treatment?",
    "clinical_case": "ESRD patient missed dialysis. K 6.9. ECG peaked T waves.",
    "labs": { "K": "6.9", "HCO3": "18", "Cr": "9.4" },
    "choices": {
      "A": "Sodium polystyrene sulfonate",
      "B": "IV calcium gluconate",
      "C": "Oral patiromer",
      "D": "Dietary potassium restriction"
    },
    "correct_choice_key": "B",
    "explanation": "ECG changes require immediate membrane stabilization with IV calcium.",
    "clinical_pearl": "In severe hyperkalemia with ECG changes, calcium comes first."
  }
}
```

Import via admin API or extend `seed_data` / `chapter_seed.py`.

---

## 🌐 Web Routes (v1.1.0)

| Route | Page |
|-------|------|
| `/dashboard` | Stats, quick actions, weak topics |
| `/chapters` | Board chapter grid with animation + MCQ counts |
| `/chapters/:slug` | Topics, lessons, start chapter quiz |
| `/lessons/:lessonId` | Animation lesson viewer |
| `/categories` | Legacy category browser |
| `/quiz/:type` | Quiz (practice, daily, category, chapter) |
| `/quiz/:type/:id` | Quiz filtered by category or chapter ID |
| `/daily-challenge` | Daily challenge |
| `/leaderboard` | Rankings |
| `/profile` | User profile |
| `/admin` | Admin dashboard (admin role) |
| `/admin/questions` | Question CRUD |
| `/admin/ai-generated` | AI question review |

---

## 🎨 Design

- **Colors**: Deep blue `#1e3a5f`, Teal `#0d9488`, White background
- **Feedback**: Green (correct), Red (incorrect), Amber (review), Teal (board difficulty)
- **Features**: Dark/light mode, Framer Motion animations, responsive cards
- **Question UI**: Clinical case block, labs table, explanation + clinical pearl on review
- **Chapter UI**: Gradient cards, hero banner, animation/lesson metadata

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Flutter 3.0+ (for mobile)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Set DB_*, LLAMA_BASE_URL for GoDaddy Ollama, optional OPENAI_API_KEY
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data   # Admin: admin / admin123
python manage.py runserver 8000
```

### Web Frontend
```bash
cd web
npm install
npm run dev    # http://localhost:5173 — proxies /api → :8000
```

### Mobile (Flutter)
```bash
cd mobile
flutter pub get
flutter run
```

> **Note:** Mobile currently targets `https://api.nephrochallenge.ai/v1` in constants. Align `baseUrl` with `http://localhost:8000/api/` for local dev.

---

## 🤖 AI on GoDaddy VPS (LLaMA / Ollama)

The backend uses your **local LLaMA** on the GoDaddy server by default — no OpenAI bill required.

### `.env` on VPS

```env
AI_PROVIDER=ollama
LLAMA_BASE_URL=http://127.0.0.1:11434/v1
LLAMA_MODEL=llama3
LLAMA_API_KEY=ollama
```

| Setting | Description |
|---------|-------------|
| `AI_PROVIDER` | `auto` (try LLaMA then OpenAI), `ollama`/`llama`, or `openai` |
| `LLAMA_BASE_URL` | Ollama OpenAI-compatible API, usually `http://127.0.0.1:11434/v1` |
| `LLAMA_MODEL` | Model name you pulled (`llama3`, `llama3.1`, `mistral`, etc.) |
| `OPENAI_API_KEY` | Optional fallback if LLaMA is down |

### Ollama on GoDaddy (one-time)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama serve   # or run as systemd service
```

### API endpoints (unchanged for web/mobile)

- `POST /api/ai/explain/` — body: `{ "question_id": 1 }`
- `POST /api/ai/generate/` — body: `{ "topic": "Hyperkalemia", "difficulty": "medium" }`

If LLaMA fails, the app returns the stored question explanation from PostgreSQL.

---

## 🔄 Recommended Frontend Flow

1. `GET /api/chapters/` — list chapters
2. User selects chapter → `GET /api/chapters/:slug/`
3. User watches lesson → `GET /api/lessons/:id/` (loads `animation_url` from CDN)
4. User starts quiz → `GET /api/quiz/chapter/:id/?limit=10`
5. User answers → `POST /api/quiz/answer/` per question (or batch via `POST /api/attempts/`)
6. Dashboard → `GET /api/stats/`

---

## 🛡️ Safety & Compliance

- **Disclaimer**: "For medical education only. Not medical advice." displayed throughout
- **PHI Warning**: Users warned not to submit identifiable patient information
- **Admin Review**: AI-generated questions require approval before publication
- **Privacy**: Privacy policy and account deletion required for App Store / Play Store submission
- **HTTPS**: Production API and web must use HTTPS

---

## 💰 Monetization

- **Free Tier**: Limited daily questions, free chapters
- **Premium**: Premium lessons (`Lesson.is_premium`), unlimited AI tutor
- **Monthly**: $6.99–$14.99
- **Annual**: Discounted subscription
- **Institutional**: Residency program plans

---

## 📋 Version History

| Version | Changes |
|---------|---------|
| **Web 1.1.0** | Chapters UI, lesson viewer, board MCQs, API alignment, clinical case/labs on questions |
| **Web 1.0.0** | Initial React app with dashboard, quiz, admin scaffold |
| **Backend** | Chapter/Topic/Lesson models, seed data, import API, stats endpoint |

---

## 🔮 Roadmap

- [ ] Lottie animation player in lesson viewer
- [ ] Bulk MCQ import UI in admin panel
- [ ] Mobile API alignment with Django backend
- [ ] Case Duel mode
- [ ] Image/lab interpretation questions
- [ ] CME credit packages

---

> Built with ❤️ for the nephrology community.
