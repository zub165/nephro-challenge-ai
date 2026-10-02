import math
import random
import uuid
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, F, FloatField, Q
from django.db.models.functions import Extract
from django.shortcuts import get_object_or_404
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
    BoardExam,
    BoardExamAttempt,
    Category,
    Chapter,
    Choice,
    Last48HourFact,
    Leaderboard,
    Lesson,
    Question,
    QuizAttempt,
    SavedPearl,
    StudyNote,
    Subscription,
    Topic,
)
from api.permissions import IsAdminOrEditor, IsOwnerOrReadOnly, IsPremiumOrReadOnly
from api.serializers import (
    AIGeneratedQuestionSerializer,
    BoardExamAnswerSerializer,
    BoardExamDetailSerializer,
    BoardExamSerializer,
    BoardPrepSettingsSerializer,
    Last48HourFactSerializer,
    CategorySerializer,
    ChapterDetailSerializer,
    ChapterSerializer,
    ChoiceSerializer,
    LeaderboardSerializer,
    LessonSerializer,
    LoginSerializer,
    MCQImportSerializer,
    QuestionDetailSerializer,
    QuestionExplanationSerializer,
    QuestionListSerializer,
    QuizAttemptCreateSerializer,
    QuizAttemptSerializer,
    StudyNoteSerializer,
    StudyNoteUpdateSerializer,
    SubscriptionSerializer,
    StudyNotesEnrichSerializer,
    StudyNotesOrganizeSerializer,
    TopicDetailSerializer,
    TopicSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from api.services.ai_service import (
    BOARD_PREP_TOPICS,
    chat_with_tutor,
    detailed_explanation,
    generate_board_prep_questions,
    generate_explanation,
    generate_question,
    generate_questions,
)
from api.services.board_exam_service import (
    BoardExamError,
    answered_count,
    build_attempt_payload,
    build_result_payload,
    exclude_board_exam_questions,
    expire_attempt_if_needed,
    question_in_published_board_exam,
    record_answer,
    start_or_resume_attempt,
    submit_attempt,
)
from api.services.leaderboard_service import build_leaderboard, user_leaderboard_rank
from api.data.board_prep_plan import BOARD_PREP_DAYS
from api.data.chapter_aliases import LEGACY_CHAPTER_SLUGS, canonical_slug, slugs_for_query
from api.services.notes_enrichment_service import enrich_note_payload, enrich_study_note, references_for_study_note
from api.services.notes_service import normalize_note_content, organize_pasted_notes

User = get_user_model()

DAILY_CHALLENGE_SIZE = 5


def _parse_limit(value, default: int = 10, maximum: int = 100) -> int:
    try:
        parsed = int(value)
        return max(1, min(parsed, maximum))
    except (TypeError, ValueError):
        return default


def _chapter_q(slug: str | None) -> Q:
    return Q(chapter__slug__in=slugs_for_query(slug))


def _high_yield_for_chapter(slug: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for day in BOARD_PREP_DAYS:
        if slug not in (day.get("chapter_slugs") or []):
            continue
        for item in day.get("high_yield") or []:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    return items


def _grouped_board_pearls(user, chapter_slug: str | None = None, include_notes: bool = False):
    from api.data.board_pearls import BOARD_PEARLS
    from api.data.medical_references import enrich_pearl, references_for_topic, resolve_reference_field

    chapter_slug = canonical_slug(chapter_slug)
    chapters = Chapter.objects.exclude(slug__in=LEGACY_CHAPTER_SLUGS.keys()).order_by("order_index")
    if chapter_slug:
        chapters = chapters.filter(slug=chapter_slug)
    chapter_map = {c.slug: c for c in chapters}
    grouped: dict = {}

    def add_pearl(slug: str | None, item: dict):
        slug = canonical_slug(slug)
        if not slug or slug not in chapter_map:
            return
        if slug not in grouped:
            ch = chapter_map[slug]
            grouped[slug] = {
                "chapter": {
                    "id": str(ch.id),
                    "title": ch.title,
                    "slug": slug,
                    "order_index": ch.order_index,
                },
                "pearls": [],
            }
        grouped[slug]["pearls"].append(item)

    seen_text: set[str] = set()
    for p in BOARD_PEARLS:
        mapped_slug = canonical_slug(p["chapter_slug"])
        if chapter_slug and mapped_slug != chapter_slug:
            continue
        text = p["pearl"].strip()
        if text.lower() in seen_text:
            continue
        seen_text.add(text.lower())
        enriched = enrich_pearl({**p, "pearl": text})
        add_pearl(mapped_slug, {
            "topic": enriched["topic"],
            "pearl": text,
            "mnemonic": enriched.get("mnemonic"),
            "source": "curated",
            "references": enriched.get("references", []),
        })

    db_qs = exclude_board_exam_questions(
        Question.objects.filter(is_published=True)
    ).exclude(clinical_pearl="").select_related("chapter", "topic")
    if chapter_slug:
        db_qs = db_qs.filter(_chapter_q(chapter_slug))
    for q in db_qs:
        text = q.clinical_pearl.strip()
        if not text or text.lower() in seen_text:
            continue
        seen_text.add(text.lower())
        slug = canonical_slug(q.chapter.slug if q.chapter_id else None)
        if slug and slug in chapter_map:
            refs = resolve_reference_field(q.reference or "")
            if not refs:
                topic = q.topic.title if q.topic_id else (q.subcategory or "From MCQ")
                refs = references_for_topic(topic, slug)
            add_pearl(slug, {
                "topic": q.topic.title if q.topic_id else (q.subcategory or "From MCQ"),
                "pearl": text,
                "mnemonic": None,
                "source": "mcq",
                "references": refs,
            })

    if include_notes and user and getattr(user, "is_authenticated", False):
        note_qs = StudyNote.objects.filter(user=user).exclude(chapter__isnull=True).select_related("chapter")
        if chapter_slug:
            note_qs = note_qs.filter(_chapter_q(chapter_slug))
        for note in note_qs:
            text = note.content.strip()
            if len(text) > 220 or not text or text.lower() in seen_text:
                continue
            seen_text.add(text.lower())
            add_pearl(note.chapter.slug if note.chapter_id else None, {
                "topic": note.topic_title or "My Pearl",
                "pearl": text,
                "mnemonic": None,
                "source": "my_book",
                "note_id": str(note.id),
                "references": references_for_study_note(note),
                "verified": note.verified,
                "verification_confidence": note.verification_confidence or None,
            })

    result = sorted(list(grouped.values()), key=lambda x: x["chapter"]["order_index"])
    for g in result:
        g["count"] = len(g["pearls"])
    total = sum(g["count"] for g in result)
    return result, total


def _user_is_premium(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role in (User.Role.PREMIUM, User.Role.ADMIN):
        return True
    try:
        sub = user.subscription
        return sub.is_active and sub.end_date > timezone.now()
    except Subscription.DoesNotExist:
        return False


def _published_questions_for_user(user):
    qs = Question.objects.filter(is_published=True)
    if not _user_is_premium(user):
        qs = qs.filter(is_premium=False)
    return exclude_board_exam_questions(qs).prefetch_related("choices")


def _daily_attempt_completed(user, today: date):
    """Return (completed, score) when user finished all daily challenge questions."""
    attempt = (
        QuizAttempt.objects.filter(
            user=user,
            mode=QuizAttempt.Mode.DAILY,
            completed_at__date=today,
        )
        .annotate(answer_count=Count("answers"))
        .filter(answer_count__gte=DAILY_CHALLENGE_SIZE)
        .order_by("-completed_at")
        .first()
    )
    if attempt:
        return True, attempt.score
    return False, None


def _unique_username(base: str) -> str:
    candidate = base[:150] or "user"
    if not User.objects.filter(username__iexact=candidate).exists():
        return candidate
    suffix = uuid.uuid4().hex[:6]
    return f"{candidate[:140]}_{suffix}"


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
        data = serializer.validated_data.copy()
        if User.objects.filter(username__iexact=data.get("username", "")).exists():
            data["username"] = _unique_username(data.get("username", "user"))
        try:
            user = User(**{k: v for k, v in data.items() if k != "password"})
            user.set_password(data["password"])
            user.save()
        except IntegrityError:
            return Response(
                {"message": "Username or email already in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tokens = _get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "token": tokens["access"], **tokens},
            status=status.HTTP_201_CREATED,
        )

    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = _get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "token": tokens["access"], **tokens},
        )

    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def update_profile(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


def _token_response_for_user(user):
    tokens = _get_tokens_for_user(user)
    return {"user": UserSerializer(user).data, "token": tokens["access"], **tokens}


def _resolve_oauth_user(email, given_name=None, family_name=None):
    if not email:
        return None
    display_name = " ".join(n for n in [given_name, family_name] if n).strip()
    user = User.objects.filter(email__iexact=email).first()
    if user:
        if display_name and not user.name and not user.display_name:
            user.name = display_name
            user.display_name = display_name
            user.save(update_fields=["name", "display_name"])
        return user
    base = (email.split("@")[0] or "user")[:30]
    username = _unique_username(base)
    user = User(username=username, email=email, name=display_name or None, display_name=display_name or None)
    user.set_unusable_password()
    try:
        user.save()
    except IntegrityError:
        user = User.objects.filter(email__iexact=email).first()
    return user


class GoogleAuthView(APIView):
    """POST /api/auth/google/ — exchange GoogleSignIn id_token for JWT."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        id_token_value = request.data.get("id_token") or request.data.get("identity_token")
        if not id_token_value:
            return Response({"detail": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token as google_id_token

            claims = google_id_token.verify_oauth2_token(
                id_token_value,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Invalid Google token: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = _resolve_oauth_user(
            claims.get("email"),
            claims.get("given_name"),
            claims.get("family_name"),
        )
        if not user:
            return Response({"detail": "Google account has no verified email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_token_response_for_user(user))


class AppleAuthView(APIView):
    """POST /api/auth/apple/ — exchange Sign in with Apple identity token for JWT."""

    permission_classes = [AllowAny]
    authentication_classes = []

    APPLE_ISSUER = "https://appleid.apple.com"
    APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"

    def post(self, request):
        identity_token = request.data.get("identity_token")
        if not identity_token:
            return Response({"detail": "identity_token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            import jwt as apple_jwt
            from jwt import PyJWKClient

            jwks_client = PyJWKClient(self.APPLE_JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(identity_token)
            claims = apple_jwt.decode(
                identity_token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.APPLE_ISSUER,
                audience=settings.APPLE_CLIENT_ID,
                options={"verify_aud": bool(settings.APPLE_CLIENT_ID)},
            )
        except Exception as exc:
            return Response(
                {"detail": f"Invalid Apple token: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = claims.get("email")
        if not email:
            apple_user = request.data.get("email")
            if apple_user:
                email = apple_user
        user = _resolve_oauth_user(
            email,
            request.data.get("given_name"),
            request.data.get("family_name"),
        )
        if not user:
            return Response({"detail": "Apple sign-in requires a verified email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_token_response_for_user(user))


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve categories."""

    queryset = Category.objects.annotate(
        question_count=Count("questions", filter=Q(questions__is_published=True))
    )
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
        qs = _published_questions_for_user(self.request.user)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()
        # Return the marked attempt (score + per-answer reveal), not the bare create payload.
        out = QuizAttemptSerializer(attempt, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user).select_related(
            "category"
        ).prefetch_related("answers__question__choices")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


def _board_exam_error_response(exc: BoardExamError) -> Response:
    return Response({"detail": exc.message}, status=exc.status_code)


def _owned_board_exam_attempt(user, attempt_id) -> BoardExamAttempt:
    return get_object_or_404(
        BoardExamAttempt.objects.select_related("exam"),
        pk=attempt_id,
        user=user,
    )


class BoardExamViewSet(viewsets.ReadOnlyModelViewSet):
    """Published board exams available to the signed-in user."""

    queryset = BoardExam.objects.filter(is_published=True)
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardExamDetailSerializer
        return BoardExamSerializer


class BoardExamStartView(APIView):
    """POST /api/board-exams/<slug>/start/ — start a new attempt or resume the active one."""

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        exam = get_object_or_404(BoardExam, slug=slug, is_published=True)
        try:
            attempt, resumed = start_or_resume_attempt(request.user, exam)
            payload = build_attempt_payload(attempt, resumed=resumed)
        except BoardExamError as exc:
            return _board_exam_error_response(exc)
        return Response(payload)


class BoardExamAttemptView(APIView):
    """GET /api/board-exams/attempts/<attempt_id>/ — active exam state for the owner."""

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = _owned_board_exam_attempt(request.user, attempt_id)
        if expire_attempt_if_needed(attempt):
            attempt.refresh_from_db()
        if attempt.status == BoardExamAttempt.Status.EXPIRED:
            return Response(
                {"detail": "Board exam attempt has expired"},
                status=status.HTTP_410_GONE,
            )
        if attempt.status != BoardExamAttempt.Status.IN_PROGRESS:
            return Response(
                {"detail": "Board exam attempt is already finalized"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(build_attempt_payload(attempt))


class BoardExamAttemptAnswerView(APIView):
    """PUT /api/board-exams/attempts/<attempt_id>/items/<position>/ — save or replace one answer."""

    permission_classes = [IsAuthenticated]

    def put(self, request, attempt_id, position):
        attempt = _owned_board_exam_attempt(request.user, attempt_id)
        serializer = BoardExamAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = record_answer(
                attempt,
                position,
                serializer.validated_data["selected_choice_key"],
            )
        except BoardExamError as exc:
            return _board_exam_error_response(exc)
        return Response(
            {
                "attempt_id": str(attempt.pk),
                "position": item.position,
                "selected_choice_key": item.selected_choice_key,
                "answered_at": item.answered_at.isoformat() if item.answered_at else None,
                "answered_count": answered_count(attempt),
                "total_questions": attempt.total_questions,
                "server_time": timezone.now().isoformat(),
            }
        )


class BoardExamAttemptSubmitView(APIView):
    """POST /api/board-exams/attempts/<attempt_id>/submit/ — finalize and grade (idempotent)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        attempt = _owned_board_exam_attempt(request.user, attempt_id)
        try:
            finalized = submit_attempt(attempt)
            payload = build_result_payload(finalized)
        except BoardExamError as exc:
            return _board_exam_error_response(exc)
        return Response(payload)


class BoardExamAttemptResultsView(APIView):
    """GET /api/board-exams/attempts/<attempt_id>/results/ — graded review for a finalized attempt."""

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = _owned_board_exam_attempt(request.user, attempt_id)
        try:
            payload = build_result_payload(attempt)
        except BoardExamError as exc:
            return _board_exam_error_response(exc)
        return Response(payload)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Leaderboard rankings computed from quiz attempts."""

    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Leaderboard.objects.none()

    def list(self, request, *args, **kwargs):
        period = request.query_params.get("period", "all_time")
        if period not in ("daily", "weekly", "monthly", "all_time"):
            period = "all_time"
        entries = build_leaderboard(period=period)
        return Response({"count": len(entries), "results": entries})

    @action(detail=False, methods=["get"])
    def user_rank(self, request):
        period = request.query_params.get("period", "all_time")
        if period not in ("daily", "weekly", "monthly", "all_time"):
            period = "all_time"
        return Response(user_leaderboard_rank(request.user, period))


class AIExplainView(APIView):
    """POST with question_id to get an AI-generated explanation."""

    permission_classes = [IsAuthenticated, IsPremiumOrReadOnly]

    def post(self, request):
        question_id = request.data.get("question_id")
        if not question_id:
            return Response({"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id, is_published=True)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        if question_in_published_board_exam(question):
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        explanation = generate_explanation(question)
        return Response({"explanation": explanation})


class AIGenerateQuestionView(APIView):
    """POST with topic and difficulty to generate a draft question."""

    permission_classes = [IsAuthenticated, IsPremiumOrReadOnly]

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


class AITutorChatView(APIView):
    """POST /api/ai/tutor/chat/ — conversational AI tutor.

    Body: { "message": str, "history": [{role, content}, ...] }
    Returns: { "response": str }
    """

    permission_classes = [IsAuthenticated, IsPremiumOrReadOnly]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)
        history = request.data.get("history") or []
        response = chat_with_tutor(message, history)
        if not response:
            return Response(
                {
                    "response": (
                        "The AI tutor is currently unavailable. Please try again in a "
                        "moment. Meanwhile, review the question explanations and clinical pearls."
                    )
                }
            )
        return Response({"response": response})


class AIDetailedExplanationView(APIView):
    """POST /api/ai/explanation/detailed/ — structured explanation for the mobile screen.

    Body: { question_id, question_text?, selected_answer?, correct_answer? }
    Returns: { explanation: {id, question_id, explanation, key_points, references,
                             related_topic, difficulty, created_at} }
    """

    permission_classes = [IsAuthenticated, IsPremiumOrReadOnly]

    def post(self, request):
        question_id = request.data.get("question_id")
        if not question_id:
            return Response({"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.prefetch_related("choices").get(
                id=question_id, is_published=True
            )
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        if question_in_published_board_exam(question):
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        result = detailed_explanation(
            question,
            selected_answer=(request.data.get("selected_answer") or ""),
        )
        return Response({"explanation": result})


class AIGenerateQuestionsView(APIView):
    """POST /api/ai/questions/generate/ — generate MCQ draft questions.

    Body: { topic: str, count?: int, difficulty?: str }
    Returns: { questions: [ {...}, ... ] }
    """

    permission_classes = [IsAuthenticated, IsPremiumOrReadOnly]

    def post(self, request):
        topic = (request.data.get("topic") or "").strip()
        if not topic:
            return Response({"error": "topic is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            count = max(1, min(10, int(request.data.get("count", 5))))
        except (TypeError, ValueError):
            count = 5
        difficulty = request.data.get("difficulty", "medium")
        questions = generate_questions(topic, count=count, difficulty=difficulty)
        return Response({"questions": questions})


class BoardPrepView(APIView):
    """POST /api/ai/board-prep/ — ML-generated nephrology board MCQs for practice.

    Body: { topic?: str, count?: int (1-10), difficulty?: easy|medium|hard }
    Returns: { topic, difficulty, questions: [...], generated: bool }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic = (request.data.get("topic") or "").strip()
        if not topic:
            topic = random.choice(BOARD_PREP_TOPICS)
        try:
            count = max(1, min(6, int(request.data.get("count", 3))))
        except (TypeError, ValueError):
            count = 3
        difficulty = request.data.get("difficulty", "medium")
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"
        questions = generate_board_prep_questions(topic, count=count, difficulty=difficulty)
        return Response(
            {
                "topic": topic,
                "difficulty": difficulty,
                "questions": questions,
                "generated": bool(questions),
            }
        )


class BoardPrepPlanView(APIView):
    """GET/POST /api/board-prep/plan/ — 25-day calendar + exam date / workdays."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.services.board_prep_service import build_plan_payload

        return Response(build_plan_payload(request.user))

    def post(self, request):
        from api.services.board_prep_service import build_plan_payload, save_settings

        serializer = BoardPrepSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_settings(
            request.user,
            exam_date=serializer.validated_data.get("exam_date"),
            work_weekdays=serializer.validated_data.get("work_weekdays"),
        )
        return Response(build_plan_payload(request.user))


class BoardPrepTodayView(APIView):
    """GET /api/board-prep/today/ — today's session from the 25-day plan."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.services.board_prep_service import build_plan_payload

        payload = build_plan_payload(request.user)
        return Response(
            {
                "today": payload["today"],
                "day_number": payload["day_number"],
                "days_until_exam": payload["days_until_exam"],
                "is_workday": payload["is_workday"],
                "today_answered": payload["today_answered"],
                "session": payload["today_session"],
                "classification": payload["classification"],
                "method": payload["method"],
            }
        )


class BoardPrepReviewQueueView(APIView):
    """GET /api/board-prep/review-queue/?tag=wrong|guessed|know|review"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.services.board_prep_service import review_queryset, serialize_review_item

        tag = (request.query_params.get("tag") or "review").strip().lower()
        if tag not in ("wrong", "guessed", "know", "review"):
            tag = "review"
        qs = review_queryset(request.user, tag=tag)[:200]
        items = [serialize_review_item(answer) for answer in qs]
        return Response({"tag": tag, "count": len(items), "items": items})


class BoardPrepLast48View(APIView):
    """GET/POST /api/board-prep/last-48h/ — rapid-review sheet."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.services.board_prep_service import last48_payload

        return Response(last48_payload(request.user))

    def post(self, request):
        from api.services.board_prep_service import last48_payload

        serializer = Last48HourFactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = None
        qid = serializer.validated_data.get("source_question_id")
        if qid:
            question = Question.objects.filter(id=qid).first()
        Last48HourFact.objects.create(
            user=request.user,
            kind=serializer.validated_data["kind"],
            text=serializer.validated_data["text"].strip(),
            source_question=question,
        )
        return Response(last48_payload(request.user), status=status.HTTP_201_CREATED)


class BoardPrepLast48DetailView(APIView):
    """DELETE /api/board-prep/last-48h/<id>/"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, fact_id):
        from api.services.board_prep_service import last48_payload

        deleted, _ = Last48HourFact.objects.filter(user=request.user, id=fact_id).delete()
        if not deleted:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(last48_payload(request.user))


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage user subscriptions."""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        sub = Subscription.objects.filter(user=request.user).first()
        if not sub:
            return Response([])
        return Response([self.get_serializer(sub).data])


class DailyChallengeView(APIView):
    """GET endpoint returning today's challenge questions."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        qs = _published_questions_for_user(request.user)
        seed = today.toordinal()
        qs_list = list(qs)
        if not qs_list:
            return Response({"detail": "No questions available"}, status=status.HTTP_404_NOT_FOUND)
        random.Random(seed).shuffle(qs_list)
        questions = qs_list[:DAILY_CHALLENGE_SIZE]
        completed, score = _daily_attempt_completed(request.user, today)
        mapped = [_map_question_quiz_safe(q) for q in questions]
        payload = {
            "id": f"daily-{today.isoformat()}",
            "date": today.isoformat(),
            "questions": mapped,
            "completed": completed,
        }
        if completed and score is not None:
            payload["score"] = score
        return Response(payload)


class WeaknessView(APIView):
    """GET endpoint returning chapters the user should reread."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        answers = Answer.objects.filter(
            quiz_attempt__user=request.user,
            question__chapter__isnull=False,
        ).select_related("question__chapter")
        stats = (
            answers.values(
                "question__chapter__id",
                "question__chapter__title",
                "question__chapter__slug",
            )
            .annotate(
                total_count=Count("id"),
                incorrect_count=Count("id", filter=Q(is_correct=False)),
            )
        )
        result = []
        for item in stats:
            total = item["total_count"]
            incorrect = item["incorrect_count"]
            if total == 0:
                continue
            accuracy = round((total - incorrect) / total * 100, 1)
            if incorrect == 0 and accuracy >= 80:
                continue
            slug = item["question__chapter__slug"]
            chapter_id = str(item["question__chapter__id"])
            title = item["question__chapter__title"]
            result.append(
                {
                    "name": title,
                    "chapter": title,
                    "chapterId": chapter_id,
                    "chapterSlug": slug,
                    "category": title,
                    "categoryId": chapter_id,
                    "subcategory": title,
                    "total_count": total,
                    "incorrect_count": incorrect,
                    "accuracy": accuracy,
                    "recommend": (
                        f"Read {title} in the Nephrology Book, then redo that chapter quiz."
                    ),
                    "read_path": f"/chapters/{slug}",
                    "book_path": f"/notes?chapter={slug}",
                    "practice_path": f"/quiz/chapter/{chapter_id}",
                }
            )
        result.sort(
            key=lambda r: (
                r["incorrect_count"] / r["total_count"] if r["total_count"] else 0,
                r["incorrect_count"],
            ),
            reverse=True,
        )
        return Response(result[:10])


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve board-review chapters with topics."""

    queryset = Chapter.objects.exclude(slug__in=LEGACY_CHAPTER_SLUGS.keys()).prefetch_related(
        "topics", "topics__lessons"
    )
    serializer_class = ChapterSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_object(self):
        slug = canonical_slug(self.kwargs.get(self.lookup_field))
        if slug:
            self.kwargs[self.lookup_field] = slug
        return super().get_object()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ChapterDetailSerializer
        return ChapterSerializer

    @action(detail=True, methods=["get"], url_path="topics")
    def chapter_topics(self, request, slug=None):
        chapter = self.get_object()
        topics = chapter.topics.prefetch_related("lessons")
        serializer = TopicDetailSerializer(topics, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="knowledge")
    def knowledge(self, request, slug=None):
        """Chapter-wise exam knowledge: lessons, high-yield list, and pearls."""
        chapter = self.get_object()
        lessons = (
            Lesson.objects.filter(topic__chapter=chapter)
            .select_related("topic")
            .order_by("topic__order_index", "order_index")
        )
        pearls, pearl_count = _grouped_board_pearls(request.user, chapter.slug, include_notes=False)
        pearl_items = pearls[0]["pearls"] if pearls else []
        return Response({
            "chapter": {
                "id": str(chapter.id),
                "title": chapter.title,
                "slug": chapter.slug,
                "description": chapter.description,
                "order_index": chapter.order_index,
            },
            "high_yield": _high_yield_for_chapter(chapter.slug),
            "pearls": pearl_items,
            "pearl_count": pearl_count,
            "lessons": [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "topic": lesson.topic.title,
                    "topic_slug": lesson.topic.slug,
                    "lesson_type": lesson.lesson_type,
                    "summary": lesson.summary,
                    "content_md": (lesson.content_md or lesson.summary or "").strip(),
                    "animation_url": lesson.animation_url,
                    "thumbnail_url": lesson.thumbnail_url,
                    "interactive_url": lesson.interactive_url,
                    "duration_seconds": lesson.duration_seconds,
                }
                for lesson in lessons
            ],
            "lesson_count": lessons.count(),
            "question_count": chapter.questions.filter(is_published=True).count(),
            "topic_count": chapter.topics.count(),
        })


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """Retrieve topics and their lessons."""

    queryset = Topic.objects.prefetch_related("lessons")
    serializer_class = TopicDetailSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        topic = self.get_object()
        serializer = LessonSerializer(topic.lessons.all(), many=True)
        return Response(serializer.data)


class QuizDailyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        qs = exclude_board_exam_questions(
            Question.objects.filter(is_published=True)
        ).prefetch_related("choices")
        qs_list = list(qs)
        if not qs_list:
            return Response({"detail": "No questions available"}, status=status.HTTP_404_NOT_FOUND)
        random.Random(today.toordinal()).shuffle(qs_list)
        question = qs_list[0]
        return Response(QuestionDetailSerializer(question).data)


class QuizChapterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id):
        limit = _parse_limit(request.query_params.get("limit"), default=10)
        qs = (
            _published_questions_for_user(request.user)
            .filter(chapter_id=chapter_id)
            .order_by("?")[:limit]
        )
        if not qs.exists():
            return Response({"detail": "No questions in this chapter"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "chapterId": chapter_id,
            "questions": [_map_question_quiz_safe(q) for q in qs],
        })


class QuizQuestionsView(APIView):
    """Frontend-compatible quiz loader: daily, practice, or category/chapter."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = _parse_limit(request.query_params.get("limit"), default=10)
        daily = request.query_params.get("daily") == "true"
        category_id = request.query_params.get("categoryId")
        chapter_id = request.query_params.get("chapterId")
        chapter_slug = request.query_params.get("chapterSlug")
        topic_id = request.query_params.get("topicId")
        board_day = request.query_params.get("board_day") or request.query_params.get("boardDay")
        qs = _published_questions_for_user(request.user)

        if board_day:
            from api.data.board_prep_plan import day_spec
            from api.services.board_prep_service import questions_for_day

            try:
                day_number = int(board_day)
            except (TypeError, ValueError):
                day_number = 1
            questions = questions_for_day(request.user, day_spec(day_number), limit)
        elif daily:
            today = date.today()
            qs_list = list(qs)
            random.Random(today.toordinal()).shuffle(qs_list)
            questions = qs_list[: min(limit, len(qs_list))]
        elif topic_id:
            questions = list(qs.filter(topic_id=topic_id).order_by("?")[:limit])
        elif chapter_id:
            questions = list(qs.filter(chapter_id=chapter_id).order_by("?")[:limit])
        elif chapter_slug:
            questions = list(qs.filter(_chapter_q(chapter_slug)).order_by("?")[:limit])
        elif category_id:
            questions = list(qs.filter(category_id=category_id).order_by("?")[:limit])
        else:
            questions = list(qs.order_by("?")[:limit])

        if not questions:
            return Response({"detail": "No questions found"}, status=status.HTTP_404_NOT_FOUND)

        mapped = [_map_question_quiz_safe(q) for q in questions]
        return Response({"questions": mapped, "sessionId": None})


class QuizAnswerView(APIView):
    """Check a single answer and return explanation."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        mcq_id = request.data.get("mcq_id") or request.data.get("question_id")
        choice_key = request.data.get("selected_choice_key") or request.data.get("choice_key")
        choice_id = request.data.get("chosen_choice_id")

        if not mcq_id:
            return Response({"error": "mcq_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.prefetch_related("choices").select_related("chapter").get(
                id=mcq_id, is_published=True
            )
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        if question_in_published_board_exam(question):
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        if question.is_premium and not _user_is_premium(request.user):
            return Response(
                {"error": "Premium subscription required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if choice_id:
            chosen = question.choices.filter(id=choice_id).first()
        elif choice_key:
            chosen = question.choices.filter(choice_key=choice_key).first()
        else:
            return Response({"error": "choice_key or chosen_choice_id required"}, status=status.HTTP_400_BAD_REQUEST)

        if not chosen:
            return Response({"error": "Invalid choice"}, status=status.HTTP_400_BAD_REQUEST)

        is_correct = chosen.is_correct
        correct = question.choices.filter(is_correct=True).first()

        return Response({
            "question_id": str(question.id),
            "is_correct": is_correct,
            "correct_choice_key": correct.choice_key if correct else "",
            "correct_choice_id": str(correct.id) if correct else "",
            "correct_answer_text": correct.choice_text if correct else "",
            "explanation": question.explanation,
            "clinical_pearl": question.clinical_pearl,
            "references": _references_for_question(question),
            "why_wrong": chosen.why_wrong if not is_correct else "",
            "chapter_slug": question.chapter.slug if question.chapter_id else None,
            "chapter_title": question.chapter.title if question.chapter_id else None,
            "chapter_id": str(question.chapter_id) if question.chapter_id else None,
        })


class QuizExplanationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, mcq_id):
        try:
            question = Question.objects.prefetch_related("choices").get(
                id=mcq_id, is_published=True
            )
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        if question_in_published_board_exam(question):
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        if question.is_premium and not _user_is_premium(request.user):
            return Response(
                {"error": "Premium subscription required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(QuestionExplanationSerializer(question).data)


class UserProgressView(APIView):
    """GET /api/users/me/progress — stats for dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        attempts = QuizAttempt.objects.filter(user=user)
        answers = Answer.objects.filter(quiz_attempt__user=user)
        total_questions = answers.count()
        correct_answers = answers.filter(is_correct=True).count()
        accuracy = round((correct_answers / total_questions) * 100, 1) if total_questions else 0

        today = date.today()
        daily_completed, _ = _daily_attempt_completed(user, today)

        category_stats = (
            answers.filter(question__category__isnull=False)
            .values("question__category__id", "question__category__name")
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
        )
        category_breakdown = [
            {
                "categoryId": str(item["question__category__id"]),
                "categoryName": item["question__category__name"],
                "totalQuestions": item["total"],
                "correctAnswers": item["correct"],
                "accuracy": round((item["correct"] / item["total"]) * 100, 1) if item["total"] else 0,
            }
            for item in category_stats
        ]

        chapter_stats = (
            answers.filter(question__chapter__isnull=False)
            .values(
                "question__chapter__id",
                "question__chapter__title",
                "question__chapter__slug",
            )
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
        )
        chapter_breakdown = [
            {
                "categoryId": str(item["question__chapter__id"]),
                "categoryName": item["question__chapter__title"],
                "chapterId": str(item["question__chapter__id"]),
                "chapterSlug": item["question__chapter__slug"],
                "totalQuestions": item["total"],
                "correctAnswers": item["correct"],
                "accuracy": round((item["correct"] / item["total"]) * 100, 1) if item["total"] else 0,
            }
            for item in chapter_stats
        ]
        chapter_breakdown.sort(key=lambda c: c["accuracy"])

        recent_dates = (
            attempts.values("completed_at__date")
            .distinct()
            .order_by("-completed_at__date")[:7]
        )
        recent_activity = []
        for row in recent_dates:
            day = row["completed_at__date"]
            day_attempts = attempts.filter(completed_at__date=day)
            day_answers = answers.filter(quiz_attempt__completed_at__date=day)
            recent_activity.append({
                "date": str(day),
                "quizzesCompleted": day_attempts.count(),
                "questionsAnswered": day_answers.count(),
                "correctAnswers": day_answers.filter(is_correct=True).count(),
            })

        from api.services.board_prep_service import build_plan_payload

        plan = build_plan_payload(user)
        return Response({
            "totalQuizzes": attempts.count(),
            "totalQuestions": total_questions,
            "correctAnswers": correct_answers,
            "accuracy": accuracy,
            "currentStreak": user.streak_count,
            "longestStreak": user.longest_streak,
            "categoryBreakdown": chapter_breakdown or category_breakdown,
            "chapterBreakdown": chapter_breakdown,
            "dailyQuizCompleted": daily_completed,
            "recentActivity": recent_activity,
            "boardPrep": {
                "dayNumber": plan["day_number"],
                "daysUntilExam": plan["days_until_exam"],
                "questionsInPlan": plan["questions_in_plan"],
                "todayAnswered": plan["today_answered"],
                "targetMin": plan["target_min"],
                "targetMax": plan["target_max"],
                "classification": plan["classification"],
                "todayFocus": plan["today_session"]["focus"],
            },
        })


class StatsView(UserProgressView):
    """Alias for frontend /stats endpoint."""
    pass


class BoardPearlsView(APIView):
    """GET /api/pearls/ — curated + MCQ board pearls grouped by chapter.

    Short My Book notes are excluded unless include_notes=1.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        include_notes = str(request.query_params.get("include_notes", "")).lower() in (
            "1",
            "true",
            "yes",
        )
        result, total = _grouped_board_pearls(
            request.user,
            request.query_params.get("chapter"),
            include_notes=include_notes,
        )
        return Response({"chapters": result, "total": total})


class MedicalReferencesView(APIView):
    """GET /api/references/ — curated literature citations."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.data.medical_references import list_all_references, resolve_references

        ids_param = request.query_params.get("ids", "").strip()
        if ids_param:
            ref_ids = [i.strip() for i in ids_param.split(",") if i.strip()]
            return Response({"references": resolve_references(ref_ids)})
        return Response({"references": list_all_references()})


class AdminContentVerifyView(APIView):
    """POST /api/admin/content/verify/ — LLM verification for pearls/MCQs."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def post(self, request):
        from api.services.content_verification_service import verify_mcq, verify_pearl

        payload = request.data if isinstance(request.data, dict) else {}
        kind = payload.get("type", "pearl")
        use_llm = bool(payload.get("use_llm", True))

        if kind == "pearl":
            pearl = payload.get("pearl") if isinstance(payload.get("pearl"), dict) else payload
            result = verify_pearl(pearl, use_llm=use_llm)
        elif kind == "mcq":
            result = verify_mcq(
                question_text=payload.get("question_text", ""),
                explanation=payload.get("explanation", ""),
                clinical_pearl=payload.get("clinical_pearl", ""),
                reference_ids=payload.get("reference_ids") or [],
                use_llm=use_llm,
            )
        else:
            return Response(
                {"error": "type must be 'pearl' or 'mcq'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(result)


class AdminAILearningView(APIView):
    """GET/PATCH /api/admin/ai-learning/ — review lessons that improve Ollama prompts over time."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def get(self, request):
        from api.models import AIKnowledgeEntry
        from api.services.ai_learning_service import learning_stats

        status_filter = request.query_params.get("status", "pending")
        qs = AIKnowledgeEntry.objects.all()
        if status_filter != "all":
            qs = qs.filter(status=status_filter)
        entries = qs.order_by("-created_at")[:100]
        return Response({
            "stats": learning_stats(),
            "entries": [
                {
                    "id": e.id,
                    "topic": e.topic,
                    "content_type": e.content_type,
                    "lesson_rule": e.lesson_rule,
                    "original_text": e.original_text[:300],
                    "corrected_text": e.corrected_text[:300],
                    "reference": e.reference,
                    "source": e.source,
                    "status": e.status,
                    "confidence": e.confidence,
                    "use_count": e.use_count,
                    "created_at": e.created_at.isoformat(),
                }
                for e in entries
            ],
        })

    def patch(self, request):
        from api.services.ai_learning_service import approve_entry, reject_entry

        entry_id = request.data.get("id")
        action = request.data.get("action")
        if not entry_id or action not in ("approve", "reject"):
            return Response(
                {"error": "Provide id and action: approve|reject"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action == "approve":
            ok = approve_entry(int(entry_id), user=request.user)
        else:
            ok = reject_entry(int(entry_id))
        if not ok:
            return Response({"error": "Entry not found or already processed"}, status=404)
        return Response({"ok": True, "id": entry_id, "action": action})


class StudyNotesOrganizeView(APIView):
    """POST /api/notes/organize/ — paste notes and sort into chapters."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudyNotesOrganizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_text = serializer.validated_data["text"]
        use_llm = serializer.validated_data.get("use_llm", False)
        result = organize_pasted_notes(raw_text)
        chapters = {c.slug: c for c in Chapter.objects.all()}
        created = []
        skipped_duplicates = 0
        with transaction.atomic():
            existing = {
                normalize_note_content(n.content)
                for n in StudyNote.objects.filter(user=request.user).order_by("pk").only("content")
            }
            for i, note in enumerate(result["notes"]):
                norm = normalize_note_content(note["content"])
                if norm in existing:
                    skipped_duplicates += 1
                    continue
                existing.add(norm)
                chapter = chapters.get(note["chapter_slug"]) if note.get("chapter_slug") else None
                chapter_slug = note.get("chapter_slug")
                enriched = enrich_note_payload(
                    topic=note.get("topic_title", ""),
                    content=note["content"],
                    chapter_slug=chapter_slug,
                )
                obj = StudyNote.objects.create(
                    user=request.user,
                    chapter=chapter,
                    topic_title=note.get("topic_title", ""),
                    content=enriched["content"],
                    reference=enriched["reference"],
                    source_batch_id=result["batch_id"],
                    order_index=i,
                )
                enrich_study_note(obj, use_llm=use_llm, apply_correction=use_llm)
                created.append(obj)
        return Response({
            "method": result["method"],
            "batch_id": result["batch_id"],
            "notes": StudyNoteSerializer(created, many=True).data,
            "total": len(created),
            "skipped_duplicates": skipped_duplicates,
        }, status=status.HTTP_201_CREATED)


class StudyNotesReviewView(APIView):
    """GET /api/notes/review/ — chapter-wise notes for pre-exam review."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = StudyNote.objects.filter(user=request.user).select_related("chapter")
        chapters_map: dict = {}
        uncategorized = []
        for note in notes:
            data = StudyNoteSerializer(note).data
            if note.chapter_id:
                key = note.chapter_id
                if key not in chapters_map:
                    chapters_map[key] = {
                        "chapter": {
                            "id": str(note.chapter.id),
                            "title": note.chapter.title,
                            "slug": note.chapter.slug,
                            "order_index": note.chapter.order_index,
                        },
                        "notes": [],
                    }
                chapters_map[key]["notes"].append(data)
            else:
                uncategorized.append(data)

        for chapter in Chapter.objects.exclude(slug__in=LEGACY_CHAPTER_SLUGS.keys()).order_by("order_index"):
            if chapter.id not in chapters_map:
                chapters_map[chapter.id] = {
                    "chapter": {
                        "id": str(chapter.id),
                        "title": chapter.title,
                        "slug": chapter.slug,
                        "order_index": chapter.order_index,
                    },
                    "notes": [],
                }
            lessons = (
                Lesson.objects.filter(topic__chapter=chapter)
                .select_related("topic")
                .order_by("topic__order_index", "order_index")
            )
            pearls, _pearl_count = _grouped_board_pearls(request.user, chapter.slug, include_notes=False)
            chapters_map[chapter.id]["book"] = {
                "high_yield": _high_yield_for_chapter(chapter.slug),
                "pearls": pearls[0]["pearls"] if pearls else [],
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "topic": lesson.topic.title,
                        "summary": lesson.summary,
                        "content_md": (lesson.content_md or lesson.summary or "").strip(),
                    }
                    for lesson in lessons
                ],
            }

        chapters = sorted(
            chapters_map.values(),
            key=lambda x: x["chapter"]["order_index"],
        )
        for group in chapters:
            group["count"] = len(group["notes"]) + len(group.get("book", {}).get("lessons") or [])

        return Response({
            "chapters": chapters,
            "uncategorized": uncategorized,
            "total": notes.count(),
            "curriculum_chapters": len(chapters),
        })


class StudyNotesDedupeView(APIView):
    """POST /api/notes/dedupe/ — remove duplicate study notes (keeps newest copy)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        notes = StudyNote.objects.filter(user=request.user).order_by("-created_at", "-id")
        seen: set[str] = set()
        delete_ids: list[int] = []
        for note in notes:
            norm = normalize_note_content(note.content)
            if norm in seen:
                delete_ids.append(note.id)
            else:
                seen.add(norm)
        removed = StudyNote.objects.filter(id__in=delete_ids, user=request.user).delete()[0]
        return Response({"removed": removed})


class StudyNotesEnrichView(APIView):
    """POST /api/notes/enrich/ — clean, add references, verify user book notes."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from api.services.notes_enrichment_service import enrich_study_notes_queryset

        serializer = StudyNotesEnrichSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_llm = serializer.validated_data.get("use_llm", False)
        apply_corrections = serializer.validated_data.get("apply_corrections", True)
        note_ids = serializer.validated_data.get("note_ids") or []
        chapter_slug = (serializer.validated_data.get("chapter_slug") or "").strip()

        qs = StudyNote.objects.filter(user=request.user)
        if note_ids:
            qs = qs.filter(id__in=note_ids)
        if chapter_slug:
            qs = qs.filter(chapter__slug=chapter_slug)

        if not qs.exists():
            return Response(
                {"message": "No notes matched", "enriched": 0, "notes": []},
                status=status.HTTP_200_OK,
            )

        payload = enrich_study_notes_queryset(
            qs,
            use_llm=use_llm,
            apply_correction=apply_corrections,
        )
        refreshed = StudyNote.objects.filter(
            id__in=[n["note_id"] for n in payload["notes"]],
            user=request.user,
        ).select_related("chapter")
        payload["notes"] = StudyNoteSerializer(refreshed, many=True).data
        return Response(payload, status=status.HTTP_200_OK)


class StudyNotesListView(APIView):
    """GET /api/notes/ — list all study notes for the user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = StudyNote.objects.filter(user=request.user).select_related("chapter")
        chapter_slug = request.query_params.get("chapter")
        if chapter_slug:
            qs = qs.filter(chapter__slug=chapter_slug)
        return Response(StudyNoteSerializer(qs, many=True).data)


class StudyNoteDetailView(APIView):
    """PATCH/DELETE /api/notes/<id>/ — update or remove a study note."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, note_id):
        try:
            note = StudyNote.objects.get(id=note_id, user=request.user)
        except StudyNote.DoesNotExist:
            return Response({"message": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudyNoteUpdateSerializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StudyNoteSerializer(note).data)

    def delete(self, request, note_id):
        deleted, _ = StudyNote.objects.filter(id=note_id, user=request.user).delete()
        if not deleted:
            return Response({"message": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthCheckView(APIView):
    """GET /api/health/ — used by GoDaddy/Nginx uptime checks."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "nephro-challenge-api"})


class AccountDeleteView(APIView):
    """DELETE user account and associated data (App Store / Play Store requirement)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LessonDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related("topic__chapter").get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)
        data = LessonSerializer(lesson).data
        data["topic"] = TopicSerializer(lesson.topic).data
        data["topic"]["chapter"] = {
            "id": lesson.topic.chapter_id,
            "title": lesson.topic.chapter.title,
            "slug": lesson.topic.chapter.slug,
        }
        return Response(data)


class AdminImportMCQView(APIView):
    """POST /api/admin/import-mcqs — bulk import from sample-mcq.json format."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def post(self, request):
        items = request.data if isinstance(request.data, list) else [request.data]
        created = []
        with transaction.atomic():
            for item in items:
                serializer = MCQImportSerializer(data=item)
                serializer.is_valid(raise_exception=True)
                question = _import_mcq_item(serializer.validated_data)
                created.append(question.id)
        return Response({"created": created, "count": len(created)}, status=status.HTTP_201_CREATED)


class AdminStatsView(APIView):
    """GET /api/admin/stats — dashboard metrics for admin UI."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def get(self, request):
        recent_users = User.objects.order_by("-created_at")[:5]
        return Response({
            "totalUsers": User.objects.count(),
            "totalQuestions": Question.objects.count(),
            "aiGeneratedPending": AIGeneratedQuestion.objects.filter(
                status=AIGeneratedQuestion.Status.PENDING
            ).count(),
            "totalQuizzes": QuizAttempt.objects.count(),
            "recentUsers": [
                {
                    "id": str(u.id),
                    "name": u.username,
                    "email": u.email,
                    "createdAt": u.created_at.isoformat(),
                }
                for u in recent_users
            ],
        })


class AdminQuestionsView(APIView):
    """GET/POST /api/admin/questions — list and create questions."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def get(self, request):
        page = _parse_limit(request.query_params.get("page"), default=1, maximum=10_000)
        limit = _parse_limit(request.query_params.get("limit"), default=20, maximum=100)
        search = request.query_params.get("search", "").strip()

        qs = Question.objects.select_related("category").prefetch_related("choices")
        if search:
            qs = qs.filter(
                Q(question_text__icontains=search) | Q(explanation__icontains=search)
            )
        total = qs.count()
        offset = (page - 1) * limit
        questions = qs[offset : offset + limit]
        return Response({
            "questions": [_map_question_for_frontend(q) for q in questions],
            "total": total,
            "totalPages": max(1, math.ceil(total / limit)),
            "page": page,
        })

    def post(self, request):
        try:
            question = _create_or_update_question_from_admin(request.data, user=request.user)
        except Category.DoesNotExist:
            return Response({"message": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_map_question_for_frontend(question), status=status.HTTP_201_CREATED)


class AdminQuestionDetailView(APIView):
    """PUT/DELETE /api/admin/questions/<id> — update or delete a question."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            question = _create_or_update_question_from_admin(
                request.data, question=question, user=request.user
            )
        except Category.DoesNotExist:
            return Response({"message": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_map_question_for_frontend(question))

    def delete(self, request, question_id):
        deleted, _ = Question.objects.filter(id=question_id).delete()
        if not deleted:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAIGeneratedQuestionsView(APIView):
    """GET /api/admin/questions/ai-generated — AI drafts for review."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def get(self, request):
        status_filter = request.query_params.get("status", "pending")
        qs = AIGeneratedQuestion.objects.all()
        if status_filter in ("pending", "approved", "rejected"):
            qs = qs.filter(status=status_filter)
        return Response([_map_ai_question_for_frontend(q) for q in qs])


class AdminQuestionReviewView(APIView):
    """PUT /api/admin/questions/<id>/review — approve or reject AI-generated draft."""

    permission_classes = [IsAuthenticated, IsAdminOrEditor]

    def put(self, request, question_id):
        try:
            ai_q = AIGeneratedQuestion.objects.get(id=question_id)
        except AIGeneratedQuestion.DoesNotExist:
            return Response({"message": "AI question not found"}, status=status.HTTP_404_NOT_FOUND)

        review_status = request.data.get("aiReviewStatus")
        if review_status not in ("approved", "rejected"):
            return Response(
                {"message": "aiReviewStatus must be approved or rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ai_q.status != AIGeneratedQuestion.Status.PENDING:
            return Response(
                {"message": f"Question already {ai_q.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_q.status = review_status
        ai_q.reviewed_by = request.user
        ai_q.save(update_fields=["status", "reviewed_by"])

        if review_status == "approved":
            category = Category.objects.first()
            if not category:
                return Response({"message": "No category available"}, status=status.HTTP_400_BAD_REQUEST)
            question = _create_question_from_ai_draft(ai_q, category, request.user)
            return Response({
                **_map_ai_question_for_frontend(ai_q),
                "publishedQuestionId": str(question.id),
            })

        return Response(_map_ai_question_for_frontend(ai_q))


def _references_for_question(question):
    from api.data.medical_references import references_for_topic, resolve_reference_field

    refs = resolve_reference_field(question.reference or "")
    if not refs:
        topic = question.topic.title if question.topic_id else (question.subcategory or "")
        slug = question.chapter.slug if question.chapter_id else None
        refs = references_for_topic(topic, slug)
    return refs


def _map_question_quiz_safe(question):
    """Quiz loader shape — no answers or explanations."""
    return {
        "id": str(question.id),
        "text": question.question_text,
        "caseText": question.case_text,
        "labs": question.labs,
        "choices": [
            {"id": str(c.id), "text": c.choice_text, "key": c.choice_key}
            for c in question.choices.all()
        ],
        "categoryId": str(question.category_id) if question.category_id else "",
        "chapterId": str(question.chapter_id) if question.chapter_id else "",
        "difficulty": question.difficulty,
        "isAIGenerated": False,
        "category": (
            {"id": str(question.category_id), "name": question.category.name}
            if question.category_id
            else None
        ),
        "createdBy": "",
        "createdAt": question.created_at.isoformat(),
        "updatedAt": question.updated_at.isoformat(),
    }


def _map_question_for_frontend(question):
    """Map backend Question to frontend Question shape."""
    correct = question.choices.filter(is_correct=True).first()
    return {
        "id": str(question.id),
        "text": question.question_text,
        "caseText": question.case_text,
        "labs": question.labs,
        "choices": [
            {"id": str(c.id), "text": c.choice_text, "key": c.choice_key}
            for c in question.choices.all()
        ],
        "correctAnswer": str(correct.id) if correct else "",
        "correctChoiceKey": correct.choice_key if correct else "",
        "explanation": question.explanation,
        "clinicalPearl": question.clinical_pearl,
        "references": _references_for_question(question),
        "categoryId": str(question.category_id) if question.category_id else "",
        "chapterId": str(question.chapter_id) if question.chapter_id else "",
        "difficulty": question.difficulty,
        "isAIGenerated": False,
        "category": (
            {"id": str(question.category_id), "name": question.category.name}
            if question.category_id
            else None
        ),
        "createdBy": "",
        "createdAt": question.created_at.isoformat(),
        "updatedAt": question.updated_at.isoformat(),
    }


def _map_ai_question_for_frontend(ai_q):
    """Map AIGeneratedQuestion to frontend Question shape."""
    keys = ["a", "b", "c", "d", "e", "f"]
    raw_choices = ai_q.choices if isinstance(ai_q.choices, list) else []
    choices = []
    correct_id = ""
    for i, item in enumerate(raw_choices):
        if isinstance(item, dict):
            text = str(item.get("text", ""))
            cid = str(item.get("id", keys[i] if i < len(keys) else str(i)))
        else:
            text = str(item)
            cid = keys[i] if i < len(keys) else str(i)
        choices.append({"id": cid, "text": text})
        if text == ai_q.correct_answer or cid == ai_q.correct_answer:
            correct_id = cid
    if not correct_id and choices:
        for c in choices:
            if c["text"] == ai_q.correct_answer:
                correct_id = c["id"]
                break
    return {
        "id": str(ai_q.id),
        "text": ai_q.question_text,
        "choices": choices,
        "correctAnswer": correct_id,
        "explanation": ai_q.explanation,
        "categoryId": "",
        "difficulty": "medium",
        "isAIGenerated": True,
        "aiReviewStatus": ai_q.status,
        "createdAt": ai_q.created_at.isoformat(),
        "updatedAt": ai_q.created_at.isoformat(),
    }


def _resolve_correct_choice_index(choices_data, correct_answer):
    if correct_answer is None or correct_answer == "":
        return None
    correct_str = str(correct_answer)
    for i, choice in enumerate(choices_data):
        if str(choice.get("id", "")) == correct_str:
            return i
    return None


def _create_or_update_question_from_admin(data, question=None, user=None):
    text = (data.get("text") or "").strip()
    explanation = (data.get("explanation") or "").strip()
    category_id = data.get("categoryId")
    difficulty = data.get("difficulty", "medium")
    choices_data = data.get("choices") or []
    correct_answer = data.get("correctAnswer")

    if not text:
        raise ValueError("Question text is required")
    if not explanation:
        raise ValueError("Explanation is required")
    if not category_id:
        raise ValueError("Category is required")
    if len(choices_data) < 2:
        raise ValueError("At least two choices are required")
    if any(not (c.get("text") or "").strip() for c in choices_data):
        raise ValueError("All choices must have text")

    correct_index = _resolve_correct_choice_index(choices_data, correct_answer)
    if correct_index is None:
        raise ValueError("Correct answer must match one of the choices")

    category = Category.objects.get(id=category_id)
    if question is None:
        question = Question.objects.create(
            category=category,
            question_text=text,
            explanation=explanation,
            difficulty=difficulty,
            is_published=True,
            created_by=user,
        )
    else:
        question.category = category
        question.question_text = text
        question.explanation = explanation
        question.difficulty = difficulty
        question.is_published = True
        question.save()

    question.choices.all().delete()
    choice_keys = ["a", "b", "c", "d", "e", "f"]
    for i, choice in enumerate(choices_data):
        key = str(choice.get("id", choice_keys[i] if i < len(choice_keys) else str(i)))
        if len(key) > 2:
            key = choice_keys[i] if i < len(choice_keys) else str(i)
        Choice.objects.create(
            question=question,
            choice_key=key,
            choice_text=choice.get("text", "").strip(),
            is_correct=(i == correct_index),
            order=i + 1,
        )
    return question


def _create_question_from_ai_draft(ai_q, category, user):
    keys = ["a", "b", "c", "d", "e", "f"]
    raw_choices = ai_q.choices if isinstance(ai_q.choices, list) else []
    question = Question.objects.create(
        category=category,
        question_text=ai_q.question_text,
        explanation=ai_q.explanation,
        difficulty="medium",
        is_published=True,
        created_by=user,
    )
    for i, item in enumerate(raw_choices):
        text = item.get("text", item) if isinstance(item, dict) else str(item)
        key = keys[i] if i < len(keys) else str(i)
        Choice.objects.create(
            question=question,
            choice_key=key,
            choice_text=str(text),
            is_correct=(str(text) == ai_q.correct_answer or key == ai_q.correct_answer),
            order=i + 1,
        )
    return question


def _import_mcq_item(data):
    from django.utils.text import slugify

    chapter, _ = Chapter.objects.get_or_create(
        title=data["chapter"],
        defaults={"slug": slugify(data["chapter"]), "order_index": 0},
    )
    topic, _ = Topic.objects.get_or_create(
        chapter=chapter,
        slug=slugify(data["topic"]),
        defaults={"title": data["topic"], "order_index": 0},
    )
    lesson = None
    if data.get("lesson"):
        lesson_data = data["lesson"]
        lesson, _ = Lesson.objects.get_or_create(
            topic=topic,
            title=lesson_data["title"],
            defaults={
                "lesson_type": lesson_data.get("lesson_type", "animation"),
                "summary": lesson_data.get("summary", ""),
                "animation_url": lesson_data.get("animation_url", ""),
                "order_index": 0,
            },
        )

    mcq = data["mcq"]
    category = chapter.category or Category.objects.first()
    question = Question.objects.create(
        category=category,
        chapter=chapter,
        topic=topic,
        lesson=lesson,
        difficulty=mcq.get("difficulty", "medium"),
        case_text=mcq.get("clinical_case", ""),
        labs=mcq.get("labs", {}),
        question_text=mcq["question_stem"],
        explanation=mcq["explanation"],
        clinical_pearl=mcq.get("clinical_pearl", ""),
        is_published=True,
    )
    for key, text in mcq.get("choices", {}).items():
        key_upper = str(key).upper()
        Choice.objects.create(
            question=question,
            choice_key=key_upper,
            choice_text=text,
            is_correct=(key_upper == str(mcq["correct_choice_key"]).upper()),
            order=ord(key_upper) - ord("A") + 1,
        )
    return question
