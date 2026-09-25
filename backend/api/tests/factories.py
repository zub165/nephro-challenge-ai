from datetime import timedelta

from django.contrib.auth import get_user_model

from api.models import BoardExam, Category, Chapter, Choice, Question

User = get_user_model()

CHOICE_KEYS = ["A", "B", "C", "D", "E", "F", "G", "H"]


def make_category(name="Nephrology", slug="nephrology"):
    category, _ = Category.objects.get_or_create(
        slug=slug, defaults={"name": name, "order": 1}
    )
    return category


def make_chapter(slug="electrolytes", title="Electrolytes", category=None):
    chapter, _ = Chapter.objects.get_or_create(
        slug=slug,
        defaults={"title": title, "order_index": 1, "category": category or make_category()},
    )
    return chapter


def make_question(
    index,
    *,
    chapter=None,
    category=None,
    is_published=True,
    is_premium=False,
    correct_keys=("A",),
    choice_count=4,
    blank_choice_index=None,
    stem=None,
    explanation="Standard explanation",
    clinical_pearl="Pearl text",
    reference="",
):
    chapter = chapter or make_chapter()
    category = category or chapter.category or make_category()
    question = Question.objects.create(
        category=category,
        chapter=chapter,
        question_text=stem or f"Question {index}: which statement is correct?",
        explanation=explanation,
        clinical_pearl=clinical_pearl,
        reference=reference,
        difficulty="medium",
        is_published=is_published,
        is_premium=is_premium,
    )
    for order in range(choice_count):
        text = f"Choice {order + 1} for question {index}"
        if blank_choice_index is not None and order == blank_choice_index:
            text = "   "
        Choice.objects.create(
            question=question,
            choice_key=CHOICE_KEYS[order],
            choice_text=text,
            is_correct=CHOICE_KEYS[order] in correct_keys,
            why_wrong=f"Why {CHOICE_KEYS[order]} is wrong for {index}",
            order=order + 1,
        )
    return question


def make_questions(count, *, chapter=None, category=None, start=0, **kwargs):
    return [
        make_question(start + offset, chapter=chapter, category=category, **kwargs)
        for offset in range(count)
    ]


def make_exam(
    questions,
    *,
    slug="nephrology-board",
    title="Nephrology Board Review",
    question_count=50,
    duration_minutes=60,
    chapter_quota=None,
    is_published=True,
):
    exam = BoardExam.objects.create(
        slug=slug,
        title=title,
        description="Timed board-style exam",
        question_count=question_count,
        duration_minutes=duration_minutes,
        chapter_quota=chapter_quota if chapter_quota is not None else {},
        is_published=is_published,
    )
    exam.questions.set(questions)
    return exam


def make_user(username="examiner", password="Local-Test-9x", role=User.Role.FREE, **kwargs):
    return User.objects.create_user(
        username=username, password=password, role=role, **kwargs
    )


def attempt_started_minutes_ago(minutes):
    from django.utils import timezone

    return timezone.now() - timedelta(minutes=minutes)
