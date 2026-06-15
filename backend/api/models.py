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
    streak_count = models.PositiveIntegerField(default=0)
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


class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
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
    image_url = models.URLField(blank=True, default="")
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
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.choice_text[:60]


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_attempts",
    )
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    time_taken = models.PositiveIntegerField(default=0)
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
