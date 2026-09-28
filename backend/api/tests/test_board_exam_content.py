"""Tests for the seeded board exam content, taxonomy, and seeding commands."""

import copy
import json
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from api.data.board_exam_seed import (
    ANIMATION_ASSET_DIR,
    BOARD_EXAM_DURATION_MINUTES,
    BOARD_EXAM_QUESTION_COUNT,
    BOARD_EXAM_SLUG,
    CHAPTER_QUOTA,
    EXPECTED_CHAPTER_ORDER,
    BoardSeedValidationError,
    assert_valid_board_seed,
    iter_seed_lessons,
    iter_seed_mcqs,
    validate_board_seed,
)
from api.data.board_pearls import BOARD_PEARLS
from api.data.chapter_seed import ANIMATION_BASE, CHAPTERS
from api.data.medical_references import MEDICAL_REFERENCES
from api.models import BoardExam, Category, Chapter, Choice, Lesson, Question, ReviewStatus, Topic
from api.services.board_content_service import seed_board_exam, seed_curriculum
from api.services.board_exam_service import select_exam_questions


class BoardSeedDataTests(TestCase):
    """The committed seed data must satisfy every content rule before publication."""

    def test_taxonomy_has_ten_chapters_in_required_order(self):
        self.assertEqual(len(CHAPTERS), 10)
        self.assertEqual(
            [(chapter["slug"], chapter["title"]) for chapter in CHAPTERS],
            EXPECTED_CHAPTER_ORDER,
        )
        self.assertEqual(
            [chapter["order_index"] for chapter in CHAPTERS], list(range(1, 11))
        )

    def test_every_chapter_slug_and_title_is_unique(self):
        slugs = [chapter["slug"] for chapter in CHAPTERS]
        titles = [chapter["title"] for chapter in CHAPTERS]
        self.assertEqual(len(set(slugs)), 10)
        self.assertEqual(len(set(titles)), 10)

    def test_seed_contains_at_least_sixty_questions(self):
        questions = list(iter_seed_mcqs())
        self.assertGreaterEqual(len(questions), 60)

    def test_every_chapter_pool_covers_its_quota_with_a_spare(self):
        per_chapter: dict[str, int] = {}
        for chapter, _topic, _mcq in iter_seed_mcqs():
            per_chapter[chapter["slug"]] = per_chapter.get(chapter["slug"], 0) + 1
        for chapter_slug, quota in CHAPTER_QUOTA.items():
            self.assertGreaterEqual(per_chapter.get(chapter_slug, 0), quota + 1)

    def test_exam_configuration_is_fifty_questions_in_sixty_minutes(self):
        self.assertEqual(BOARD_EXAM_QUESTION_COUNT, 50)
        self.assertEqual(BOARD_EXAM_DURATION_MINUTES, 60)
        self.assertEqual(sum(CHAPTER_QUOTA.values()), BOARD_EXAM_QUESTION_COUNT)
        self.assertEqual(len(CHAPTER_QUOTA), 10)
        self.assertEqual(set(CHAPTER_QUOTA), {slug for slug, _ in EXPECTED_CHAPTER_ORDER})

    def test_question_stems_are_unique_after_normalization(self):
        from api.services.board_exam_service import normalize_stem

        stems = [normalize_stem(mcq["question_text"]) for _c, _t, mcq in iter_seed_mcqs()]
        self.assertEqual(len(stems), len(set(stems)))

    def test_every_question_has_one_correct_answer_and_full_explanations(self):
        for chapter, topic, mcq in iter_seed_mcqs():
            where = f"{chapter['slug']}/{topic['slug']}"
            with self.subTest(where=where, stem=mcq["question_text"][:40]):
                choices = mcq["choices"]
                self.assertGreaterEqual(len(choices), 2)
                self.assertLessEqual(len(choices), 6)
                self.assertEqual(sum(1 for c in choices if c[2]), 1)
                for key, text, is_correct, why_wrong in choices:
                    self.assertTrue(text.strip())
                    if not is_correct:
                        self.assertTrue((why_wrong or "").strip())
                self.assertTrue(mcq["case_text"].strip())
                self.assertTrue(mcq["explanation"].strip())
                self.assertTrue(mcq["clinical_pearl"].strip())
                self.assertTrue(mcq["reference_ids"])

    def test_every_question_links_to_a_lesson_in_its_own_topic(self):
        for chapter, topic, mcq in iter_seed_mcqs():
            lesson_slugs = {lesson["lesson_slug"] for lesson in topic.get("lessons", [])}
            self.assertIn(mcq["lesson_slug"], lesson_slugs)

    def test_lesson_slugs_match_their_titles(self):
        from django.utils.text import slugify

        for _chapter, _topic, lesson in iter_seed_lessons():
            self.assertEqual(lesson["lesson_slug"], slugify(lesson["title"]))

    def test_every_reference_id_resolves_to_a_registered_source(self):
        for _chapter, _topic, item in list(iter_seed_mcqs()) + list(iter_seed_lessons()):
            for reference_id in item["reference_ids"]:
                self.assertIn(reference_id, MEDICAL_REFERENCES)

    def test_lesson_animations_exist_and_all_assets_are_referenced(self):
        referenced = {
            lesson["animation_url"].rsplit("/", 1)[-1]
            for _c, _t, lesson in iter_seed_lessons()
            if lesson.get("animation_url")
        }
        present = {path.name for path in ANIMATION_ASSET_DIR.glob("*.json")}
        self.assertTrue(present, "animation asset directory is missing")
        self.assertEqual(referenced, present)
        for _c, _t, lesson in iter_seed_lessons():
            if lesson.get("lesson_type") == "animation":
                self.assertTrue(lesson["animation_url"].startswith(f"{ANIMATION_BASE}/"))
                self.assertGreater(lesson["duration_seconds"], 0)
            else:
                self.assertTrue(lesson.get("content_md", "").strip())

    def test_animation_assets_are_valid_json_with_steps(self):
        for path in sorted(ANIMATION_ASSET_DIR.glob("*.json")):
            with self.subTest(animation=path.name):
                payload = json.loads(path.read_text())
                self.assertIsInstance(payload, dict)
                steps = payload.get("steps") or payload.get("frames")
                self.assertIsInstance(steps, list)
                self.assertTrue(steps)

    def test_every_chapter_has_a_valid_board_pearl(self):
        chapter_slugs = {chapter["slug"] for chapter in CHAPTERS}
        pearl_slugs = {pearl["chapter_slug"] for pearl in BOARD_PEARLS}
        self.assertEqual(pearl_slugs, chapter_slugs)
        for pearl in BOARD_PEARLS:
            for reference_id in pearl["reference_ids"]:
                self.assertIn(reference_id, MEDICAL_REFERENCES)

    def test_validator_reports_no_errors(self):
        report = validate_board_seed()
        self.assertEqual(report["errors"], [])
        self.assertGreaterEqual(report["stats"]["questions"], 60)

    def test_validator_rejects_duplicate_question_stems(self):
        chapters = copy.deepcopy(CHAPTERS)
        first = chapters[0]["topics"][0]["mcqs"][0]
        chapters[0]["topics"][0]["mcqs"].append(copy.deepcopy(first))

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        self.assertTrue(any("duplicate question stem" in error for error in report["errors"]))
        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            with self.assertRaises(BoardSeedValidationError):
                assert_valid_board_seed()

    def test_validator_rejects_multiple_correct_answers(self):
        chapters = copy.deepcopy(CHAPTERS)
        choices = chapters[0]["topics"][0]["mcqs"][0]["choices"]
        choices[1] = (choices[1][0], choices[1][1], True, None)

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        self.assertTrue(any("expected 1" in error for error in report["errors"]))

    def test_validator_rejects_missing_explanation_pearl_and_references(self):
        chapters = copy.deepcopy(CHAPTERS)
        mcq = chapters[0]["topics"][0]["mcqs"][0]
        mcq["explanation"] = ""
        mcq["clinical_pearl"] = "   "
        mcq["reference_ids"] = []
        mcq["reference_ids"] = ["not-a-real-reference"]

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        joined = " ".join(report["errors"])
        self.assertIn("no explanation", joined)
        self.assertIn("no clinical_pearl", joined)
        self.assertIn("unknown reference id", joined)

    def test_validator_rejects_unknown_reference_ids(self):
        chapters = copy.deepcopy(CHAPTERS)
        chapters[1]["topics"][0]["lessons"][0]["reference_ids"] = ["missing-source"]

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        self.assertTrue(any("unknown reference id" in error for error in report["errors"]))

    def test_validator_rejects_mislinked_question_lesson(self):
        chapters = copy.deepcopy(CHAPTERS)
        chapters[2]["topics"][0]["mcqs"][0]["lesson_slug"] = "lesson-from-another-topic"

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        self.assertTrue(any("is not a lesson of this topic" in error for error in report["errors"]))

    def test_validator_rejects_chapter_order_drift(self):
        chapters = copy.deepcopy(CHAPTERS)
        chapters[0], chapters[1] = chapters[1], chapters[0]

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        joined = " ".join(report["errors"])
        self.assertIn("expected 'acid-base-disorders'", joined)
        self.assertIn("order_index is 2, expected 1", joined)

    def test_validator_rejects_an_underfilled_chapter_pool(self):
        chapters = copy.deepcopy(CHAPTERS)
        for chapter in chapters:
            for topic in chapter["topics"]:
                topic["mcqs"] = topic["mcqs"][:1]
        for topic in chapters[0]["topics"]:
            topic["mcqs"] = topic["mcqs"] * 6

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        joined = " ".join(report["errors"])
        self.assertIn("quota is 5", joined)
        self.assertIn("minimum is 60", joined)

    def test_validator_rejects_invalid_choice_counts(self):
        chapters = copy.deepcopy(CHAPTERS)
        chapters[0]["topics"][0]["mcqs"][0]["choices"] = chapters[0]["topics"][0]["mcqs"][0][
            "choices"
        ][:1]

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            report = validate_board_seed()

        self.assertTrue(any("expected 2-6" in error for error in report["errors"]))

    def test_validator_rejects_unreferenced_animation_files(self):
        stray = ANIMATION_ASSET_DIR / "stray-unused-animation.json"
        stray.write_text(json.dumps({"steps": [{"title": "Unused"}]}), encoding="utf-8")
        self.addCleanup(stray.unlink)

        report = validate_board_seed()

        self.assertTrue(
            any("stray-unused-animation.json" in error for error in report["errors"])
        )

    def test_validator_rejects_missing_animation_files(self):
        target = ANIMATION_ASSET_DIR / "tubulointerstitial-cystic.json"
        original = target.read_text(encoding="utf-8")
        target.unlink()
        self.addCleanup(lambda: target.write_text(original, encoding="utf-8"))

        report = validate_board_seed()

        self.assertTrue(
            any("tubulointerstitial-cystic.json is missing" in error for error in report["errors"])
        )


class SeedBoardExamCommandTests(TestCase):
    """The command must be idempotent, unpublished by default, and validated."""

    def _call(self, *args):
        out = StringIO()
        call_command("seed_board_exam", *args, stdout=out, stderr=out)
        return out.getvalue()

    def _approve_all_questions(self):
        Question.objects.update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
        )

    def test_dry_run_writes_nothing(self):
        self._call("--dry-run")

        self.assertEqual(Chapter.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(BoardExam.objects.count(), 0)

    def test_command_creates_unpublished_exam_with_quota(self):
        output = self._call()

        exam = BoardExam.objects.get(slug=BOARD_EXAM_SLUG)
        self.assertFalse(exam.is_published)
        self.assertEqual(exam.question_count, BOARD_EXAM_QUESTION_COUNT)
        self.assertEqual(exam.duration_minutes, BOARD_EXAM_DURATION_MINUTES)
        self.assertEqual(exam.chapter_quota, CHAPTER_QUOTA)
        self.assertEqual(exam.questions.count(), 75)
        self.assertIn("left unpublished", output)
        self.assertIn("NOT been reviewed by a nephrologist", output)

    def test_seeding_never_publishes_questions(self):
        self._call()

        self.assertFalse(Question.objects.filter(is_published=True).exists())
        self.assertTrue(Question.objects.filter(review_status=ReviewStatus.NEEDS_REVIEW).exists())

    def test_publish_is_refused_until_questions_are_clinician_approved(self):
        self._call()

        out = StringIO()
        with self.assertRaises(CommandError):
            call_command("seed_board_exam", "--publish", stdout=out, stderr=out)

        self.assertFalse(BoardExam.objects.get(slug=BOARD_EXAM_SLUG).is_published)
        self.assertFalse(Question.objects.filter(is_published=True).exists())
        self.assertIn("Publication refused", out.getvalue())

    def test_publish_flag_publishes_exam_and_approved_questions(self):
        self._call()
        self._approve_all_questions()

        self._call("--publish")

        self.assertTrue(BoardExam.objects.get(slug=BOARD_EXAM_SLUG).is_published)
        self.assertEqual(Question.objects.filter(is_published=True).count(), 75)

    def test_rerunning_is_idempotent(self):
        self._call()
        self._call()
        self._call()
        self._approve_all_questions()
        self._call("--publish")

        self.assertEqual(Chapter.objects.count(), 10)
        self.assertEqual(Topic.objects.count(), 39)
        self.assertEqual(Lesson.objects.count(), 58)
        self.assertEqual(Question.objects.count(), 75)
        self.assertEqual(Choice.objects.count(), 300)
        self.assertEqual(BoardExam.objects.count(), 1)
        self.assertEqual(BoardExam.objects.get(slug=BOARD_EXAM_SLUG).questions.count(), 75)

    def test_seeded_content_records_source_and_review_metadata(self):
        self._call()

        question = Question.objects.filter(review_status=ReviewStatus.NEEDS_REVIEW).first()
        self.assertEqual(question.source_metadata["origin"], "seed")
        self.assertEqual(question.source_metadata["kind"], "question")
        self.assertIn("review_note", question.source_metadata)
        self.assertTrue(question.source_metadata["references"])
        self.assertTrue(question.reference)
        self.assertEqual(question.lesson.review_status, ReviewStatus.NEEDS_REVIEW)
        self.assertEqual(question.lesson.source_metadata["kind"], "lesson")
        self.assertEqual(question.reviewed_by, "")
        self.assertIsNone(question.reviewed_at)

    def test_seeded_categories_match_chapter_category_slugs(self):
        self._call()

        for chapter in Chapter.objects.select_related("category").all():
            self.assertIsNotNone(chapter.category)
        seeded_slugs = set(Category.objects.values_list("slug", flat=True))
        self.assertEqual(
            {chapter["category_slug"] for chapter in CHAPTERS} - seeded_slugs, set()
        )

    def test_published_exam_selects_fifty_unique_questions_with_quota(self):
        self._call()
        self._approve_all_questions()
        self._call("--publish")
        exam = BoardExam.objects.get(slug=BOARD_EXAM_SLUG)

        selected = select_exam_questions(exam)

        self.assertEqual(len(selected), BOARD_EXAM_QUESTION_COUNT)
        stems = [question.question_text for question in selected]
        self.assertEqual(len(stems), len(set(stems)))
        counts: dict[str, int] = {}
        for question in selected:
            counts[question.chapter.slug] = counts.get(question.chapter.slug, 0) + 1
        for chapter_slug, quota in CHAPTER_QUOTA.items():
            self.assertEqual(counts.get(chapter_slug, 0), quota)

    def test_command_fails_atomically_when_validation_fails(self):
        chapters = copy.deepcopy(CHAPTERS)
        chapters[0]["topics"][0]["mcqs"][0]["explanation"] = ""

        with mock.patch("api.data.board_exam_seed.CHAPTERS", chapters):
            with self.assertRaises(CommandError):
                self._call()

        self.assertEqual(Chapter.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(BoardExam.objects.count(), 0)

    def test_json_output_reports_counts_and_review_state(self):
        out = StringIO()
        call_command("seed_board_exam", "--json", stdout=out)

        payload = json.loads(out.getvalue()[out.getvalue().index("{") :])
        self.assertEqual(payload["exam"]["question_count"], BOARD_EXAM_QUESTION_COUNT)
        self.assertEqual(payload["exam"]["chapter_quota"], CHAPTER_QUOTA)
        self.assertEqual(payload["review_status"], ReviewStatus.NEEDS_REVIEW)
        self.assertFalse(payload["exam"]["is_published"])


class SeedContentServiceTests(TestCase):
    def test_seed_curriculum_can_be_called_with_explicit_chapters(self):
        chapters = [
            {
                "slug": "custom-chapter",
                "title": "Custom Chapter",
                "order_index": 1,
                "description": "Only chapter for this test",
                "category_slug": "electrolyte-disorders",
                "icon": "ActivityIcon",
                "topics": [
                    {
                        "slug": "custom-topic",
                        "title": "Custom Topic",
                        "lessons": [
                            {
                                "title": "Custom Lesson",
                                "lesson_slug": "custom-lesson",
                                "lesson_type": "article",
                                "summary": "A short lesson",
                                "content_md": "Body text",
                                "duration_seconds": 60,
                                "reference_ids": ["kdigo-ckd-2024"],
                            }
                        ],
                        "mcqs": [
                            {
                                "difficulty": "easy",
                                "case_text": "A short case",
                                "labs": {"k": "5.0 mEq/L"},
                                "question_text": "Which statement about potassium is true?",
                                "explanation": "Explanation",
                                "clinical_pearl": "Pearl",
                                "reference_ids": ["aha-hyperk-2015"],
                                "lesson_slug": "custom-lesson",
                                "choices": [
                                    ("A", "Correct", True, None),
                                    ("B", "Wrong", False, "Because it is wrong"),
                                ],
                            }
                        ],
                    }
                ],
            }
        ]

        report = seed_curriculum(chapters)

        self.assertEqual(report.questions_created, 1)
        self.assertEqual(report.choices_written, 2)
        self.assertEqual(report.missing_categories, [])
        question = Question.objects.get()
        self.assertEqual(question.lesson.title, "Custom Lesson")
        self.assertEqual(question.category.slug, "electrolyte-disorders")
        self.assertTrue(question.is_published)

    def test_seed_exam_repairs_edited_choices_and_keeps_answers_consistent(self):
        seed_board_exam()
        question = Question.objects.filter(chapter__slug="acid-base-disorders").first()
        question.choices.update(choice_text="Stale text", why_wrong="")

        seed_board_exam()

        question.refresh_from_db()
        self.assertEqual(question.choices.count(), 4)
        self.assertNotIn("Stale text", question.choices.values_list("choice_text", flat=True))
        for choice in question.choices.all():
            if not choice.is_correct:
                self.assertTrue(choice.why_wrong.strip())

    def test_unchanged_approved_content_keeps_its_review_state(self):
        seed_board_exam()
        question = Question.objects.first()
        Question.objects.filter(pk=question.pk).update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
        )

        result = seed_board_exam()

        question.refresh_from_db()
        self.assertFalse(result["exam"].is_published)
        self.assertEqual(question.review_status, ReviewStatus.APPROVED)
        self.assertEqual(question.reviewed_by, "Dr. Reviewer")
        self.assertIn(question.pk, result["exam"].questions.values_list("pk", flat=True))

    def test_edited_approved_content_is_reset_to_needs_review(self):
        chapters = copy.deepcopy(CHAPTERS)
        target = chapters[0]["topics"][0]["mcqs"][0]
        seed_board_exam()
        question = Question.objects.get(question_text=target["question_text"])
        Question.objects.filter(pk=question.pk).update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
            source_metadata={
                **(question.source_metadata or {}),
                "content_fingerprint": "stale-fingerprint",
            },
        )

        seed_curriculum(chapters)

        question.refresh_from_db()
        self.assertEqual(question.review_status, ReviewStatus.NEEDS_REVIEW)
        self.assertEqual(question.reviewed_by, "")

    def test_unchanged_approved_lesson_keeps_its_review_state(self):
        seed_board_exam()
        lesson = Lesson.objects.filter(image_url="").first() or Lesson.objects.first()
        Lesson.objects.filter(pk=lesson.pk).update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
        )

        seed_curriculum(copy.deepcopy(CHAPTERS))

        lesson.refresh_from_db()
        self.assertEqual(lesson.review_status, ReviewStatus.APPROVED)
        self.assertEqual(lesson.reviewed_by, "Dr. Reviewer")

    def test_attaching_a_figure_does_not_reset_an_approved_lesson(self):
        """A figure changes what the page shows, not what the lesson teaches."""
        chapters = copy.deepcopy(CHAPTERS)
        topic = chapters[0]["topics"][0]
        lesson_data = next(
            item for item in topic["lessons"] if not item.get("image_url")
        )
        lesson_data["image_url"] = "https://example.test/figure.webp"
        lesson_data["thumbnail_url"] = "https://example.test/figure-thumb.webp"
        lesson_data.pop("interactive_url", None)

        seed_curriculum(copy.deepcopy(CHAPTERS))
        lesson = Lesson.objects.get(title=lesson_data["title"])
        Lesson.objects.filter(pk=lesson.pk).update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
        )

        seed_curriculum(chapters)

        lesson.refresh_from_db()
        self.assertEqual(lesson.review_status, ReviewStatus.APPROVED)
        self.assertEqual(lesson.reviewed_by, "Dr. Reviewer")
        self.assertEqual(lesson.image_url, "https://example.test/figure.webp")

    def test_edited_approved_lesson_text_is_still_reset_to_needs_review(self):
        chapters = copy.deepcopy(CHAPTERS)
        topic = chapters[0]["topics"][0]
        lesson_data = next(item for item in topic["lessons"] if not item.get("image_url"))
        lesson_data["content_md"] = (lesson_data.get("content_md") or "") + "\n\nRevised text."

        seed_curriculum(copy.deepcopy(CHAPTERS))
        lesson = Lesson.objects.get(title=lesson_data["title"])
        Lesson.objects.filter(pk=lesson.pk).update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by="Dr. Reviewer",
            reviewed_at=timezone.now(),
        )

        seed_curriculum(chapters)

        lesson.refresh_from_db()
        self.assertEqual(lesson.review_status, ReviewStatus.NEEDS_REVIEW)
        self.assertEqual(lesson.reviewed_by, "")

    def test_lesson_media_changes_are_tracked_separately_from_content(self):
        seed_curriculum(copy.deepcopy(CHAPTERS))
        with_media = Lesson.objects.exclude(image_url="").first()
        without_media = Lesson.objects.filter(image_url="").first()
        self.assertIsNotNone(with_media)

        self.assertNotEqual(
            with_media.source_metadata["content_fingerprint"],
            without_media.source_metadata["content_fingerprint"],
        )
        for lesson in (with_media, without_media):
            self.assertIn("media_fingerprint", lesson.source_metadata)

    def test_rejected_questions_are_excluded_from_the_exam_pool(self):
        seed_board_exam()
        rejected = Question.objects.first()
        Question.objects.filter(pk=rejected.pk).update(review_status=ReviewStatus.REJECTED)

        result = seed_board_exam()

        self.assertNotIn(rejected.pk, result["exam"].questions.values_list("pk", flat=True))
        self.assertEqual(result["questions_attached"], 74)

    def test_questions_from_legacy_content_are_excluded_from_the_exam_pool(self):
        """Older `seed_data` questions can sit in a seeded chapter but must not be pooled.

        Production showed both shapes of legacy row: source_metadata with an empty
        chapter_slug, and source_metadata with no chapter_slug key at all.
        """
        seed_board_exam()
        chapter = Chapter.objects.get(slug=CHAPTERS[0]["slug"])
        legacy_rows = [
            Question.objects.create(
                question_text="Legacy question stamped with an empty chapter slug",
                category=chapter.category,
                chapter=chapter,
                explanation="Legacy explanation",
                review_status=ReviewStatus.NEEDS_REVIEW,
                source_metadata={
                    "origin": "seed",
                    "kind": "question",
                    "chapter_slug": "",
                    "topic_slug": "",
                },
            ),
            Question.objects.create(
                question_text="Legacy question with no chapter slug recorded",
                category=chapter.category,
                chapter=chapter,
                explanation="Legacy explanation",
                review_status=ReviewStatus.NEEDS_REVIEW,
                source_metadata={},
            ),
        ]

        result = seed_board_exam()

        attached = list(result["exam"].questions.values_list("pk", flat=True))
        for legacy in legacy_rows:
            self.assertNotIn(legacy.pk, attached)
        self.assertEqual(len(attached), 75)
        self.assertTrue(
            all(
                (q.source_metadata or {}).get("chapter_slug") == q.chapter.slug
                for q in Question.objects.filter(pk__in=attached)
            )
        )


class AnimationAssetTests(TestCase):
    def test_new_chapter_animations_are_committed_assets(self):
        for filename in ("tubulointerstitial-cystic.json", "nephrology-pharmacology.json"):
            with self.subTest(animation=filename):
                path = Path(ANIMATION_ASSET_DIR) / filename
                self.assertTrue(path.is_file())
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertGreaterEqual(len(payload.get("steps", [])), 4)


class SeedVerificationRuleTests(TestCase):
    """Seeded content must pass the repo's own rule-based verifier with no issues."""

    def test_every_seeded_mcq_and_pearl_passes_rule_based_verification(self):
        from api.services.content_verification_service import verify_mcq, verify_pearl

        for chapter, topic, mcq in iter_seed_mcqs():
            with self.subTest(mcq=f"{chapter['slug']}/{topic['slug']}"):
                result = verify_mcq(
                    question_text=mcq["question_text"],
                    explanation=mcq["explanation"],
                    clinical_pearl=mcq["clinical_pearl"],
                    reference_ids=mcq["reference_ids"],
                    use_llm=False,
                )
                self.assertEqual(result["verification"]["issues"], [])

        for pearl in BOARD_PEARLS:
            with self.subTest(pearl=pearl["topic"]):
                result = verify_pearl(pearl=dict(pearl), use_llm=False)
                self.assertEqual(result["verification"]["issues"], [])

    def test_board_pearls_group_under_seeded_chapters(self):
        from rest_framework.test import APIClient

        from api.data.board_pearls import BOARD_PEARLS
        from api.tests.factories import make_user

        call_command("seed_board_exam")
        client = APIClient()
        client.force_authenticate(user=make_user(username="pearl-reader"))

        response = client.get("/api/pearls/")

        self.assertEqual(response.status_code, 200)
        grouped = {entry["chapter"]["slug"]: entry for entry in response.data["chapters"]}
        self.assertEqual(set(grouped), {chapter["slug"] for chapter in CHAPTERS})
        self.assertEqual([entry["chapter"]["slug"] for entry in response.data["chapters"]],
                         [chapter["slug"] for chapter in CHAPTERS])
        curated = [
            pearl
            for entry in response.data["chapters"]
            for pearl in entry["pearls"]
            if pearl["source"] == "curated"
        ]
        self.assertEqual(len(curated), len(BOARD_PEARLS))
        self.assertEqual(response.data["total"], sum(entry["count"] for entry in response.data["chapters"]))
