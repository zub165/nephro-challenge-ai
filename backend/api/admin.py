from django.contrib import admin

from api.models import (
    AIGeneratedQuestion,
    Answer,
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


class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "lesson_type", "duration_seconds", "is_premium"]
    list_filter = ["lesson_type", "is_premium"]
    search_fields = ["title", "summary"]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = [
        "question_text",
        "category",
        "chapter",
        "difficulty",
        "is_published",
        "times_answered",
        "times_correct",
        "created_at",
    ]
    list_filter = ["category", "chapter", "difficulty", "is_published"]
    search_fields = ["question_text", "subcategory"]
    list_editable = ["is_published"]


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
