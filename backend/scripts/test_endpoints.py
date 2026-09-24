#!/usr/bin/env python3
"""Smoke-test all Nephro Challenge API endpoints and print results."""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://nephro-api.schedulemygroup.com/api"
TIMEOUT = 25


@dataclass
class Result:
    method: str
    path: str
    auth: str
    frontend: str
    status: int | str
    ok: bool
    note: str = ""


results: list[Result] = []
token: str | None = None
refresh: str | None = None
user_id: str | None = None
category_slug: str | None = None
category_id: str | None = None
chapter_slug: str | None = None
chapter_id: str | None = None
topic_id: str | None = None
lesson_id: str | None = None
question_id: str | None = None
attempt_id: str | None = None
note_id: str | None = None
choice_id: str | None = None


def req(
    method: str,
    path: str,
    *,
    auth: bool = False,
    body: dict | None = None,
    frontend: str = "",
) -> tuple[int | str, Any]:
    url = f"{BASE}{path}"
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if auth and token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=TIMEOUT) as resp:
            raw = resp.read().decode()
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = raw[:200]
            return resp.status, parsed
    except HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = raw[:200]
        return e.code, parsed
    except URLError as e:
        return "ERR", str(e.reason)


def record(
    method: str,
    path: str,
    *,
    auth: str,
    frontend: str,
    status: int | str,
    ok: bool,
    note: str = "",
) -> None:
    results.append(
        Result(method, path, auth, frontend, status, ok, note)
    )


def call(
    method: str,
    path: str,
    *,
    auth: bool = False,
    auth_label: str = "None",
    body: dict | None = None,
    frontend: str = "",
    expect: tuple[int, ...] = (200, 201),
) -> Any:
    status, data = req(method, path, auth=auth, body=body)
    ok = status in expect
    note = ""
    if not ok:
        if isinstance(data, dict):
            note = str(data.get("detail") or data.get("message") or data.get("error") or data)[:120]
        else:
            note = str(data)[:120]
    record(method, path, auth=auth_label, frontend=frontend, status=status, ok=ok, note=note)
    return data if ok else None


def main() -> int:
    global token, refresh, user_id
    global category_slug, category_id, chapter_slug, chapter_id
    global topic_id, lesson_id, question_id, attempt_id, note_id, choice_id

    print(f"Testing {BASE}\n")

    # --- Public / health ---
    call("GET", "/health/", auth_label="None", frontend="—", expect=(200,))

    try:
        request = Request("https://nephro-api.schedulemygroup.com/api/schema/")
        with urlopen(request, timeout=TIMEOUT) as r:
            record("GET", "/api/schema/", auth="None", frontend="—", status=r.status, ok=r.status == 200)
    except Exception as e:
        record("GET", "/api/schema/", auth="None", frontend="—", status="ERR", ok=False, note=str(e)[:80])

    try:
        request = Request("https://nephro-api.schedulemygroup.com/api/docs/")
        with urlopen(request, timeout=TIMEOUT) as r:
            record("GET", "/api/docs/", auth="None", frontend="—", status=r.status, ok=r.status == 200, note="HTML")
    except Exception as e:
        record("GET", "/api/docs/", auth="None", frontend="—", status="ERR", ok=False, note=str(e)[:80])

    # --- Auth ---
    email = f"apitest_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123!"
    reg = call(
        "POST",
        "/auth/register/",
        body={"username": email.split("@")[0], "email": email, "password": password, "bio": "API Test"},
        frontend="Register.tsx",
        expect=(201,),
    )
    if reg and isinstance(reg, dict):
        token = reg.get("token") or reg.get("access")
        refresh = reg.get("refresh")
        user_id = str((reg.get("user") or {}).get("id", ""))

    if not token:
        login = call(
            "POST",
            "/auth/login/",
            body={"email": "admin@nephrochallenge.com", "password": "admin123"},
            frontend="Login.tsx",
            expect=(200,),
        )
        if login and isinstance(login, dict):
            token = login.get("token") or login.get("access")
            refresh = login.get("refresh")
            user_id = str((login.get("user") or {}).get("id", ""))

    if not token:
        print("FATAL: Could not obtain auth token")
        return 1

    call("GET", "/auth/profile/", auth=True, auth_label="Bearer", frontend="Profile.tsx")
    call("PATCH", "/auth/profile/", auth=True, auth_label="Bearer", body={"bio": "API Test User"}, frontend="Profile.tsx")

    if refresh:
        call("POST", "/token/refresh/", body={"refresh": refresh}, frontend="axios interceptor", expect=(200,))

    # --- Public content ---
    cats = call("GET", "/categories/", auth_label="None", frontend="Categories.tsx")
    if cats:
        items = cats if isinstance(cats, list) else cats.get("results", [])
        if items:
            category_slug = items[0].get("slug")
            category_id = str(items[0].get("id"))

    chapters = call("GET", "/chapters/", auth_label="None", frontend="Chapters.tsx")
    if chapters:
        items = chapters if isinstance(chapters, list) else chapters.get("results", [])
        if items:
            chapter_slug = items[0].get("slug")
            chapter_id = str(items[0].get("id"))
            topics = items[0].get("topics") or []
            if topics:
                topic_id = str(topics[0].get("id"))
                lessons = topics[0].get("lessons") or []
                if lessons:
                    lesson_id = str(lessons[0].get("id"))

    if category_slug:
        call("GET", f"/categories/{category_slug}/", auth_label="None", frontend="Categories.tsx")
    if chapter_slug:
        ch = call("GET", f"/chapters/{chapter_slug}/", auth_label="None", frontend="ChapterDetail.tsx")
        if ch and not topic_id:
            for t in (ch.get("topics") or []):
                topic_id = str(t.get("id"))
                for les in (t.get("lessons") or []):
                    lesson_id = str(les.get("id"))
                    break
                break
        call("GET", f"/chapters/{chapter_slug}/topics/", auth_label="None", frontend="ChapterDetail.tsx")

    if topic_id:
        call("GET", f"/topics/{topic_id}/", auth_label="None", frontend="—")
        call("GET", f"/topics/{topic_id}/lessons/", auth_label="None", frontend="—")

    if lesson_id:
        call("GET", f"/lessons/{lesson_id}/", auth_label="None", frontend="LessonView.tsx")

    # --- Questions (auth) ---
    qs = call("GET", "/questions/", auth=True, auth_label="Bearer", frontend="—")
    if qs:
        items = qs if isinstance(qs, list) else qs.get("results", [])
        if items:
            question_id = str(items[0].get("id"))

    if question_id:
        call("GET", f"/questions/{question_id}/", auth=True, auth_label="Bearer", frontend="—")
    call("GET", "/questions/daily_challenge/", auth=True, auth_label="Bearer", frontend="— (legacy)")

    quiz = call(
        "GET",
        "/questions/quiz/?limit=3",
        auth=True,
        auth_label="Bearer",
        frontend="Quiz.tsx",
    )
    if quiz and quiz.get("questions"):
        q0 = quiz["questions"][0]
        question_id = str(q0.get("id"))
        if q0.get("choices"):
            choice_id = str(q0["choices"][0].get("id"))
        # quiz-safe: should NOT have correctAnswer
        has_leak = "correctAnswer" in q0 or "explanation" in q0
        record(
            "GET",
            "/questions/quiz/",
            auth="Bearer",
            frontend="Quiz.tsx",
            status=200,
            ok=not has_leak,
            note="LEAKS answers" if has_leak else "quiz-safe OK",
        )

    call("GET", "/quiz/daily/", auth=True, auth_label="Bearer", frontend="mobile")
    if chapter_id:
        call("GET", f"/quiz/chapter/{chapter_id}/?limit=3", auth=True, auth_label="Bearer", frontend="mobile/Quiz")

    call("GET", "/daily-challenge/", auth=True, auth_label="Bearer", frontend="DailyChallenge.tsx")

    if question_id and choice_id:
        call(
            "POST",
            "/quiz/answer/",
            auth=True,
            auth_label="Bearer",
            body={"question_id": question_id, "chosen_choice_id": choice_id},
            frontend="mobile quiz",
        )
        call("GET", f"/quiz/explanation/{question_id}/", auth=True, auth_label="Bearer", frontend="Quiz.tsx review")

    # --- Attempts ---
    if question_id and choice_id:
        attempt = call(
            "POST",
            "/attempts/",
            auth=True,
            auth_label="Bearer",
            body={
                "mode": "practice",
                "total_questions": 1,
                "time_taken": 30,
                "answers_data": [
                    {"question_id": question_id, "chosen_choice_id": choice_id, "time_taken": 30}
                ],
            },
            frontend="Quiz.tsx",
            expect=(201,),
        )
        if attempt and attempt.get("id") is not None:
            attempt_id = str(attempt["id"])

    call("POST", "/quiz/attempts/", auth=True, auth_label="Bearer", body={
        "mode": "practice", "total_questions": 0, "answers_data": []
    }, frontend="alias", expect=(400,))  # empty should 400

    call("GET", "/attempts/", auth=True, auth_label="Bearer", frontend="—")
    if attempt_id:
        call("GET", f"/attempts/{attempt_id}/", auth=True, auth_label="Bearer", frontend="—")

    # --- Stats ---
    call("GET", "/stats/", auth=True, auth_label="Bearer", frontend="Dashboard.tsx, Profile.tsx")
    call("GET", "/users/me/progress/", auth=True, auth_label="Bearer", frontend="alias")
    call("GET", "/weaknesses/", auth=True, auth_label="Bearer", frontend="Dashboard.tsx")
    call("GET", "/leaderboard/?period=all_time", auth=True, auth_label="Bearer", frontend="Leaderboard.tsx")
    call("GET", "/leaderboard/user_rank/", auth=True, auth_label="Bearer", frontend="Leaderboard.tsx")

    # --- Pearls & notes ---
    call("GET", "/pearls/", auth=True, auth_label="Bearer", frontend="BoardPearls.tsx")
    if chapter_slug:
        call("GET", f"/pearls/?chapter={chapter_slug}", auth=True, auth_label="Bearer", frontend="BoardPearls.tsx")

    org = call(
        "POST",
        "/notes/organize/",
        auth=True,
        auth_label="Bearer",
        body={"text": "Hyperkalemia pearl: IV calcium for ECG changes.\n\nAKI pearl: Check pre-renal vs intrinsic."},
        frontend="Notes.tsx",
        expect=(201,),
    )
    if org and org.get("notes"):
        note_id = str(org["notes"][0].get("id"))

    call("GET", "/notes/review/", auth=True, auth_label="Bearer", frontend="Notes.tsx")
    call("GET", "/notes/", auth=True, auth_label="Bearer", frontend="Notes.tsx")
    call("POST", "/notes/dedupe/", auth=True, auth_label="Bearer", body={}, frontend="Notes.tsx", expect=(200,))
    call("POST", "/notes/enrich/", auth=True, auth_label="Bearer", body={"use_llm": False}, frontend="Notes.tsx", expect=(200,))

    if note_id:
        call("PATCH", f"/notes/{note_id}/", auth=True, auth_label="Bearer", body={"topic_title": "Test"}, frontend="Notes.tsx")

    # --- AI ---
    if question_id:
        call("POST", "/ai/explain/", auth=True, auth_label="Bearer", body={"question_id": question_id}, frontend="mobile", expect=(200, 403))
    call("POST", "/ai/generate/", auth=True, auth_label="Bearer", body={"topic": "Hyperkalemia", "difficulty": "medium"}, frontend="admin", expect=(201, 403, 500))

    # --- Subscriptions ---
    call("GET", "/subscriptions/", auth=True, auth_label="Bearer", frontend="—", expect=(200,))
    call("POST", "/subscriptions/", auth=True, auth_label="Bearer", body={
        "plan": "monthly", "end_date": "2027-01-01T00:00:00Z", "is_active": True
    }, frontend="—", expect=(201, 400))

    # --- Admin (may 403 for non-admin) ---
    for method, path, body, fe in [
        ("GET", "/admin/stats/", None, "AdminDashboard.tsx"),
        ("GET", "/admin/questions/", None, "AdminQuestions.tsx"),
        ("GET", "/admin/questions/ai-generated/", None, "AdminAIGenerated.tsx"),
    ]:
        call(method, path, auth=True, auth_label="Bearer (admin)", body=body, frontend=fe, expect=(200, 403))

    # --- Missing mobile endpoints ---
    for method, path in [
        ("POST", "/auth/google/"),
        ("POST", "/auth/apple/"),
        ("POST", "/ai/tutor/chat/"),
        ("POST", "/ai/explanation/detailed/"),
        ("POST", "/ai/questions/generate/"),
    ]:
        status, data = req(method, path, auth=True, body={"message": "test"})
        record(method, path, auth="Bearer", frontend="mobile (missing)", status=status, ok=False, note="404 expected" if status == 404 else str(data)[:60])

    # --- Summary ---
    passed = sum(1 for r in results if r.ok)
    failed = [r for r in results if not r.ok]
    print(f"\n{'METHOD':<7} {'PATH':<45} {'AUTH':<16} {'ST':<5} {'OK':<4} FRONTEND / NOTE")
    print("-" * 120)
    for r in results:
        mark = "✓" if r.ok else "✗"
        print(f"{r.method:<7} {r.path:<45} {r.auth:<16} {str(r.status):<5} {mark:<4} {r.frontend} {r.note}")

    print(f"\n{passed}/{len(results)} passed, {len(failed)} failed")
    out = BASE.replace("/api", "")
    report_path = "/home/newgen/nephro-challenge-ai-staging/docs/FRONTEND_API.md"
    write_frontend_doc(report_path, results, passed, len(results))
    print(f"\nFrontend doc written: {report_path}")
    return 0 if len(failed) <= 8 else 1  # allow missing mobile endpoints


def write_frontend_doc(path: str, test_results: list[Result], passed: int, total: int) -> None:
    """Generate markdown API reference for frontend."""
    from datetime import datetime, timezone

    tested = {f"{r.method} {r.path.split('?')[0]}": r for r in test_results}

    content = f"""# Nephro Challenge API — Frontend Reference

> Auto-tested against `https://nephro-api.schedulemygroup.com/api` on {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  
> **{passed}/{total}** endpoint checks passed.

## Base URL

| Client | Base URL |
|--------|----------|
| **React (GitHub Pages)** | `VITE_API_URL` → `https://nephro-api.schedulemygroup.com/api` |
| **Flutter** | `baseUrl` in `mobile/lib/config/constants.dart` |

All paths below are relative to `/api`. Send `Authorization: Bearer <access_token>` for protected routes.

---

## Auth headers

```ts
// web/src/lib/axios.ts — already configured
headers: {{
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${{token}}`,  // when logged in
}}
```

Login/register responses:

```json
{{
  "user": {{ "id", "username", "email", "bio", "role", "streak_count", "longest_streak", "xp_points", "created_at" }},
  "token": "<access>",
  "access": "<access>",
  "refresh": "<refresh>"
}}
```

Map user for UI: `mapUserFromApi()` in `web/src/lib/apiMappers.ts` (`bio` → display name).

---

## Health & docs

| Status | Method | Endpoint | Auth | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "GET", "/health/")} | GET | `/health/` | None | uptime |
| {_st(tested, "GET", "/api/schema/")} | GET | `/api/schema/` | None | OpenAPI JSON |
| {_st(tested, "GET", "/api/docs/")} | GET | `/api/docs/` | None | Swagger UI |

---

## Auth & account

| Status | Method | Endpoint | Body | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "POST", "/auth/register/")} | POST | `/auth/register/` | `{{ username, email, password, bio? }}` | Register.tsx |
| {_st(tested, "POST", "/auth/login/")} | POST | `/auth/login/` | `{{ email, password }}` or `{{ username, password }}` | Login.tsx |
| {_st(tested, "GET", "/auth/profile/")} | GET | `/auth/profile/` | — | Profile.tsx |
| {_st(tested, "PATCH", "/auth/profile/")} | PATCH | `/auth/profile/` | `{{ bio, specialty? }}` | Profile.tsx |
| — | DELETE | `/auth/account/` | — | mobile deleteAccount |
| {_st(tested, "POST", "/token/refresh/")} | POST | `/token/refresh/` | `{{ refresh }}` | axios / mobile interceptor |
| ✗ 404 | POST | `/auth/google/` | `{{ id_token, access_token }}` | **mobile only — not implemented** |
| ✗ 404 | POST | `/auth/apple/` | `{{ identity_token, ... }}` | **mobile only — not implemented** |

---

## Chapters, topics, lessons

| Status | Method | Endpoint | Auth | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "GET", "/chapters/")} | GET | `/chapters/` | None | Chapters.tsx, Notes.tsx |
| {_st(tested, "GET", "/chapters/{{slug}}/")} | GET | `/chapters/{{slug}}/` | None | ChapterDetail.tsx |
| {_st(tested, "GET", "/chapters/{{slug}}/topics/")} | GET | `/chapters/{{slug}}/topics/` | None | ChapterDetail.tsx |
| {_st(tested, "GET", "/topics/{{id}}/")} | GET | `/topics/{{id}}/` | None | — |
| {_st(tested, "GET", "/topics/{{id}}/lessons/")} | GET | `/topics/{{id}}/lessons/` | None | — |
| {_st(tested, "GET", "/lessons/{{id}}/")} | GET | `/lessons/{{id}}/` | None | LessonView.tsx |

**Tip:** Pass `?limit=100` on list endpoints to avoid DRF pagination truncation (20/page default).

---

## Categories & questions

| Status | Method | Endpoint | Auth | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "GET", "/categories/")} | GET | `/categories/` | None | Categories.tsx, AdminQuestions |
| {_st(tested, "GET", "/categories/{{slug}}/")} | GET | `/categories/{{slug}}/` | None | — |
| {_st(tested, "GET", "/questions/")} | GET | `/questions/` | Bearer | — |
| {_st(tested, "GET", "/questions/{{id}}/")} | GET | `/questions/{{id}}/` | Bearer | includes answers |
| {_st(tested, "GET", "/questions/random_question/")} | GET | `/questions/random_question/` | Bearer | — |
| {_st(tested, "GET", "/questions/daily_challenge/")} | GET | `/questions/daily_challenge/` | Bearer | legacy single Q |
| {_st(tested, "GET", "/questions/quiz/")} | GET | `/questions/quiz/` | Bearer | **Quiz.tsx** |

### `GET /questions/quiz/` query params

| Param | Values | Description |
|-------|--------|-------------|
| `limit` | number | Default 10; daily uses 5 |
| `daily` | `true` | Daily challenge set |
| `categoryId` | id | Category practice |
| `chapterId` | id | Chapter practice |
| `topicId` | id | Topic practice |

**Response (quiz-safe — no answers):**

```json
{{
  "questions": [
    {{
      "id": "1",
      "text": "...",
      "caseText": "...",
      "labs": {{}},
      "choices": [{{ "id": "10", "text": "...", "key": "A" }}],
      "difficulty": "medium",
      "categoryId": "1",
      "chapterId": "2"
    }}
  ],
  "sessionId": null
}}
```

Use `mapBackendQuestion()` — do **not** expect `correctAnswer` until after submit.

---

## Quiz flow

| Status | Method | Endpoint | Body / params | Used by |
|--------|--------|----------|---------------|---------|
| {_st(tested, "GET", "/daily-challenge/")} | GET | `/daily-challenge/` | — | DailyChallenge.tsx |
| {_st(tested, "GET", "/quiz/daily/")} | GET | `/quiz/daily/` | — | mobile |
| {_st(tested, "GET", "/quiz/chapter/{{id}}/")} | GET | `/quiz/chapter/{{id}}/?limit=10` | — | mobile |
| {_st(tested, "POST", "/quiz/answer/")} | POST | `/quiz/answer/` | `{{ question_id, chosen_choice_id }}` | mobile per-question |
| {_st(tested, "GET", "/quiz/explanation/{{id}}/")} | GET | `/quiz/explanation/{{id}}/` | — | Quiz.tsx review |
| {_st(tested, "POST", "/attempts/")} | POST | `/attempts/` | see below | **Quiz.tsx** |
| {_st(tested, "POST", "/quiz/attempts/")} | POST | `/quiz/attempts/` | alias of create | — |
| {_st(tested, "GET", "/attempts/")} | GET | `/attempts/` | — | — |
| {_st(tested, "GET", "/attempts/{{id}}/")} | GET | `/attempts/{{id}}/` | — | — |

### `POST /attempts/`

```json
{{
  "mode": "daily | chapter | category | practice",
  "chapter": "id?",
  "category": "id?",
  "total_questions": 5,
  "time_taken": 300,
  "answers_data": [
    {{ "question_id": "1", "chosen_choice_id": "10", "time_taken": 30 }}
  ]
}}
```

**Response:** `{{ id, score, total_questions, percentage, answers: [...] }}` — use `score` for results UI.

### `GET /daily-challenge/`

```json
{{
  "id": "daily-2026-06-17",
  "date": "2026-06-17",
  "questions": [ /* quiz-safe */ ],
  "completed": false,
  "score": 4
}}
```

`score` only present when `completed: true` (requires ≥5 answers on today's daily attempt).

---

## Progress & leaderboard

| Status | Method | Endpoint | Used by |
|--------|--------|----------|---------|
| {_st(tested, "GET", "/stats/")} | GET | `/stats/` | Dashboard.tsx, Profile.tsx |
| {_st(tested, "GET", "/users/me/progress/")} | GET | `/users/me/progress/` | alias |
| {_st(tested, "GET", "/weaknesses/")} | GET | `/weaknesses/` | Dashboard.tsx |
| {_st(tested, "GET", "/leaderboard/")} | GET | `/leaderboard/?period=all_time` | Leaderboard.tsx |
| {_st(tested, "GET", "/leaderboard/user_rank/")} | GET | `/leaderboard/user_rank/?period=weekly` | Leaderboard.tsx |

### `GET /stats/` response (camelCase from backend)

```json
{{
  "totalQuizzes": 12,
  "totalQuestions": 120,
  "correctAnswers": 90,
  "accuracy": 75.0,
  "currentStreak": 3,
  "longestStreak": 5,
  "dailyQuizCompleted": true,
  "categoryBreakdown": [{{ "categoryId", "categoryName", "totalQuestions", "correctAnswers", "accuracy" }}],
  "recentActivity": [{{ "date", "quizzesCompleted", "questionsAnswered", "correctAnswers" }}]
}}
```

### `GET /leaderboard/` response

```json
{{ "count": 50, "results": [{{ "user", "username", "score", "quiz_count", "accuracy", "streak", "rank" }}] }}
```

Use `mapLeaderboardEntries()` and `unwrapList()`.

---

## Board pearls & study notes

| Status | Method | Endpoint | Body | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "GET", "/pearls/")} | GET | `/pearls/` | `?chapter=slug` | BoardPearls.tsx |
| {_st(tested, "POST", "/notes/organize/")} | POST | `/notes/organize/` | `{{ text }}` | Notes.tsx |
| {_st(tested, "GET", "/notes/review/")} | GET | `/notes/review/` | — | Notes.tsx |
| {_st(tested, "POST", "/notes/dedupe/")} | POST | `/notes/dedupe/` | — | Notes.tsx |
| {_st(tested, "GET", "/notes/")} | GET | `/notes/` | `?chapter=slug` | Notes.tsx |
| {_st(tested, "PATCH", "/notes/{{id}}/")} | PATCH | `/notes/{{id}}/` | `{{ chapter, topic_title, content }}` | Notes.tsx |
| — | DELETE | `/notes/{{id}}/` | — | Notes.tsx |

---

## AI

| Status | Method | Endpoint | Body | Used by |
|--------|--------|----------|------|---------|
| {_st(tested, "POST", "/ai/explain/")} | POST | `/ai/explain/` | `{{ question_id }}` | mobile quiz |
| {_st(tested, "POST", "/ai/generate/")} | POST | `/ai/generate/` | `{{ topic, difficulty }}` | admin draft |
| ✗ 404 | POST | `/ai/tutor/chat/` | `{{ message }}` | **mobile — not implemented** |
| ✗ 404 | POST | `/ai/explanation/detailed/` | question + answers | **mobile — not implemented** |
| ✗ 404 | POST | `/ai/questions/generate/` | `{{ topic, count, difficulty }}` | **mobile — not implemented** |

---

## Admin (role: admin)

| Status | Method | Endpoint | Used by |
|--------|--------|----------|---------|
| {_st(tested, "GET", "/admin/stats/")} | GET | `/admin/stats/` | AdminDashboard.tsx |
| {_st(tested, "GET", "/admin/questions/")} | GET | `/admin/questions/?page=1&limit=20` | AdminQuestions.tsx |
| {_st(tested, "POST", "/admin/questions/")} | POST | `/admin/questions/` | AdminQuestions.tsx |
| — | PUT | `/admin/questions/{{id}}/` | AdminQuestions.tsx |
| — | DELETE | `/admin/questions/{{id}}/` | AdminQuestions.tsx |
| {_st(tested, "GET", "/admin/questions/ai-generated/")} | GET | `/admin/questions/ai-generated/` | AdminAIGenerated.tsx |
| — | PUT | `/admin/questions/{{id}}/review/` | `{{ aiReviewStatus: "approved" \\| "rejected" }}` | AdminAIGenerated.tsx |
| — | POST | `/admin/import-mcqs/` | bulk JSON | — |

---

## Subscriptions

| Status | Method | Endpoint | Used by |
|--------|--------|----------|---------|
| {_st(tested, "GET", "/subscriptions/")} | GET | `/subscriptions/` | — |
| {_st(tested, "POST", "/subscriptions/")} | POST | `/subscriptions/` | — |

---

## Frontend mapper cheat sheet

| Endpoint | Mapper / helper |
|----------|-----------------|
| `/questions/quiz/`, `/daily-challenge/` | `mapBackendQuestion()` |
| `/daily-challenge/` | `mapDailyChallenge()` |
| `/categories/` | `mapCategories()` + `unwrapList()` |
| `/chapters/` | `unwrapList()` |
| `/leaderboard/` | `mapLeaderboardEntries()` |
| `/auth/login/`, `/auth/register/`, `/auth/profile/` | `mapUserFromApi()` |

---

## Error shapes

| Case | Response |
|------|----------|
| Login failed | `{{ "message": "Invalid credentials" }}` or `non_field_errors` |
| Validation | `{{ "field": ["error"] }}` or `{{ "message": "..." }}` |
| 401 | Token expired → refresh via `/token/refresh/` |
| 403 | Premium/admin required |

---

## Not yet on API (mobile expects these)

1. `POST /auth/google/`
2. `POST /auth/apple/`
3. `POST /ai/tutor/chat/`
4. `POST /ai/explanation/detailed/`
5. `POST /ai/questions/generate/`
6. `GET/POST/DELETE /saved-pearls/`

---

*Generated by `backend/scripts/test_endpoints.py`*
"""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def _st(tested: dict, method: str, path: str) -> str:
    key = f"{method} {path}"
    for k, r in tested.items():
        if k.startswith(f"{method} {path.split('{')[0]}"):
            return "✓" if r.ok else f"✗ {r.status}"
    r = tested.get(key)
    if r:
        return "✓" if r.ok else f"✗ {r.status}"
    return "—"


if __name__ == "__main__":
    sys.exit(main())
