from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.data.board_prep_plan import PLAN_LENGTH_DAYS, TARGET_MIN_QUESTIONS
from api.models import Last48HourFact
from api.tests.factories import make_chapter, make_question, make_user


class BoardPrepPlanApiTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="board-prep-user")
        self.chapter = make_chapter(slug="acute-kidney-injury-icu", title="AKI")
        self.question = make_question(1, chapter=self.chapter, correct_keys=("A",))
        self.correct = self.question.choices.get(choice_key="A")
        self.wrong = self.question.choices.get(choice_key="B")

    def test_plan_requires_auth(self):
        response = self.client.get(reverse("board-prep-plan"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_plan_returns_25_days_and_accepts_exam_date(self):
        self.client.force_authenticate(self.user)
        exam = date.today() + timedelta(days=24)
        response = self.client.post(
            reverse("board-prep-plan"),
            {"exam_date": exam.isoformat(), "work_weekdays": [1, 2, 3, 4, 5]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["days"]), PLAN_LENGTH_DAYS)
        self.assertEqual(response.data["day_number"], 1)
        self.assertEqual(response.data["days_until_exam"], 24)
        self.assertEqual(response.data["target_min"], TARGET_MIN_QUESTIONS)
        self.assertEqual(response.data["today_session"]["focus"], "AKI + ICU nephrology")

    def test_today_endpoint_and_quiz_loader_board_day(self):
        self.client.force_authenticate(self.user)
        today = self.client.get(reverse("board-prep-today"))
        self.assertEqual(today.status_code, status.HTTP_200_OK)
        quiz = self.client.get(reverse("questions-quiz"), {"board_day": 1, "limit": 5})
        self.assertEqual(quiz.status_code, status.HTTP_200_OK, quiz.data)
        self.assertTrue(quiz.data["questions"])

    def test_attempt_stores_confidence_and_review_queue(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("quiz-attempts"),
            {
                "mode": "board_prep",
                "chapter": self.chapter.id,
                "total_questions": 1,
                "answers_data": [
                    {
                        "question_id": self.question.id,
                        "chosen_choice_id": str(self.wrong.id),
                        "confidence": "guessed",
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        answer = response.data["answers"][0]
        self.assertEqual(answer["tag"], "wrong")
        self.assertEqual(answer["confidence"], "guessed")

        queue = self.client.get(reverse("board-prep-review"), {"tag": "wrong"})
        self.assertEqual(queue.status_code, status.HTTP_200_OK)
        self.assertEqual(queue.data["count"], 1)
        self.assertEqual(queue.data["items"][0]["question_id"], str(self.question.id))

        sheet = self.client.get(reverse("board-prep-last48"))
        self.assertEqual(sheet.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(sheet.data["items"]), 1)

    def test_last48_manual_add_and_delete(self):
        self.client.force_authenticate(self.user)
        created = self.client.post(
            reverse("board-prep-last48"),
            {"kind": "formula", "text": "Winter's: PCO2 = 1.5×HCO3 + 8 ± 2"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        fact_id = created.data["items"][0]["id"]
        deleted = self.client.delete(reverse("board-prep-last48-detail", args=[fact_id]))
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)
        self.assertEqual(Last48HourFact.objects.filter(user=self.user).count(), 0)

    def test_stats_include_board_prep(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("boardPrep", response.data)
        self.assertIn("classification", response.data["boardPrep"])
