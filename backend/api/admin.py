from django.contrib import admin

from api.models import (
    AIGeneratedQuestion,
    ReviewStatus,
    Answer,
    BoardExam,
    BoardExamAttempt,
    BoardExamAttemptItem,
    Category,
    Chapter,
    Choice,
    Leaderboard,
    Lesson,
    Question,
    QuizAttempt,
    SavedPearl,
    StudyNote,
    Subscription,
    Topic,
    User,
)


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "role",
        "specialty",
        "xp_points",
        "rank_score",
        "streak_count",
        "is_active",
    ]
    list_filter = ["role", "is_active"]
    search_fields = ["username", "email", "specialty"]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug", "order"]
    list_editable = ["order"]


class ChapterAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "slug", "order_index", "category"]
    list_editable = ["order_index"]


class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "chapter", "order_index"]
    list_filter = ["chapter"]


class MedicalReviewAdminMixin:
    readonly_fields = ["source_metadata", "reviewed_by", "reviewed_at"]
    medical_review_list_filter = ("review_status",)

    def get_list_filter(self, request):
        return tuple(self.list_filter) + self.medical_review_list_filter


class LessonAdmin(MedicalReviewAdminMixin, admin.ModelAdmin):
    list_display = [
        "title",
        "topic",
        "lesson_type",
        "duration_seconds",
        "review_status",
        "is_premium",
    ]
    list_filter = ["lesson_type", "is_premium"]
    search_fields = ["title", "summary"]
    fieldsets = (
        (None, {"fields": ("topic", "title", "lesson_type", "summary", "order_index")}),
        ("Content", {"fields": ("animation_url", "thumbnail_url", "content_md", "duration_seconds")}),
        ("Medical review", {"fields": ("review_status", "reviewed_by", "reviewed_at", "source_metadata")}),
        ("Access", {"fields": ("is_premium",)}),
    )


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionAdmin(MedicalReviewAdminMixin, admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = [
        "question_text",
        "category",
        "chapter",
        "difficulty",
        "review_status",
        "is_published",
        "times_answered",
        "times_correct",
        "created_at",
    ]
    list_filter = ["category", "chapter", "difficulty", "is_published"]
    search_fields = ["question_text", "subcategory"]
    list_editable = ["is_published"]
    fieldsets = (
        (None, {"fields": ("category", "chapter", "topic", "lesson", "subcategory", "difficulty")}),
        ("Stem", {"fields": ("case_text", "labs", "question_text", "image_url")}),
        ("Answer key", {"fields": ("explanation", "clinical_pearl", "reference")}),
        ("Medical review", {"fields": ("review_status", "reviewed_by", "reviewed_at", "source_metadata")}),
        ("Publication", {"fields": ("is_published", "is_premium")}),
        ("Stats", {"fields": ("times_answered", "times_correct", "created_by", "created_at", "updated_at")}),
    )
    actions = ["mark_reviewed", "mark_needs_review"]

    @admin.action(description="Mark selected questions as clinically reviewed")
    def mark_reviewed(self, request, queryset):
        from django.utils import timezone

        reviewer = request.user.get_username()
        updated = queryset.update(
            review_status=ReviewStatus.APPROVED,
            reviewed_by=reviewer,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} question(s) marked as reviewed by {reviewer}.")

    @admin.action(description="Move selected questions back to needs review")
    def mark_needs_review(self, request, queryset):
        updated = queryset.update(review_status=ReviewStatus.NEEDS_REVIEW, reviewed_by="", reviewed_at=None)
        self.message_user(request, f"{updated} question(s) moved to needs review.")


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "score", "total_questions", "time_taken", "completed_at"]
    list_filter = ["completed_at"]


class AnswerAdmin(admin.ModelAdmin):
    list_display = ["quiz_attempt", "question", "is_correct", "time_taken"]


class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ["user", "score", "period", "date"]
    list_filter = ["period", "date"]


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "start_date", "end_date", "is_active"]
    list_filter = ["plan", "is_active"]


class AIGeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "status", "created_at"]
    list_filter = ["status"]


class SavedPearlAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "created_at"]


class StudyNoteAdmin(admin.ModelAdmin):
    list_display = ["user", "chapter", "topic_title", "content", "created_at"]
    list_filter = ["chapter"]
    search_fields = ["content", "topic_title", "user__username"]


class BoardExamAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "slug", "question_count", "duration_minutes", "is_published", "created_at"]
    list_filter = ["is_published"]
    search_fields = ["title", "slug"]
    filter_horizontal = ["questions"]
    readonly_fields = ["created_at", "updated_at"]


class BoardExamAttemptItemInline(admin.TabularInline):
    model = BoardExamAttemptItem
    extra = 0
    fields = ["position", "question", "selected_choice_key", "answered_at"]
    readonly_fields = ["position", "question", "selected_choice_key", "answered_at"]
    ordering = ["position"]


class BoardExamAttemptAdmin(admin.ModelAdmin):
    inlines = [BoardExamAttemptItemInline]
    list_display = [
        "user",
        "exam",
        "status",
        "correct_count",
        "total_questions",
        "score",
        "time_taken_seconds",
        "started_at",
        "deadline",
        "finalized_at",
    ]
    list_filter = ["status", "exam"]
    search_fields = ["user__username", "exam__slug"]
    readonly_fields = ["user", "exam", "status", "correct_count", "total_questions", "score", "time_taken_seconds", "started_at", "deadline", "finalized_at", "created_at", "updated_at"]
    date_hierarchy = "created_at"


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(AIGeneratedQuestion, AIGeneratedQuestionAdmin)
admin.site.register(SavedPearl, SavedPearlAdmin)
admin.site.register(StudyNote, StudyNoteAdmin)
admin.site.register(BoardExam, BoardExamAdmin)
admin.site.register(BoardExamAttempt, BoardExamAttemptAdmin)
