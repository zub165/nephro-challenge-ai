from django.contrib import admin

from api.models import (
    AIGeneratedQuestion,
    Answer,
    Category,
    Choice,
    Leaderboard,
    Question,
    QuizAttempt,
    SavedPearl,
    Subscription,
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


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = [
        "question_text",
        "category",
        "difficulty",
        "is_published",
        "times_answered",
        "times_correct",
        "created_at",
    ]
    list_filter = ["category", "difficulty", "is_published"]
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


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(AIGeneratedQuestion, AIGeneratedQuestionAdmin)
admin.site.register(SavedPearl, SavedPearlAdmin)
