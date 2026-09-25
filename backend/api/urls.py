from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    AccountDeleteView,
    AdminAIGeneratedQuestionsView,
    AdminAILearningView,
    AdminContentVerifyView,
    AdminImportMCQView,
    AdminQuestionDetailView,
    AdminQuestionReviewView,
    AdminQuestionsView,
    AdminStatsView,
    AIGenerateQuestionView,
    AIDetailedExplanationView,
    AIGenerateQuestionsView,
    AIExplainView,
    AITutorChatView,
    AppleAuthView,
    AuthViewSet,
    BoardPearlsView,
    BoardPrepView,
    MedicalReferencesView,
    CategoryViewSet,
    ChapterViewSet,
    DailyChallengeView,
    GoogleAuthView,
    LeaderboardViewSet,
    LessonDetailView,
    HealthCheckView,
    QuestionViewSet,
    QuizAnswerView,
    QuizAttemptViewSet,
    QuizChapterView,
    QuizDailyView,
    QuizExplanationView,
    QuizQuestionsView,
    StatsView,
    StudyNoteDetailView,
    StudyNotesListView,
    StudyNotesEnrichView,
    StudyNotesOrganizeView,
    StudyNotesReviewView,
    StudyNotesDedupeView,
    SubscriptionViewSet,
    TopicViewSet,
    UserProgressView,
    WeaknessView,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"chapters", ChapterViewSet, basename="chapter")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"attempts", QuizAttemptViewSet, basename="attempt")
router.register(r"leaderboard", LeaderboardViewSet, basename="leaderboard")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("auth/register/", AuthViewSet.as_view({"post": "register"}), name="auth-register"),
    path("auth/login/", AuthViewSet.as_view({"post": "login"}), name="auth-login"),
    path("auth/profile/", AuthViewSet.as_view({"get": "profile", "patch": "update_profile"}), name="auth-profile"),
    path("auth/account/", AccountDeleteView.as_view(), name="auth-account-delete"),
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
    path("auth/apple/", AppleAuthView.as_view(), name="auth-apple"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("ai/explain/", AIExplainView.as_view(), name="ai-explain"),
    path("ai/generate/", AIGenerateQuestionView.as_view(), name="ai-generate"),
    path("ai/explanation/detailed/", AIDetailedExplanationView.as_view(), name="ai-explanation-detailed"),
    path("ai/explanation/detailed", AIDetailedExplanationView.as_view(), name="ai-explanation-detailed-noslash"),
    path("ai/tutor/chat/", AITutorChatView.as_view(), name="ai-tutor-chat"),
    path("ai/tutor/chat", AITutorChatView.as_view(), name="ai-tutor-chat-noslash"),
    path("ai/questions/generate/", AIGenerateQuestionsView.as_view(), name="ai-questions-generate"),
    path("ai/questions/generate", AIGenerateQuestionsView.as_view(), name="ai-questions-generate-noslash"),
    path("ai/board-prep/", BoardPrepView.as_view(), name="ai-board-prep"),
    path("ai/board-prep", BoardPrepView.as_view(), name="ai-board-prep-noslash"),
    path("daily-challenge/", DailyChallengeView.as_view(), name="daily-challenge"),
    path("weaknesses/", WeaknessView.as_view(), name="weaknesses"),
    # Quiz API (plan-compatible)
    path("quiz/daily/", QuizDailyView.as_view(), name="quiz-daily"),
    path("quiz/chapter/<int:chapter_id>/", QuizChapterView.as_view(), name="quiz-chapter"),
    path("quiz/answer/", QuizAnswerView.as_view(), name="quiz-answer"),
    path("quiz/explanation/<int:mcq_id>/", QuizExplanationView.as_view(), name="quiz-explanation"),
    path("questions/quiz/", QuizQuestionsView.as_view(), name="questions-quiz"),
    path("quiz/attempts/", QuizAttemptViewSet.as_view({"post": "create"}), name="quiz-attempts"),
    # User progress & stats
    path("users/me/progress/", UserProgressView.as_view(), name="user-progress"),
    path("stats/", StatsView.as_view(), name="stats"),
    path("pearls/", BoardPearlsView.as_view(), name="board-pearls"),
    path("references/", MedicalReferencesView.as_view(), name="medical-references"),
    path("notes/enrich/", StudyNotesEnrichView.as_view(), name="notes-enrich"),
    path("notes/organize/", StudyNotesOrganizeView.as_view(), name="notes-organize"),
    path("notes/review/", StudyNotesReviewView.as_view(), name="notes-review"),
    path("notes/dedupe/", StudyNotesDedupeView.as_view(), name="notes-dedupe"),
    path("notes/<int:note_id>/", StudyNoteDetailView.as_view(), name="note-detail"),
    path("notes/", StudyNotesListView.as_view(), name="notes-list"),
    # Admin
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("admin/content/verify/", AdminContentVerifyView.as_view(), name="admin-content-verify"),
    path("admin/ai-learning/", AdminAILearningView.as_view(), name="admin-ai-learning"),
    path("admin/questions/ai-generated/", AdminAIGeneratedQuestionsView.as_view(), name="admin-ai-questions"),
    path("admin/questions/<int:question_id>/review/", AdminQuestionReviewView.as_view(), name="admin-question-review"),
    path("admin/questions/<int:question_id>/", AdminQuestionDetailView.as_view(), name="admin-question-detail"),
    path("admin/questions/", AdminQuestionsView.as_view(), name="admin-questions"),
    path("admin/import-mcqs/", AdminImportMCQView.as_view(), name="admin-import-mcqs"),
    path("lessons/<int:lesson_id>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("health/", HealthCheckView.as_view(), name="health"),
]

urlpatterns += router.urls
