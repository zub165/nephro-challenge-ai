from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import QuizAttempt, Subscription, User
from api.tests.factories import (
    make_chapter,
    make_exam,
    make_question,
    make_questions,
    make_user,
)


class LegacyBoardExamExclusionTests(APITestCase):
    def setUp(self):
        self.chapter = make_chapter()
        self.user = make_user(username="legacy-user")
        self.practice_questions = make_questions(4, chapter=self.chapter)
        self.exam_questions = make_questions(50, chapter=self.chapter, start=100)
        self.exam = make_exam(self.exam_questions)
        self.client.force_authenticate(self.user)

    def practice_choice(self, question, correct=True):
        choice = question.choices.filter(is_correct=correct).first()
        return str(choice.pk), choice.choice_key

    def test_question_list_excludes_exam_questions(self):
        response = self.client.get("/api/questions/")

        ids = {str(row["id"]) for row in response.data["results"]}
        self.assertTrue(ids)
        self.assertTrue(ids.issubset({str(q.pk) for q in self.practice_questions}))

    def test_question_detail_404_for_exam_question(self):
        response = self.client.get(f"/api/questions/{self.exam_questions[0].pk}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_question_excludes_exam_questions(self):
        for _ in range(5):
            response = self.client.get("/api/questions/random_question/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(str(response.data["id"]), {str(q.pk) for q in self.practice_questions})

    def test_random_question_returns_404_when_pool_is_empty(self):
        for question in self.practice_questions:
            question.delete()

        response = self.client.get("/api/questions/random_question/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_legacy_daily_challenge_excludes_exam_questions(self):
        response = self.client.get("/api/questions/daily_challenge/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(response.data["id"]), {str(q.pk) for q in self.practice_questions})

    def test_quiz_daily_excludes_exam_questions(self):
        response = self.client.get("/api/quiz/daily/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(response.data["id"]), {str(q.pk) for q in self.practice_questions})

    def test_quiz_questions_excludes_exam_questions(self):
        response = self.client.get("/api/questions/quiz/?limit=20")

        ids = {row["id"] for row in response.data["questions"]}
        self.assertTrue(ids.issubset({str(q.pk) for q in self.practice_questions}))

    def test_daily_challenge_view_excludes_exam_questions(self):
        response = self.client.get("/api/daily-challenge/")

        ids = {row["id"] for row in response.data["questions"]}
        self.assertTrue(ids.issubset({str(q.pk) for q in self.practice_questions}))

    def test_quiz_chapter_excludes_exam_questions(self):
        response = self.client.get(f"/api/quiz/chapter/{self.chapter.pk}/?limit=20")

        ids = {row["id"] for row in response.data["questions"]}
        self.assertTrue(ids.issubset({str(q.pk) for q in self.practice_questions}))

    def test_immediate_grading_404_for_exam_question(self):
        question = self.exam_questions[0]
        choice_id, _ = self.practice_choice(question)

        response = self.client.post(
            "/api/quiz/answer/",
            {"question_id": str(question.pk), "chosen_choice_id": choice_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_immediate_grading_still_works_for_practice_question(self):
        question = self.practice_questions[0]
        choice_id, _ = self.practice_choice(question)

        response = self.client.post(
            "/api/quiz/answer/",
            {"question_id": str(question.pk), "chosen_choice_id": choice_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_correct"])
        self.assertTrue(response.data["correct_choice_key"])

    def test_explanation_404_for_exam_question(self):
        response = self.client.get(f"/api/quiz/explanation/{self.exam_questions[0].pk}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_explanation_still_works_for_practice_question(self):
        response = self.client.get(f"/api/quiz/explanation/{self.practice_questions[0].pk}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["correct_choice_key"])

    def test_ai_explanation_404_for_exam_question(self):
        self.client.force_authenticate(make_user(username="premium-ai-user", role="premium"))

        response = self.client.post(
            "/api/ai/explain/",
            {"question_id": str(self.exam_questions[0].pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detailed_ai_explanation_404_for_exam_question(self):
        self.client.force_authenticate(make_user(username="premium-ai-user-2", role="premium"))

        response = self.client.post(
            "/api/ai/explanation/detailed/",
            {"question_id": str(self.exam_questions[0].pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_board_pearls_exclude_exam_questions(self):
        exam_question = self.exam_questions[0]
        practice_question = self.practice_questions[0]
        exam_question.clinical_pearl = "Exam pearl that must stay hidden"
        exam_question.save(update_fields=["clinical_pearl"])
        practice_question.clinical_pearl = "Practice pearl visible to user"
        practice_question.save(update_fields=["clinical_pearl"])

        response = self.client.get("/api/pearls/")

        texts = {pearl["pearl"] for group in response.data["chapters"] for pearl in group["pearls"]}
        self.assertIn("Practice pearl visible to user", texts)
        self.assertNotIn("Exam pearl that must stay hidden", texts)

    def test_legacy_attempt_submission_rejects_exam_questions(self):
        question = self.exam_questions[0]
        choice_id, _ = self.practice_choice(question)

        response = self.client.post(
            "/api/attempts/",
            {
                "mode": "practice",
                "total_questions": 1,
                "time_taken": 10,
                "answers_data": [
                    {"question_id": str(question.pk), "chosen_choice_id": choice_id, "time_taken": 5}
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(QuizAttempt.objects.count(), 0)

    def test_legacy_attempt_submission_accepts_practice_questions(self):
        question = self.practice_questions[0]
        choice_id, _ = self.practice_choice(question)

        response = self.client.post(
            "/api/attempts/",
            {
                "mode": "practice",
                "total_questions": 1,
                "time_taken": 10,
                "answers_data": [
                    {"question_id": str(question.pk), "chosen_choice_id": choice_id, "time_taken": 5}
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attempt = QuizAttempt.objects.get()
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.total_questions, 1)

    def test_unpublished_exam_questions_remain_available_for_practice(self):
        draft_questions = make_questions(2, chapter=self.chapter, start=300)
        make_exam(draft_questions, slug="draft-exam", is_published=False)

        response = self.client.get("/api/questions/quiz/?limit=20")

        ids = {row["id"] for row in response.data["questions"]}
        self.assertTrue(ids.issubset({str(q.pk) for q in [*self.practice_questions, *draft_questions]}))
        self.assertIn(str(draft_questions[0].pk), ids)


class LegacyPremiumGateTests(APITestCase):
    def setUp(self):
        self.chapter = make_chapter()
        self.free_user = make_user(username="free-user")
        self.premium_user = make_user(username="premium-user", role="premium")
        self.premium_question = make_question(1, chapter=self.chapter, is_premium=True)
        self.client.force_authenticate(self.free_user)

    def answer(self, question):
        choice = question.choices.filter(is_correct=True).first()
        return {
            "question_id": str(question.pk),
            "chosen_choice_id": str(choice.pk),
        }

    def test_answer_requires_premium_for_premium_question(self):
        response = self.client.post("/api/quiz/answer/", self.answer(self.premium_question), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_premium_user_can_answer_premium_question(self):
        self.client.force_authenticate(self.premium_user)

        response = self.client.post("/api/quiz/answer/", self.answer(self.premium_question), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_explanation_requires_premium_for_premium_question(self):
        response = self.client.get(f"/api/quiz/explanation/{self.premium_question.pk}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_premium_user_can_read_premium_explanation(self):
        self.client.force_authenticate(self.premium_user)

        response = self.client.get(f"/api/quiz/explanation/{self.premium_question.pk}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ActiveSubscriptionPremiumTests(APITestCase):
    def setUp(self):
        self.chapter = make_chapter()
        self.user = make_user(username="subscribed-user")
        Subscription.objects.create(
            user=self.user,
            plan=Subscription.Plan.MONTHLY,
            end_date=timezone.now() + timedelta(days=10),
            is_active=True,
        )
        self.premium_question = make_question(1, chapter=self.chapter, is_premium=True)
        self.client.force_authenticate(self.user)

    def test_active_subscription_unlocks_premium_answers(self):
        choice = self.premium_question.choices.filter(is_correct=True).first()

        response = self.client.post(
            "/api/quiz/answer/",
            {"question_id": str(self.premium_question.pk), "chosen_choice_id": str(choice.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_subscription_locks_premium_answers(self):
        Subscription.objects.filter(user=self.user).update(
            end_date=timezone.now() - timedelta(days=1)
        )
        self.client.force_authenticate(User.objects.get(pk=self.user.pk))
        choice = self.premium_question.choices.filter(is_correct=True).first()

        response = self.client.post(
            "/api/quiz/answer/",
            {"question_id": str(self.premium_question.pk), "chosen_choice_id": str(choice.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
