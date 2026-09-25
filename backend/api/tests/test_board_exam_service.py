import random
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api.models import BoardExamAttempt, BoardExamAttemptItem
from api.services.board_exam_service import (
    InsufficientQuestionPool,
    build_result_payload,
    eligible_exam_questions,
    expire_attempt_if_needed,
    normalize_stem,
    payload_contains_answer_leakage,
    record_answer,
    select_exam_questions,
    start_or_resume_attempt,
    submit_attempt,
)
from api.tests.factories import make_chapter, make_exam, make_question, make_questions, make_user


class BoardExamSelectionTests(TestCase):
    def test_selects_exactly_question_count_unique_questions(self):
        questions = make_questions(75)
        exam = make_exam(questions, question_count=50)
        user = make_user()

        selected = select_exam_questions(exam)

        self.assertEqual(len(selected), 50)
        self.assertEqual(len({q.pk for q in selected}), 50)
        self.assertTrue(set(q.pk for q in selected).issubset(set(q.pk for q in questions)))

    def test_selection_is_randomized_but_deterministic_for_seeded_rng(self):
        questions = make_questions(60)
        exam = make_exam(questions, question_count=50)

        first = [q.pk for q in select_exam_questions(exam, rng=random.Random(7))]
        second = [q.pk for q in select_exam_questions(exam, rng=random.Random(7))]
        different_seed = [q.pk for q in select_exam_questions(exam, rng=random.Random(99))]

        self.assertEqual(first, second)
        self.assertNotEqual(first, different_seed)

    def test_normalizes_stems_for_dedupe(self):
        self.assertEqual(
            normalize_stem("  A 70-year-old   man: BUN/Cr?  "),
            normalize_stem("a 70 year old man bun cr"),
        )

    def test_duplicate_normalized_stems_are_dropped(self):
        chapter = make_chapter()
        make_question(1, chapter=chapter, stem="Serum potassium is 6.8 mEq/L?")
        make_question(2, chapter=chapter, stem="  Serum   potassium is 6.8 mEq/L  ")
        make_question(3, chapter=chapter, stem="Different stem entirely?")
        exam = make_exam([*chapter.questions.all()], question_count=2)

        eligible = eligible_exam_questions(exam)

        self.assertEqual(len(eligible), 2)
        self.assertNotEqual(
            normalize_stem(eligible[0].question_text),
            normalize_stem(eligible[1].question_text),
        )

    def test_excludes_questions_with_invalid_choice_sets(self):
        chapter = make_chapter()
        valid = make_question(1, chapter=chapter)
        make_question(2, chapter=chapter, choice_count=1)
        make_question(3, chapter=chapter, choice_count=7)
        make_question(4, chapter=chapter, blank_choice_index=1)
        make_question(5, chapter=chapter, correct_keys=("A", "B"))
        make_question(6, chapter=chapter, correct_keys=("B", "C"))
        make_question(7, chapter=chapter, is_published=False)
        exam = make_exam(list(chapter.questions.all()), question_count=1)

        self.assertEqual([q.pk for q in eligible_exam_questions(exam)], [valid.pk])

    def test_excludes_questions_not_attached_to_exam(self):
        attached = make_questions(2)
        make_questions(3, chapter=make_chapter(slug="other", title="Other"))
        exam = make_exam(attached, question_count=2)

        self.assertEqual(len(eligible_exam_questions(exam)), 2)

    def test_chapter_quota_is_guaranteed_before_global_fill(self):
        quota_chapter = make_chapter(slug="hyperkalemia", title="Hyperkalemia")
        filler_chapter = make_chapter(slug="acidosis", title="Acidosis")
        quota_questions = make_questions(20, chapter=quota_chapter)
        filler_questions = make_questions(40, chapter=filler_chapter, start=100)
        exam = make_exam(
            [*quota_questions, *filler_questions],
            question_count=50,
            chapter_quota={"hyperkalemia": 10},
        )

        selected = select_exam_questions(exam, rng=random.Random(3))

        self.assertEqual(len(selected), 50)
        quota_selected = [q for q in selected if q.chapter_id == quota_chapter.id]
        self.assertGreaterEqual(len(quota_selected), 10)
        self.assertEqual(len({q.pk for q in selected}), 50)

    def test_quotas_larger_than_target_still_select_exactly_target(self):
        first_chapter = make_chapter(slug="hyperkalemia", title="Hyperkalemia")
        second_chapter = make_chapter(slug="acidosis", title="Acidosis")
        first_questions = make_questions(30, chapter=first_chapter)
        second_questions = make_questions(30, chapter=second_chapter, start=100)
        exam = make_exam(
            [*first_questions, *second_questions],
            question_count=50,
            chapter_quota={"hyperkalemia": 40, "acidosis": 40},
        )

        selected = select_exam_questions(exam, rng=random.Random(21))

        self.assertEqual(len(selected), 50)
        self.assertEqual(len({q.pk for q in selected}), 50)

    def test_chapter_quota_shortage_falls_back_to_global_pool(self):
        quota_chapter = make_chapter(slug="hyperkalemia", title="Hyperkalemia")
        filler_chapter = make_chapter(slug="acidosis", title="Acidosis")
        quota_questions = make_questions(3, chapter=quota_chapter)
        filler_questions = make_questions(50, chapter=filler_chapter, start=100)
        exam = make_exam(
            [*quota_questions, *filler_questions],
            question_count=50,
            chapter_quota={"hyperkalemia": 25},
        )

        selected = select_exam_questions(exam, rng=random.Random(11))

        self.assertEqual(len(selected), 50)
        self.assertEqual(
            len([q for q in selected if q.chapter_id == quota_chapter.id]), 3
        )

    def test_chapter_quota_list_form_is_supported(self):
        chapter = make_chapter(slug="hyperkalemia", title="Hyperkalemia")
        questions = make_questions(50, chapter=chapter)
        exam = make_exam(
            questions,
            question_count=50,
            chapter_quota=[{"chapter": "hyperkalemia", "count": 50}],
        )

        selected = select_exam_questions(exam, rng=random.Random(5))

        self.assertEqual(len(selected), 50)
        self.assertTrue(all(q.chapter_id == chapter.id for q in selected))

    def test_raises_when_pool_is_too_small(self):
        questions = make_questions(49)
        exam = make_exam(questions, question_count=50)

        with self.assertRaises(InsufficientQuestionPool):
            select_exam_questions(exam)

    def test_raises_when_duplicate_stems_shrink_the_pool(self):
        chapter = make_chapter()
        questions = [make_question(i, chapter=chapter, stem=f"Same stem number {i % 40}?") for i in range(60)]
        exam = make_exam(questions, question_count=50)

        with self.assertRaises(InsufficientQuestionPool):
            select_exam_questions(exam)


class BoardExamAttemptServiceTests(TestCase):
    def setUp(self):
        self.questions = make_questions(55)
        self.exam = make_exam(self.questions)
        self.user = make_user()

    def test_start_creates_attempt_with_snapshots_and_deadline(self):
        now = timezone.now()
        attempt, resumed = start_or_resume_attempt(self.user, self.exam, now=now)

        self.assertFalse(resumed)
        self.assertEqual(attempt.status, BoardExamAttempt.Status.IN_PROGRESS)
        self.assertEqual(attempt.total_questions, 50)
        self.assertEqual(
            attempt.deadline - attempt.started_at, timedelta(minutes=60)
        )
        items = list(attempt.items.order_by("position"))
        self.assertEqual(len(items), 50)
        self.assertEqual([item.position for item in items], list(range(1, 51)))
        for item in items:
            self.assertTrue(item.public_snapshot["question_text"])
            self.assertTrue(item.solution_snapshot["correct_choice_key"])
            self.assertNotIn("explanation", item.public_snapshot)
            self.assertNotIn("clinical_pearl", item.public_snapshot)
            self.assertNotIn("why_wrong", item.public_snapshot)

    def test_start_resumes_the_active_attempt(self):
        first, _ = start_or_resume_attempt(self.user, self.exam)
        second, resumed = start_or_resume_attempt(self.user, self.exam)

        self.assertTrue(resumed)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 1)

    def test_start_rejects_unpublished_exam(self):
        exam = make_exam(make_questions(50), slug="draft-exam", is_published=False)

        from api.services.board_exam_service import ExamNotPublished

        with self.assertRaises(ExamNotPublished):
            start_or_resume_attempt(self.user, exam)

    def test_start_creates_new_attempt_after_submission(self):
        first, _ = start_or_resume_attempt(self.user, self.exam)
        submit_attempt(first)

        second, resumed = start_or_resume_attempt(self.user, self.exam)

        self.assertFalse(resumed)
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 2)
        self.assertEqual(second.items.count(), self.exam.question_count)

    def test_start_creates_new_attempt_after_expiry(self):
        first, _ = start_or_resume_attempt(self.user, self.exam)
        first.deadline = first.started_at - timedelta(seconds=5)
        first.save(update_fields=["deadline"])

        second, resumed = start_or_resume_attempt(self.user, self.exam)

        self.assertFalse(resumed)
        self.assertNotEqual(first.pk, second.pk)
        first.refresh_from_db()
        self.assertEqual(first.status, BoardExamAttempt.Status.EXPIRED)
        self.assertEqual(BoardExamAttempt.objects.filter(user=self.user).count(), 2)

    def test_answer_replacement_is_idempotent(self):
        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        item = attempt.items.order_by("position").first()

        first = record_answer(attempt, item.position, "B")
        replaced = record_answer(attempt, item.position, "C")
        again = record_answer(attempt, item.position, "C")

        self.assertEqual(first.selected_choice_key, "B")
        self.assertEqual(replaced.selected_choice_key, "C")
        self.assertEqual(again.selected_choice_key, "C")
        self.assertEqual(attempt.items.filter(position=item.position).count(), 1)

    def test_grading_counts_unanswered_questions_incorrect(self):
        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        items = list(attempt.items.order_by("position"))
        for item in items[:4]:
            record_answer(attempt, item.position, item.solution_snapshot["correct_choice_key"])
        record_answer(attempt, items[4].position, "D" if items[4].solution_snapshot["correct_choice_key"] != "D" else "A")

        finalized = submit_attempt(attempt)

        self.assertEqual(finalized.status, BoardExamAttempt.Status.SUBMITTED)
        self.assertEqual(finalized.correct_count, 4)
        self.assertEqual(finalized.total_questions, 50)
        self.assertEqual(finalized.score, 8.0)
        self.assertLessEqual(finalized.time_taken_seconds, 3600)

    def test_submit_is_idempotent(self):
        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        item = attempt.items.order_by("position").first()
        record_answer(attempt, item.position, item.solution_snapshot["correct_choice_key"])

        first = submit_attempt(attempt)
        finalized_at = first.finalized_at
        second = submit_attempt(attempt)

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(second.status, BoardExamAttempt.Status.SUBMITTED)
        self.assertEqual(second.finalized_at, finalized_at)
        self.assertEqual(second.correct_count, 1)

    def test_lazy_expiry_finalizes_past_deadline(self):
        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        item = attempt.items.order_by("position").first()
        record_answer(attempt, item.position, item.solution_snapshot["correct_choice_key"])
        BoardExamAttempt.objects.filter(pk=attempt.pk).update(
            deadline=timezone.now() - timedelta(minutes=1)
        )
        attempt.refresh_from_db()

        self.assertTrue(expire_attempt_if_needed(attempt))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, BoardExamAttempt.Status.EXPIRED)
        self.assertIsNotNone(attempt.finalized_at)
        self.assertEqual(attempt.correct_count, 1)
        self.assertTrue(expire_attempt_if_needed(attempt) is False)

    def test_expired_attempt_rejects_new_answers(self):
        from api.services.board_exam_service import AttemptExpired

        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        BoardExamAttempt.objects.filter(pk=attempt.pk).update(
            deadline=timezone.now() - timedelta(seconds=1)
        )
        attempt.refresh_from_db()

        with self.assertRaises(AttemptExpired):
            record_answer(attempt, 1, "A")

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, BoardExamAttempt.Status.EXPIRED)

    def test_only_one_active_attempt_allowed(self):
        from django.db import IntegrityError, transaction

        start_or_resume_attempt(self.user, self.exam)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BoardExamAttempt.objects.create(
                    user=self.user,
                    exam=self.exam,
                    started_at=timezone.now(),
                    deadline=timezone.now() + timedelta(minutes=60),
                )

    def test_item_question_is_protected_from_deletion(self):
        from django.db.models import ProtectedError

        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        question = attempt.items.first().question

        with self.assertRaises(ProtectedError):
            question.delete()

    def test_unique_item_position_and_question(self):
        from django.db import IntegrityError, transaction

        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        first_item = attempt.items.order_by("position").first()
        other_question = self.questions[54]

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BoardExamAttemptItem.objects.create(
                    attempt=attempt,
                    question=other_question,
                    position=first_item.position,
                    public_snapshot={},
                    solution_snapshot={},
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BoardExamAttemptItem.objects.create(
                    attempt=attempt,
                    question=first_item.question,
                    position=999,
                    public_snapshot={},
                    solution_snapshot={},
                )

    def test_result_payload_reveals_solutions_only_after_finalize(self):
        from api.services.board_exam_service import AttemptInProgress

        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        with self.assertRaises(AttemptInProgress):
            build_result_payload(attempt)

        finalized = submit_attempt(attempt)
        payload = build_result_payload(finalized)

        self.assertEqual(payload["total_questions"], 50)
        self.assertEqual(payload["correct_count"], 0)
        self.assertEqual(payload["unanswered_count"], 50)
        self.assertEqual(payload["percentage"], 0.0)
        self.assertTrue(all(row["correct_choice_key"] for row in payload["items"]))
        self.assertTrue(all(row["is_correct"] is False for row in payload["items"]))

    def test_active_payload_has_no_answer_leakage(self):
        from api.services.board_exam_service import build_attempt_payload

        attempt, _ = start_or_resume_attempt(self.user, self.exam)
        payload = build_attempt_payload(attempt, resumed=False)

        self.assertEqual(payload_contains_answer_leakage(payload), [])
        self.assertEqual(payload["answered_count"], 0)
        self.assertEqual(len(payload["items"]), 50)
        self.assertFalse(payload["resumed"])
        self.assertIn("server_time", payload)
        self.assertIn("deadline", payload)
        self.assertIn("remaining_seconds", payload)
