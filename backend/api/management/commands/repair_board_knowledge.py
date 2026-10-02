"""Merge legacy chapters, publish curriculum MCQs, and keep pearls exam-ready."""

from django.core.management.base import BaseCommand
from django.db import transaction

from api.data.board_prep_plan import BOARD_PREP_DAYS
from api.data.chapter_aliases import CANONICAL_CHAPTER_SLUGS, LEGACY_CHAPTER_SLUGS
from api.data.chapter_seed import CHAPTERS
from api.models import Chapter, Lesson, Question, StudyNote, Topic
from api.services.board_content_service import seed_curriculum
from api.services.board_exam_service import question_in_published_board_exam


def _high_yield_for(slug: str) -> list[str]:
    items: list[str] = []
    for day in BOARD_PREP_DAYS:
        if slug in (day.get("chapter_slugs") or []):
            items.extend(day.get("high_yield") or [])
    seen = set()
    unique = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


class Command(BaseCommand):
    help = "Fix chapter-wise knowledge base and pearls: merge aliases, publish seed MCQs."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        if dry:
            self.stdout.write("Dry run — no writes")
            self._report()
            return
        with transaction.atomic():
            seed_curriculum(CHAPTERS, publish_questions=True)
            moved = self._merge_legacy_chapters()
            published = self._publish_practice_questions()
        self.stdout.write(self.style.SUCCESS(f"Merged questions/notes from {moved} legacy chapters"))
        self.stdout.write(self.style.SUCCESS(f"Published {published} practice MCQs"))
        self._report()

    def _merge_legacy_chapters(self) -> int:
        moved = 0
        for old_slug, new_slug in LEGACY_CHAPTER_SLUGS.items():
            old = Chapter.objects.filter(slug=old_slug).first()
            new = Chapter.objects.filter(slug=new_slug).first()
            if not old or not new or old.id == new.id:
                continue
            for topic in list(old.topics.all()):
                existing = Topic.objects.filter(chapter=new, slug=topic.slug).first()
                if existing:
                    topic.lessons.update(topic=existing)
                    Question.objects.filter(topic=topic).update(topic=existing, chapter=new)
                    topic.delete()
                else:
                    topic.chapter = new
                    topic.save(update_fields=["chapter"])
            Question.objects.filter(chapter=old).update(chapter=new)
            StudyNote.objects.filter(chapter=old).update(chapter=new)
            old.delete()
            moved += 1
        return moved

    def _publish_practice_questions(self) -> int:
        count = 0
        qs = Question.objects.filter(
            is_published=False,
            chapter__slug__in=CANONICAL_CHAPTER_SLUGS,
        )
        for question in qs:
            if question_in_published_board_exam(question):
                continue
            question.is_published = True
            question.save(update_fields=["is_published"])
            count += 1
        return count

    def _report(self):
        for chapter in Chapter.objects.order_by("order_index"):
            q = chapter.questions.filter(is_published=True).count()
            lessons = Lesson.objects.filter(topic__chapter=chapter).count()
            self.stdout.write(
                f"{chapter.slug}: published_q={q} lessons={lessons} topics={chapter.topics.count()}"
            )
