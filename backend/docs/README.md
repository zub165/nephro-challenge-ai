# Nephrology Board MCQ Backend

PostgreSQL stores MCQs, chapters, topics, and lesson metadata. **Animation files are NOT stored in the database** — only `animation_url` and `thumbnail_url` point to Cloudflare R2 / AWS S3 / your CDN.

## Django Models (maps to schema.sql)

| Plan table | Django model |
|------------|--------------|
| `chapters` | `api.Chapter` |
| `topics` | `api.Topic` |
| `lessons` | `api.Lesson` |
| `mcqs` | `api.Question` |
| `mcq_choices` | `api.Choice` |
| `quiz_attempts` | `api.QuizAttempt` |
| `user_answers` | `api.Answer` |

## Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8000
```

## API Endpoints (frontend)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/chapters/` | All chapters with counts |
| GET | `/api/chapters/:slug/` | Chapter + topics |
| GET | `/api/chapters/:slug/topics/` | Topics under chapter |
| GET | `/api/topics/:id/lessons/` | Lessons + animation URLs |
| GET | `/api/lessons/:id/` | Single lesson detail |
| GET | `/api/quiz/daily/` | Today's MCQ |
| GET | `/api/quiz/chapter/:id/?limit=10` | Chapter MCQs |
| GET | `/api/questions/quiz/` | Frontend quiz loader |
| POST | `/api/quiz/answer/` | Check answer + explanation |
| GET | `/api/quiz/explanation/:id/` | Full explanation |
| POST | `/api/attempts/` | Submit quiz attempt |
| GET | `/api/stats/` | Dashboard stats |
| POST | `/api/admin/import-mcqs/` | Import `sample-mcq.json` format |

## Animation Storage

1. Upload Lottie JSON / MP4 to R2 or S3 bucket `nephrochallenge-animations`
2. Set public URL e.g. `https://cdn.nephrochallenge.ai/animations/hyperkalemia-algorithm.json`
3. Save URL in `Lesson.animation_url` only — never store binary in PostgreSQL

## Import MCQs

```bash
curl -X POST http://localhost:8000/api/admin/import-mcqs/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @docs/sample-mcq.json
```

See also: `schema.sql`, `seed.sql`, `api-plan.md`, `sample-mcq.json`
