import json

from django.core.management.base import BaseCommand, CommandError

from api.data.board_exam_seed import (
    BOARD_EXAM_DURATION_MINUTES,
    BOARD_EXAM_QUESTION_COUNT,
    BOARD_EXAM_SLUG,
    SEED_REVIEW_STATUS,
    validate_board_seed,
)
from api.services.board_content_service import BoardExamPublishBlocked, seed_board_exam

CLINICIAN_REVIEW_WARNING = (
    "Seeded content is original teaching material that has NOT been reviewed by a "
    "nephrologist or ABIM-certified clinician. Keep the exam unpublished until a "
    "qualified reviewer sets review_status=approved on its questions and lessons."
)


class Command(BaseCommand):
    help = (
        "Seed the weighted nephrology board exam (chapters, lessons, questions, "
        "and exam) idempotently. Unpublished by default; use --publish to publish."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Publish the exam after validation passes. Requires clinician review.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the seed data and report the plan without writing to the database.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print the seed report as JSON.",
        )

    def _write_stats(self, stats, as_json):
        if as_json:
            return
        self.stdout.write(
            f"Chapters: {stats['chapters']}, topics: {stats['topics']}, "
            f"lessons: {stats['lessons']}, questions: {stats['questions']}, "
            f"animations: {stats['animations_referenced']}/{stats['animations_present']} referenced"
        )
        for chapter_slug, count in stats["questions_per_chapter"].items():
            self.stdout.write(f"  {chapter_slug}: {count} question(s)")

    def handle(self, *args, **options):
        publish = options["publish"]
        dry_run = options["dry_run"]
        as_json = options["json"]

        report = validate_board_seed()
        self._write_stats(report["stats"], as_json)
        for warning in report["warnings"]:
            self.stdout.write(self.style.WARNING(f"warning: {warning}"))
        if report["errors"]:
            for error in report["errors"]:
                self.stderr.write(self.style.ERROR(f"invalid: {error}"))
            raise CommandError(
                f"Board exam seed validation failed with {len(report['errors'])} error(s); "
                "nothing was written"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Validated {report['stats']['questions']} questions across "
                f"{report['stats']['chapters']} chapters "
                f"({BOARD_EXAM_QUESTION_COUNT} per exam, {BOARD_EXAM_DURATION_MINUTES} minutes)"
            )
        )
        self.stdout.write(self.style.WARNING(CLINICIAN_REVIEW_WARNING))

        if dry_run:
            self.stdout.write("Dry run: no database changes made")
            return

        try:
            result = seed_board_exam(publish=publish)
        except BoardExamPublishBlocked as blocked:
            self.stderr.write(self.style.ERROR(f"Publication refused: {blocked}"))
            self.stderr.write(
                "Approve the seeded questions in Django admin "
                "(Questions -> review_status = approved) until every chapter meets "
                "its quota, then re-run with --publish."
            )
            raise CommandError("nothing was published") from blocked
        curriculum = result["curriculum"]
        self.stdout.write(
            f"Curriculum: {curriculum['chapters_created']} chapter(s) created, "
            f"{curriculum['topics_created']} topic(s) created, "
            f"{curriculum['lessons_created']} lesson(s) created / "
            f"{curriculum['lessons_updated']} updated, "
            f"{curriculum['questions_created']} question(s) created / "
            f"{curriculum['questions_updated']} updated, "
            f"{curriculum['choices_written']} choice(s) written"
        )
        for missing in curriculum["missing_categories"]:
            self.stdout.write(self.style.WARNING(f"category not found: {missing}"))

        exam = result["exam"]
        self.stdout.write(
            f"Exam '{exam.slug}' ({BOARD_EXAM_SLUG}) attached to "
            f"{result['questions_attached']} question(s), "
            f"quota {BOARD_EXAM_QUESTION_COUNT} questions / {BOARD_EXAM_DURATION_MINUTES} minutes"
        )
        for chapter_slug, count in result["questions_per_chapter"].items():
            quota = exam.chapter_quota.get(chapter_slug, 0)
            approved = result["approved_per_chapter"].get(chapter_slug, 0)
            style = self.style.SUCCESS if count >= quota else self.style.ERROR
            self.stdout.write(
                style(
                    f"  {chapter_slug}: {count} in pool, quota {quota}, "
                    f"{approved} clinician-approved"
                )
            )

        if exam.is_published:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Exam published with {result['published_questions']} newly "
                    f"published question(s). Current seed review_status={SEED_REVIEW_STATUS}."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Exam left unpublished and no questions were published, so the "
                    "live practice pool is unchanged."
                )
            )
            self.stdout.write(
                "Review the seeded questions in Django admin, set "
                "review_status=approved, then re-run with --publish."
            )

        if as_json:
            self.stdout.write(
                json.dumps(
                    {
                        "stats": report["stats"],
                        "curriculum": curriculum,
                        "exam": {
                            "slug": exam.slug,
                            "title": exam.title,
                            "question_count": exam.question_count,
                            "duration_minutes": exam.duration_minutes,
                            "chapter_quota": exam.chapter_quota,
                            "questions_attached": result["questions_attached"],
                            "approved_per_chapter": result["approved_per_chapter"],
                            "published_questions": result["published_questions"],
                            "is_published": exam.is_published,
                        },
                        "questions_per_chapter": result["questions_per_chapter"],
                        "review_status": SEED_REVIEW_STATUS,
                        "review_warning": CLINICIAN_REVIEW_WARNING,
                    },
                    indent=2,
                    default=str,
                )
            )
