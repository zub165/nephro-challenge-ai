from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.data.chapter_seed import CHAPTERS
from api.data.medical_references import references_for_topic
from api.models import Answer
from api.services.board_exam_service import payload_contains_answer_leakage
from api.tests.factories import make_chapter, make_question, make_user


class QuizLoaderLeakTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="quiz-leak-user")
        self.chapter = make_chapter()
        self.question = make_question(
            1, chapter=self.chapter, correct_keys=("A",), choice_count=4
        )

    def test_quiz_loader_never_leaks_answers_or_explanations(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("questions-quiz"), {"chapterId": self.chapter.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        questions = response.data["questions"]
        self.assertFalse(any("correct" in key.lower() for key in questions[0]))
        self.assertEqual(payload_contains_answer_leakage(questions), [])

    def test_chapter_quiz_loader_never_leaks_answers(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("quiz-chapter", args=[self.chapter.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(payload_contains_answer_leakage(response.data), [])


class ServerSideMarkingAndRevealTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="quiz-mark-user")
        self.chapter = make_chapter()
        self.question = make_question(
            1,
            chapter=self.chapter,
            correct_keys=("A",),
            choice_count=4,
            explanation="Systemic causes of shock must be excluded before volume repletion.",
            clinical_pearl="Urinalysis with active sediment distinguishes ATN from prerenal disease.",
            reference="",
        )
        self.correct_choice = self.question.choices.get(choice_key="A")
        self.wrong_choice = self.question.choices.get(choice_key="B")

    def post_attempt(self, answers):
        self.client.force_authenticate(self.user)
        return self.client.post(
            reverse("quiz-attempts"),
            {
                "mode": "practice",
                "chapter": self.chapter.id,
                "total_questions": 1,
                "answers_data": answers,
            },
            format="json",
        )

    def test_attempt_is_marked_server_side_and_returns_reveal_payload(self):
        response = self.post_attempt(
            [{"question_id": self.question.id, "chosen_choice_id": str(self.wrong_choice.id)}]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        data = response.data
        self.assertEqual(data["score"], 0)
        self.assertEqual(len(data["answers"]), 1)
        answer = data["answers"][0]
        self.assertFalse(answer["is_correct"])
        self.assertEqual(answer["chosen_choice_id"], str(self.wrong_choice.id))
        self.assertEqual(answer["correct_choice_id"], str(self.correct_choice.id))
        self.assertEqual(answer["why_wrong"], self.wrong_choice.why_wrong)
        self.assertEqual(answer["explanation"], self.question.explanation)
        self.assertEqual(answer["clinical_pearl"], self.question.clinical_pearl)
        self.assertIn("chosen_choice_id", answer)

    def test_correct_answer_marks_score_and_persists_stats(self):
        response = self.post_attempt(
            [{"question_id": self.question.id, "chosen_choice_id": str(self.correct_choice.id)}]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        data = response.data
        self.assertEqual(data["score"], 1)
        answer = data["answers"][0]
        self.assertTrue(answer["is_correct"])
        self.assertEqual(answer["correct_choice_id"], str(self.correct_choice.id))
        self.assertTrue(Answer.objects.filter(question=self.question, is_correct=True).exists())
        self.question.refresh_from_db()
        self.assertEqual(self.question.times_answered, 1)
        self.assertEqual(self.question.times_correct, 1)

    def test_empty_answers_payload_creates_zero_scored_attempt(self):
        response = self.post_attempt([])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["score"], 0)
        self.question.refresh_from_db()
        self.assertEqual(self.question.times_answered, 0)


class ChapterWiseLiteratureCoverageTests(TestCase):
    def test_every_seeded_chapter_topic_resolves_a_nephrology_reference(self):
        missing = []
        for chapter in CHAPTERS:
            for topic in chapter.get("topics", []):
                if not references_for_topic(topic["title"], chapter["slug"]):
                    missing.append((chapter["slug"], topic["title"]))
        self.assertEqual(missing, [])


class ImmediateAnswerRevealTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="reveal-user")
        self.chapter = make_chapter()
        self.question = make_question(
            2,
            chapter=self.chapter,
            correct_keys=("A",),
            explanation="Winter formula checks respiratory compensation.",
            clinical_pearl="Expected PCO2 = 1.5 x HCO3 + 8 +/- 2.",
        )
        self.correct_choice = self.question.choices.get(choice_key="A")
        self.wrong_choice = self.question.choices.get(choice_key="B")

    def test_quiz_answer_returns_correct_choice_and_explanation(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("quiz-answer"),
            {
                "question_id": self.question.id,
                "chosen_choice_id": str(self.wrong_choice.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(response.data["is_correct"])
        self.assertEqual(response.data["correct_choice_id"], str(self.correct_choice.id))
        self.assertEqual(response.data["explanation"], self.question.explanation)
        self.assertTrue(response.data["why_wrong"])
        self.question.refresh_from_db()
        self.assertEqual(self.question.times_answered, 0)

    def test_weaknesses_recommend_chapter_reading(self):
        self.client.force_authenticate(self.user)
        self.client.post(
            reverse("quiz-attempts"),
            {
                "mode": "practice",
                "chapter": self.chapter.id,
                "total_questions": 1,
                "answers_data": [
                    {
                        "question_id": self.question.id,
                        "chosen_choice_id": str(self.wrong_choice.id),
                    }
                ],
            },
            format="json",
        )
        response = self.client.get(reverse("weaknesses"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertGreaterEqual(len(response.data), 1)
        row = response.data[0]
        self.assertEqual(row["chapterSlug"], self.chapter.slug)
        self.assertIn("Read", row["recommend"])
        self.assertTrue(row["read_path"].endswith(self.chapter.slug))
