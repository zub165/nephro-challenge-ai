from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.FREE,
    )
    specialty = models.CharField(max_length=100, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, default="")
    display_name = models.CharField(max_length=100, blank=True, default="")
    streak_count = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)
    xp_points = models.PositiveIntegerField(default=0)
    rank_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rank_score"]

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class Chapter(models.Model):
    """Board-review chapter (e.g. Electrolytes, AKI). Maps to plan `chapters` table."""

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    order_index = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="BookOpenIcon")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chapters",
    )

    class Meta:
        ordering = ["order_index"]

    def __str__(self) -> str:
        return self.title


class Topic(models.Model):
    """Sub-topic within a chapter (e.g. Hyperkalemia under Electrolytes)."""

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="topics",
    )
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    order_index = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["order_index"]
        unique_together = ["chapter", "slug"]

    def __str__(self) -> str:
        return f"{self.chapter.title} — {self.title}"


class Lesson(models.Model):
    """Learning content: animation URL stored externally (R2/S3); only URL in DB."""

    class LessonType(models.TextChoices):
        ANIMATION = "animation", "Animation"
        ARTICLE = "article", "Article"
        VIDEO = "video", "Video"

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.ANIMATION,
    )
    summary = models.TextField(blank=True, default="")
    content_md = models.TextField(blank=True, default="")
    animation_url = models.URLField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    duration_seconds = models.PositiveIntegerField(default=0)
    order_index = models.PositiveIntegerField(default=0)
    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ["order_index"]

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"
        BOARD = "board", "Board"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    subcategory = models.CharField(max_length=100, blank=True, default="")
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
    )
    case_text = models.TextField(blank=True, default="")
    labs = models.JSONField(blank=True, default=dict)
    question_text = models.TextField()
    explanation = models.TextField(blank=True, default="")
    clinical_pearl = models.TextField(blank=True, default="")
    reference = models.TextField(blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    times_answered = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.question_text[:80]


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    choice_key = models.CharField(max_length=2, blank=True, default="")
    choice_text = models.TextField()
    why_wrong = models.TextField(blank=True, default="")
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ["question", "choice_key"]

    def __str__(self) -> str:
        return self.choice_text[:60]


class QuizAttempt(models.Model):
    class Mode(models.TextChoices):
        DAILY = "daily", "Daily"
        PRACTICE = "practice", "Practice"
        CHAPTER = "chapter", "Chapter"
        CATEGORY = "category", "Category"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.PRACTICE,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_attempts",
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_attempts",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_attempts",
    )
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    time_taken = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.score}/{self.total_questions}"


class Answer(models.Model):
    quiz_attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    chosen_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_correct = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Q: {self.question_id} - {'Correct' if self.is_correct else 'Incorrect'}"


class Leaderboard(models.Model):
    class Period(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ALL_TIME = "all_time", "All Time"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leaderboard_entries",
    )
    score = models.FloatField(default=0.0)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    period = models.CharField(
        max_length=10,
        choices=Period.choices,
        default=Period.ALL_TIME,
    )
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-score"]
        unique_together = ["user", "period", "date"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.period} - {self.score}"


class Subscription(models.Model):
    class Plan(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.CharField(
        max_length=10,
        choices=Plan.choices,
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.plan}"


class AIGeneratedQuestion(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    question_text = models.TextField()
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_questions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.question_text[:80]


class SavedPearl(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_pearls",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="saved_pearls",
    )
    pearl_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "question"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.question_id}"


class StudyNote(models.Model):
    """User-pasted study notes organized by board-review chapter."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="study_notes",
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_notes",
    )
    topic_title = models.CharField(max_length=150, blank=True, default="")
    content = models.TextField()
    reference = models.TextField(blank=True, default="")
    verified = models.BooleanField(null=True, blank=True)
    verification_confidence = models.CharField(max_length=10, blank=True, default="")
    verification_issues = models.JSONField(blank=True, default=list)
    source_batch_id = models.CharField(max_length=64, blank=True, default="")
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["chapter__order_index", "order_index", "-created_at"]

    def __str__(self) -> str:
        chapter_title = self.chapter.title if self.chapter_id else "Uncategorized"
        return f"{self.user.username} — {chapter_title}: {self.content[:50]}"


class AIKnowledgeEntry(models.Model):
    """Approved corrections and rules injected into Ollama prompts (RAG-style learning)."""

    class ContentType(models.TextChoices):
        PEARL = "pearl", "Pearl"
        MCQ = "mcq", "MCQ"
        RULE = "rule", "Rule"
        ADMIN = "admin", "Admin"

    class Source(models.TextChoices):
        LLAMA_AUDIT = "llama_audit", "LLaMA audit"
        RULE_CHECK = "rule_check", "Rule check"
        ADMIN = "admin", "Admin"
        VERIFICATION = "verification", "Verification"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    topic = models.CharField(max_length=150, db_index=True, blank=True, default="")
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.RULE)
    original_text = models.TextField(blank=True, default="")
    corrected_text = models.TextField(blank=True, default="")
    lesson_rule = models.TextField(
        help_text="Short rule injected into future AI prompts (e.g. hyponatremia correction limits).",
    )
    reference = models.TextField(blank=True, default="")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.RULE_CHECK)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    confidence = models.CharField(max_length=10, blank=True, default="medium")
    use_count = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_ai_lessons",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "topic"]),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.topic or 'General'}: {self.lesson_rule[:60]}"
