
# Backend API Plan

## Frontend APIs

GET /api/chapters
Returns all chapters.

GET /api/chapters/:slug/topics
Returns topics under a chapter.

GET /api/topics/:id/lessons
Returns lessons and animation URLs.

GET /api/quiz/daily
Returns today's MCQ.

GET /api/quiz/chapter/:chapterId?limit=10
Returns MCQs from a chapter.

POST /api/quiz/attempts
Creates a quiz attempt.

POST /api/quiz/answer
Checks answer and saves user progress.

GET /api/quiz/explanation/:mcqId
Returns explanation, wrong-answer explanations, and clinical pearl.

GET /api/users/me/progress
Returns accuracy, streak, weak chapters, and completed questions.

## Admin APIs

POST /api/admin/chapters
POST /api/admin/topics
POST /api/admin/lessons
POST /api/admin/mcqs
PUT /api/admin/mcqs/:id
POST /api/admin/import-mcqs
POST /api/admin/ai-generate-mcq

## Animation Storage

Do not store animation files inside PostgreSQL.
Store animation files in:
- Cloudflare R2
- AWS S3
- Your own server
- Firebase Storage

Database should store only:
- animation_url
- thumbnail_url
- lesson title
- summary
- chapter/topic link
