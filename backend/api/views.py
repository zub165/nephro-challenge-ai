import random
from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, F, FloatField, Q
from django.db.models.functions import Extract
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import (
    AIGeneratedQuestion,
    Answer,
    Category,
    Leaderboard,
    Question,
    QuizAttempt,
    SavedPearl,
    Subscription,
)
from api.permissions import IsAdminOrEditor, IsOwnerOrReadOnly, IsPremiumOrReadOnly
from api.serializers import (
    AIGeneratedQuestionSerializer,
    CategorySerializer,
    ChoiceSerializer,
    LeaderboardSerializer,
    LoginSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuizAttemptCreateSerializer,
    QuizAttemptSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from api.services.ai_service import generate_explanation, generate_question

User = get_user_model()


def _get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class AuthViewSet(viewsets.ViewSet):
    """Authentication and user profile endpoints."""

    def get_permissions(self):
        if self.action in ("register", "login"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = _get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )

    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = _get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, **tokens},
        )

    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def update_profile(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """List, retrieve, and special actions for questions."""

    queryset = Question.objects.filter(is_published=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuestionDetailSerializer
        return QuestionListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        difficulty = self.request.query_params.get("difficulty")
        subcategory = self.request.query_params.get("subcategory")
        if category:
            qs = qs.filter(category__slug=category)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if subcategory:
            qs = qs.filter(subcategory__iexact=subcategory)
        return qs

    @action(detail=False, methods=["get"])
    def random_question(self, request):
        qs = self.get_queryset()
        category = request.query_params.get("category")
        difficulty = request.query_params.get("difficulty")
        if category:
            qs = qs.filter(category__slug=category)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        question = random.choice(list(qs)) if qs.exists() else None
        if not question:
            return Response({"detail": "No questions found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionDetailSerializer(question)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def daily_challenge(self, request):
        today = date.today()
        qs = self.get_queryset()
        # Deterministic seed based on date for consistent daily question
        seed = today.toordinal()
        qs_list = list(qs)
        if not qs_list:
            return Response({"detail": "No questions available"}, status=status.HTTP_404_NOT_FOUND)
        random.Random(seed).shuffle(qs_list)
        question = qs_list[0]
        serializer = QuestionDetailSerializer(question)
        return Response(serializer.data)


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """Create and list quiz attempts."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return QuizAttemptCreateSerializer
        return QuizAttemptSerializer

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user).select_related(
            "category"
        ).prefetch_related("answers__question__choices")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Leaderboard rankings."""

    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        period = self.request.query_params.get("period", "all_time")
        qs = Leaderboard.objects.select_related("user")
        if period in ("daily", "weekly", "monthly", "all_time"):
            qs = qs.filter(period=period)
        return qs.order_by("-score")[:100]

    @action(detail=False, methods=["get"])
    def user_rank(self, request):
        period = request.query_params.get("period", "all_time")
        entry = Leaderboard.objects.filter(
            user=request.user, period=period
        ).first()
        if not entry:
            return Response({"rank": None, "score": 0})
        rank = (
            Leaderboard.objects.filter(period=period, score__gt=entry.score).count() + 1
        )
        return Response({"rank": rank, "score": entry.score})


class AIExplainView(APIView):
    """POST with question_id to get an AI-generated explanation."""

    permission_classes = [IsPremiumOrReadOnly]

    def post(self, request):
        question_id = request.data.get("question_id")
        if not question_id:
            return Response({"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id, is_published=True)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        explanation = generate_explanation(question)
        return Response({"explanation": explanation})


class AIGenerateQuestionView(APIView):
    """POST with topic and difficulty to generate a draft question."""

    permission_classes = [IsPremiumOrReadOnly]

    def post(self, request):
        topic = request.data.get("topic", "")
        difficulty = request.data.get("difficulty", "medium")
        if not topic:
            return Response({"error": "topic is required"}, status=status.HTTP_400_BAD_REQUEST)
        result = generate_question(topic, difficulty)
        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ai_q = AIGeneratedQuestion.objects.create(
            question_text=result["question_text"],
            choices=result["choices"],
            correct_answer=result["correct_answer"],
            explanation=result.get("explanation", ""),
        )
        serializer = AIGeneratedQuestionSerializer(ai_q)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage user subscriptions."""

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DailyChallengeView(APIView):
    """GET endpoint returning today's challenge question."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        qs = Question.objects.filter(is_published=True)
        seed = today.toordinal()
        qs_list = list(qs)
        if not qs_list:
            return Response({"detail": "No questions available"}, status=status.HTTP_404_NOT_FOUND)
        random.Random(seed).shuffle(qs_list)
        question = qs_list[0]
        serializer = QuestionDetailSerializer(question)
        return Response(serializer.data)


class WeaknessView(APIView):
    """GET endpoint returning user's weak topics."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        answers = Answer.objects.filter(
            quiz_attempt__user=request.user, is_correct=False
        ).select_related("question__category")
        stats = (
            answers.values("question__category__name", "question__subcategory")
            .annotate(
                incorrect_count=Count("id"),
            )
            .order_by("-incorrect_count")[:10]
        )
        return Response(
            [
                {
                    "category": item["question__category__name"],
                    "subcategory": item["question__subcategory"],
                    "incorrect_count": item["incorrect_count"],
                }
                for item in stats
            ]
        )
