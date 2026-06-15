from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import (
    AIGenerateQuestionView,
    AIExplainView,
    AuthViewSet,
    CategoryViewSet,
    DailyChallengeView,
    LeaderboardViewSet,
    QuestionViewSet,
    QuizAttemptViewSet,
    SubscriptionViewSet,
    WeaknessView,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"attempts", QuizAttemptViewSet, basename="attempt")
router.register(r"leaderboard", LeaderboardViewSet, basename="leaderboard")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("auth/register/", AuthViewSet.as_view({"post": "register"}), name="auth-register"),
    path("auth/login/", AuthViewSet.as_view({"post": "login"}), name="auth-login"),
    path("auth/profile/", AuthViewSet.as_view({"get": "profile", "patch": "update_profile"}), name="auth-profile"),
    path("ai/explain/", AIExplainView.as_view(), name="ai-explain"),
    path("ai/generate/", AIGenerateQuestionView.as_view(), name="ai-generate"),
    path("daily-challenge/", DailyChallengeView.as_view(), name="daily-challenge"),
    path("weaknesses/", WeaknessView.as_view(), name="weaknesses"),
]

urlpatterns += router.urls
