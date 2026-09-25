from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import BoardExam, BoardExamAttempt
from api.services.board_exam_service import payload_contains_answer_leakage
from api.tests.factories import (
    make_exam,
    make_question,
    make_questions,
    make_user,
)


class BoardExamApiBase(APITestCase):
    def setUp(self):
        self.user = make_user(username="board-user")
        self.other_user = make_user(username="other-user")
        self.questions = make_questions(60)
        self.exam = make_exam(self.questions)

    def authenticate(self, user=None):
        self.client.force_authenticate(user or self.user)

    def start(self, slug="nephrology-board", expect=status.HTTP_200_OK):
        self.authenticate()
        response = self.client.post(reverse("board-exam-start", args=[slug]))
        self.assertEqual(response.status_code, expect, response.data)
        return response

    def attempt_id_from(self, response):
        return response.data["attempt_id"]

    def force_deadline(self, attempt, *, seconds_from_now):
        BoardExamAttempt.objects.filter(pk=attempt.pk).update(
            deadline=timezone.now() + timedelta(seconds=seconds_from_now)
        )


class BoardExamListApiTests(BoardExamApiBase):
    def test_exam_endpoints_require_authentication(self):
        get_urls = [
            reverse("board-exam-list"),
            reverse("board-exam-detail", args=[self.exam.slug]),
        ]
        for url in get_urls:
            self.assertEqual(
                self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED, url
            )
        self.assertEqual(
            self.client.post(reverse("board-exam-start", args=[self.exam.slug])).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_list_returns_only_published_exams(self):
        make_exam(make_questions(50, start=500), slug="draft-exam", is_published=False)
        self.authenticate()

        response = self.client.get(reverse("board-exam-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [row["slug"] for row in response.data["results"]]
        self.assertEqual(slugs, ["nephrology-board"])

    def test_detail_returns_published_exam_and_hides_drafts(self):
        self.authenticate()

        response = self.client.get(reverse("board-exam-detail", args=[self.exam.slug]))
        missing = self.client.get(reverse("board-exam-detail", args=["draft-exam"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "nephrology-board")
        self.assertEqual(response.data["question_count"], 50)
        self.assertEqual(response.data["duration_minutes"], 60)
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)


class BoardExamStartApiTests(BoardExamApiBase):
    def test_start_returns_fifty_questions_without_answer_leakage(self):
        response = self.start()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["resumed"])
        self.assertEqual(response.data["total_questions"], 50)
        self.assertEqual(response.data["answered_count"], 0)
        self.assertEqual(len(response.data["items"]), 50)
        self.assertEqual(
            [item["position"] for item in response.data["items"]], list(range(1, 51))
        )
        self.assertIn("server_time", response.data)
        self.assertIn("deadline", response.data)
        self.assertIn("remaining_seconds", response.data)
        self.assertEqual(payload_contains_answer_leakage(response.data), [])

    def test_second_start_resumes_same_attempt(self):
        first = self.start()
        second = self.start()

        self.assertTrue(second.data["resumed"])
        self.assertEqual(first.data["attempt_id"], second.data["attempt_id"])
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 1)

    def test_resume_preserves_answers_and_answered_count(self):
        started = self.start()
        attempt_id = self.attempt_id_from(started)
        self.client.put(
            reverse("board-exam-answer", args=[attempt_id, 1]),
            {"selected_choice_key": "B"},
            format="json",
        )

        resumed = self.start()

        self.assertTrue(resumed.data["resumed"])
        self.assertEqual(resumed.data["answered_count"], 1)
        self.assertEqual(resumed.data["items"][0]["selected_choice_key"], "B")

    def test_start_returns_409_when_pool_is_insufficient(self):
        exam = make_exam(make_questions(49, start=300), slug="thin-exam", question_count=50)

        response = self.start(slug="thin-exam", expect=status.HTTP_409_CONFLICT)

        self.assertIn("detail", response.data)
        self.assertEqual(BoardExamAttempt.objects.filter(exam=exam).count(), 0)

    def test_start_creates_new_attempt_after_submission(self):
        started = self.start()
        first_attempt_id = self.attempt_id_from(started)
        self.client.post(reverse("board-exam-submit", args=[first_attempt_id]))

        response = self.start(expect=status.HTTP_200_OK)

        self.assertFalse(response.data["resumed"])
        self.assertNotEqual(response.data["attempt_id"], first_attempt_id)
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 2)

    def test_start_creates_new_attempt_after_expiry(self):
        started = self.start()
        first_attempt_id = self.attempt_id_from(started)
        attempt = BoardExamAttempt.objects.get(pk=first_attempt_id)
        self.force_deadline(attempt, seconds_from_now=-5)

        response = self.start(expect=status.HTTP_200_OK)

        self.assertFalse(response.data["resumed"])
        self.assertNotEqual(response.data["attempt_id"], first_attempt_id)
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 2)

    def test_start_resumes_only_one_active_attempt(self):
        self.start()
        BoardExamAttempt.objects.filter(
            user=self.user, status=BoardExamAttempt.Status.IN_PROGRESS
        ).update(status=BoardExamAttempt.Status.SUBMITTED)
        second = self.start()
        third = self.start()

        self.assertFalse(second.data["resumed"])
        self.assertTrue(third.data["resumed"])
        self.assertEqual(second.data["attempt_id"], third.data["attempt_id"])
        self.assertEqual(
            BoardExamAttempt.objects.filter(
                user=self.user, status=BoardExamAttempt.Status.IN_PROGRESS
            ).count(),
            1,
        )

    def test_start_ignores_client_supplied_duration_and_questions(self):
        self.authenticate()

        response = self.client.post(
            reverse("board-exam-start", args=[self.exam.slug]),
            {
                "duration_minutes": 5,
                "question_count": 2,
                "questions": [q.pk for q in self.questions[:3]],
                "question_ids": [q.pk for q in self.questions[:3]],
                "score": 100,
                "time_taken": 1,
            },
            format="json",
        )

        attempt = BoardExamAttempt.objects.get(pk=response.data["attempt_id"])
        self.assertEqual(
            attempt.deadline - attempt.started_at, timedelta(minutes=60)
        )
        self.assertEqual(attempt.total_questions, 50)
        self.assertEqual(attempt.score, 0.0)
        self.assertEqual(attempt.time_taken_seconds, 0)

    def test_start_uses_deadline_of_sixty_minutes(self):
        response = self.start()
        attempt = BoardExamAttempt.objects.get(pk=response.data["attempt_id"])

        self.assertEqual(attempt.deadline - attempt.started_at, timedelta(minutes=60))
        self.assertGreater(response.data["remaining_seconds"], 3500)


class BoardExamAttemptApiTests(BoardExamApiBase):
    def test_get_attempt_returns_active_state(self):
        started = self.start()
        attempt_id = self.attempt_id_from(started)

        response = self.client.get(reverse("board-exam-attempt", args=[attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BoardExamAttempt.Status.IN_PROGRESS)
        self.assertEqual(payload_contains_answer_leakage(response.data), [])

    def test_get_attempt_410_when_expired(self):
        started = self.start()
        attempt = BoardExamAttempt.objects.get(pk=self.attempt_id_from(started))
        self.force_deadline(attempt, seconds_from_now=-1)

        response = self.client.get(reverse("board-exam-attempt", args=[attempt.pk]))

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, BoardExamAttempt.Status.EXPIRED)

    def test_get_attempt_409_after_submit(self):
        started = self.start()
        attempt_id = self.attempt_id_from(started)
        self.client.post(reverse("board-exam-submit", args=[attempt_id]))

        response = self.client.get(reverse("board-exam-attempt", args=[attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_get_attempt_404_for_other_user(self):
        started = self.start()
        attempt_id = self.attempt_id_from(started)
        self.authenticate(self.other_user)

        response = self.client.get(reverse("board-exam-attempt", args=[attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BoardExamAnswerApiTests(BoardExamApiBase):
    def setUp(self):
        super().setUp()
        self.started = self.start()
        self.attempt_id = self.attempt_id_from(self.started)

    def answer_url(self, position=1, attempt_id=None):
        return reverse("board-exam-answer", args=[attempt_id or self.attempt_id, position])

    def test_answer_saves_selection(self):
        response = self.client.put(self.answer_url(3), {"selected_choice_key": "B"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["position"], 3)
        self.assertEqual(response.data["selected_choice_key"], "B")
        self.assertEqual(response.data["answered_count"], 1)
        self.assertIn("answered_at", response.data)
        self.assertIn("server_time", response.data)

    def test_answer_replacement_updates_single_item(self):
        self.client.put(self.answer_url(1), {"selected_choice_key": "B"}, format="json")
        response = self.client.put(self.answer_url(1), {"selected_choice_key": "D"}, format="json")

        self.assertEqual(response.data["selected_choice_key"], "D")
        self.assertEqual(response.data["answered_count"], 1)
        self.assertEqual(
            self.started.data["attempt_id"],
            str(BoardExamAttempt.objects.get(pk=self.attempt_id).pk),
        )

    def test_answer_requires_choice_key(self):
        response = self.client.put(self.answer_url(1), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("selected_choice_key", response.data)

    def test_answer_rejects_choice_not_in_question(self):
        response = self.client.put(self.answer_url(1), {"selected_choice_key": "Z"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_answer_unknown_position_returns_404(self):
        response = self.client.put(self.answer_url(999), {"selected_choice_key": "A"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_answer_position_from_other_attempt_returns_404(self):
        other_exam = make_exam(self.questions[5:], slug="second-exam", question_count=55)
        other = self.client.post(reverse("board-exam-start", args=[other_exam.slug]))
        other_attempt_id = other.data["attempt_id"]

        own = self.client.put(
            self.answer_url(55), {"selected_choice_key": "A"}, format="json"
        )
        foreign = self.client.put(
            self.answer_url(55, attempt_id=other_attempt_id),
            {"selected_choice_key": "A"},
            format="json",
        )

        self.assertEqual(own.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(foreign.status_code, status.HTTP_200_OK)

    def test_answer_404_for_other_user(self):
        self.authenticate(self.other_user)

        response = self.client.put(self.answer_url(1), {"selected_choice_key": "A"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_answer_409_after_submit(self):
        self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))

        response = self.client.put(self.answer_url(1), {"selected_choice_key": "A"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_answer_410_after_expiry(self):
        attempt = BoardExamAttempt.objects.get(pk=self.attempt_id)
        self.force_deadline(attempt, seconds_from_now=-1)

        response = self.client.put(self.answer_url(1), {"selected_choice_key": "A"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, BoardExamAttempt.Status.EXPIRED)

    def test_answer_ignores_client_supplied_scoring_fields(self):
        response = self.client.put(
            self.answer_url(1),
            {"selected_choice_key": "A", "is_correct": True, "score": 100, "time_taken": 1},
            format="json",
        )
        attempt = BoardExamAttempt.objects.get(pk=self.attempt_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(attempt.score, 0.0)
        self.assertEqual(attempt.correct_count, 0)
        self.assertEqual(attempt.time_taken_seconds, 0)


class BoardExamSubmitApiTests(BoardExamApiBase):
    def setUp(self):
        super().setUp()
        self.started = self.start()
        self.attempt_id = self.attempt_id_from(self.started)
        self.items = {item["position"]: item for item in self.started.data["items"]}

    def correct_key_for(self, position):
        return self.correct_keys[position]

    def answer_positions(self, positions, use_correct=True):
        for position in positions:
            if use_correct:
                key = self.correct_keys[position]
            else:
                key = next(
                    key
                    for key in ("A", "B", "C", "D", "E")
                    if key != self.correct_keys[position]
                )
            self.client.put(
                reverse("board-exam-answer", args=[self.attempt_id, position]),
                {"selected_choice_key": key},
                format="json",
            )

    def setUpItems(self):
        attempt = BoardExamAttempt.objects.get(pk=self.attempt_id)
        self.correct_keys = {
            item.position: item.solution_snapshot["correct_choice_key"]
            for item in attempt.items.all()
        }
        self.started_position_question = {
            item.position: item.question_id for item in attempt.items.all()
        }

    def test_submit_grades_answers_and_unanswered_as_incorrect(self):
        self.setUpItems()
        self.answer_positions([1, 2, 3], use_correct=True)
        self.answer_positions([4], use_correct=False)

        response = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BoardExamAttempt.Status.SUBMITTED)
        self.assertEqual(response.data["correct_count"], 3)
        self.assertEqual(response.data["total_questions"], 50)
        self.assertEqual(response.data["answered_count"], 4)
        self.assertEqual(response.data["unanswered_count"], 46)
        self.assertEqual(response.data["score"], 6.0)
        self.assertEqual(response.data["percentage"], 6.0)
        self.assertEqual(len(response.data["items"]), 50)
        self.assertTrue(response.data["items"][0]["is_correct"])
        self.assertFalse(response.data["items"][3]["is_correct"])
        self.assertFalse(response.data["items"][4]["is_answered"])

    def test_submit_is_idempotent(self):
        self.setUpItems()
        self.answer_positions([1], use_correct=True)

        first = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))
        second = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["correct_count"], second.data["correct_count"])
        self.assertEqual(first.data["finalized_at"], second.data["finalized_at"])
        self.assertEqual(
            BoardExamAttempt.objects.filter(
                pk=self.attempt_id, status=BoardExamAttempt.Status.SUBMITTED
            ).count(),
            1,
        )

    def test_submit_ignores_client_supplied_score_and_timing(self):
        self.setUpItems()

        response = self.client.post(
            reverse("board-exam-submit", args=[self.attempt_id]),
            {"score": 100, "correct_count": 50, "time_taken_seconds": 1, "status": "submitted"},
            format="json",
        )

        attempt = BoardExamAttempt.objects.get(pk=self.attempt_id)
        self.assertEqual(response.data["score"], 0.0)
        self.assertEqual(attempt.correct_count, 0)
        self.assertEqual(attempt.total_questions, 50)

    def test_submit_404_for_other_user(self):
        self.authenticate(self.other_user)

        response = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_results_before_submit_returns_409(self):
        response = self.client.get(reverse("board-exam-results", args=[self.attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("detail", response.data)


class BoardExamResultsApiTests(BoardExamApiBase):
    def setUp(self):
        super().setUp()
        self.started = self.start()
        self.attempt_id = self.attempt_id_from(self.started)
        self.attempt = BoardExamAttempt.objects.get(pk=self.attempt_id)

    def test_results_include_solutions_and_why_wrong(self):
        item = self.attempt.items.order_by("position").first()
        wrong_key = next(
            choice["choice_key"]
            for choice in item.public_snapshot["choices"]
            if choice["choice_key"] != item.solution_snapshot["correct_choice_key"]
        )
        self.client.put(
            reverse("board-exam-answer", args=[self.attempt_id, item.position]),
            {"selected_choice_key": wrong_key},
            format="json",
        )

        response = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))
        row = response.data["items"][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BoardExamAttempt.Status.SUBMITTED)
        self.assertEqual(row["selected_choice_key"], wrong_key)
        self.assertEqual(row["correct_choice_key"], item.solution_snapshot["correct_choice_key"])
        self.assertFalse(row["is_correct"])
        self.assertTrue(row["why_wrong"].startswith(f"Why {wrong_key} is wrong"))
        self.assertEqual(row["explanation"], item.solution_snapshot["explanation"])
        self.assertEqual(row["clinical_pearl"], item.solution_snapshot["clinical_pearl"])
        self.assertIn("references", row)
        self.assertIn("server_time", response.data)

    def test_results_available_after_expiry(self):
        self.force_deadline(self.attempt, seconds_from_now=-1)

        response = self.client.get(reverse("board-exam-results", args=[self.attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], BoardExamAttempt.Status.EXPIRED)
        self.assertEqual(response.data["unanswered_count"], 50)
        self.assertIsNotNone(response.data["finalized_at"])

    def test_results_404_for_other_user(self):
        self.authenticate(self.other_user)

        response = self.client.get(reverse("board-exam-results", args=[self.attempt_id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_results_404_for_unknown_attempt(self):
        response = self.client.get(reverse("board-exam-results", args=[99999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_results_time_is_capped_at_duration(self):
        BoardExamAttempt.objects.filter(pk=self.attempt_id).update(
            started_at=timezone.now() - timedelta(hours=3),
            deadline=timezone.now() - timedelta(hours=2),
        )
        self.attempt.refresh_from_db()

        response = self.client.post(reverse("board-exam-submit", args=[self.attempt_id]))

        self.assertEqual(response.data["status"], BoardExamAttempt.Status.EXPIRED)
        self.assertEqual(response.data["time_taken_seconds"], 3600)

    def test_active_exam_question_is_not_exposed_through_exam_payload(self):
        response = self.start()
        question_ids = {
            item.question_id for item in self.attempt.items.all()
        }

        self.assertEqual(payload_contains_answer_leakage(response.data), [])
        self.assertNotIn("question_id", response.data["items"][0])
        self.assertEqual(len(question_ids), 50)
