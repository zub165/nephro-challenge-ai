from django.contrib.auth import get_user_model, authenticate
from django.db import models, transaction
from rest_framework import serializers

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
    StudyNote,
    Subscription,
    Topic,
)

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username") or data.get("email")
        if not username:
            raise serializers.ValidationError("Username or email is required")
        user = authenticate(username=username, password=data["password"])
        if user is None:
            raise serializers.ValidationError({"message": "Invalid credentials"})
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "name",
            "display_name",
            "password",
            "role",
            "specialty",
            "bio",
            "avatar",
            "streak_count",
            "longest_streak",
            "xp_points",
            "rank_score",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "role",
            "streak_count",
            "longest_streak",
            "last_streak_date",
            "xp_points",
            "rank_score",
            "created_at",
        ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = [
            "id",
            "role",
            "streak_count",
            "longest_streak",
            "xp_points",
            "rank_score",
            "created_at",
            "username",
        ]


class CategorySerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "order", "question_count"]

    def get_question_count(self, obj) -> int:
        if hasattr(obj, "question_count"):
            return obj.question_count
        return obj.questions.filter(is_published=True).count()


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_key", "choice_text", "why_wrong", "is_correct", "order"]
        extra_kwargs = {
            "is_correct": {"write_only": True},
            "why_wrong": {"write_only": True},
        }


class ChoicePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_key", "choice_text", "order"]


class ChoiceExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_key", "choice_text", "why_wrong", "order"]


class QuestionListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    topic_title = serializers.CharField(source="topic.title", read_only=True)
    choice_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "category_name",
            "chapter",
            "chapter_title",
            "topic",
            "topic_title",
            "subcategory",
            "difficulty",
            "question_text",
            "image_url",
            "times_answered",
            "times_correct",
            "choice_count",
            "created_at",
        ]

    def get_choice_count(self, obj) -> int:
        return obj.choices.count()


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoicePublicSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    topic_title = serializers.CharField(source="topic.title", read_only=True)
    correct_choice_key = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "category_name",
            "chapter",
            "chapter_title",
            "topic",
            "topic_title",
            "subcategory",
            "difficulty",
            "case_text",
            "labs",
            "question_text",
            "explanation",
            "clinical_pearl",
            "reference",
            "image_url",
            "choices",
            "correct_choice_key",
            "times_answered",
            "times_correct",
            "created_at",
        ]

    def get_correct_choice_key(self, obj) -> str:
        correct = obj.choices.filter(is_correct=True).first()
        return correct.choice_key if correct else ""


class QuestionExplanationSerializer(serializers.ModelSerializer):
    choices = ChoiceExplanationSerializer(many=True, read_only=True)
    correct_choice_key = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "case_text",
            "labs",
            "explanation",
            "clinical_pearl",
            "reference",
            "references",
            "choices",
            "correct_choice_key",
        ]

    def get_correct_choice_key(self, obj) -> str:
        correct = obj.choices.filter(is_correct=True).first()
        return correct.choice_key if correct else ""

    def get_references(self, obj) -> list:
        from api.data.medical_references import references_for_topic, resolve_reference_field

        refs = resolve_reference_field(obj.reference or "")
        if not refs:
            topic = obj.topic.title if obj.topic_id else (obj.subcategory or "")
            slug = obj.chapter.slug if obj.chapter_id else None
            refs = references_for_topic(topic, slug)
        return refs


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.question_text", read_only=True)
    chosen_text = serializers.CharField(source="chosen_choice.choice_text", read_only=True)
    correct_answer_text = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "id",
            "question",
            "question_text",
            "chosen_choice",
            "chosen_text",
            "correct_answer_text",
            "is_correct",
            "time_taken",
        ]

    def get_correct_answer_text(self, obj) -> str:
        correct = obj.question.choices.filter(is_correct=True).first()
        return correct.choice_text if correct else ""


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "user",
            "mode",
            "category",
            "category_name",
            "chapter",
            "topic",
            "score",
            "total_questions",
            "percentage",
            "time_taken",
            "completed_at",
            "answers",
        ]
        read_only_fields = ["id", "user", "completed_at"]

    def get_percentage(self, obj) -> float:
        if obj.total_questions == 0:
            return 0.0
        return round((obj.score / obj.total_questions) * 100, 1)


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers_data = serializers.ListField(write_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "mode",
            "category",
            "chapter",
            "topic",
            "total_questions",
            "time_taken",
            "answers_data",
        ]

    def validate_answers_data(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required")
        return value

    def create(self, validated_data):
        answers_data = validated_data.pop("answers_data")
        user = self.context["request"].user

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(user=user, **validated_data)
            score = 0
            for item in answers_data:
                try:
                    question = Question.objects.get(
                        id=item["question_id"], is_published=True
                    )
                except Question.DoesNotExist:
                    raise serializers.ValidationError(
                        {"answers_data": f"Question {item.get('question_id')} not found"}
                    )

                chosen_id = item.get("chosen_choice_id")
                chosen_key = item.get("chosen_choice_key")
                try:
                    if chosen_id:
                        chosen = Choice.objects.get(id=chosen_id, question=question)
                    elif chosen_key:
                        chosen = Choice.objects.get(
                            question=question, choice_key=chosen_key
                        )
                    else:
                        raise serializers.ValidationError(
                            {"answers_data": "Each answer needs chosen_choice_id or chosen_choice_key"}
                        )
                except Choice.DoesNotExist:
                    raise serializers.ValidationError(
                        {"answers_data": "Invalid choice for question"}
                    )

                is_correct = chosen.is_correct
                if is_correct:
                    score += 1
                Answer.objects.create(
                    quiz_attempt=attempt,
                    question=question,
                    chosen_choice=chosen,
                    is_correct=is_correct,
                    time_taken=item.get("time_taken", 0),
                )
                Question.objects.filter(id=question.id).update(
                    times_answered=models.F("times_answered") + 1,
                    times_correct=models.F("times_correct") + (1 if is_correct else 0),
                )
            attempt.score = score
            attempt.save(update_fields=["score"])

        from api.services.leaderboard_service import refresh_user_stats

        refresh_user_stats(user)
        return attempt


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    specialty = serializers.CharField(source="user.specialty", read_only=True)

    class Meta:
        model = Leaderboard
        fields = [
            "id",
            "user",
            "username",
            "avatar",
            "specialty",
            "score",
            "category",
            "period",
            "date",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Subscription
        fields = ["id", "plan", "start_date", "end_date", "is_active"]
        read_only_fields = ["id", "start_date"]

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        if not validated_data.get("end_date"):
            plan = validated_data.get("plan", Subscription.Plan.MONTHLY)
            days = 365 if plan == Subscription.Plan.ANNUAL else 30
            validated_data["end_date"] = timezone.now() + timedelta(days=days)
        return super().create(validated_data)


class AIGeneratedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneratedQuestion
        fields = [
            "id",
            "question_text",
            "choices",
            "correct_answer",
            "explanation",
            "status",
            "reviewed_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_by", "status"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "lesson_type",
            "summary",
            "content_md",
            "animation_url",
            "thumbnail_url",
            "duration_seconds",
            "order_index",
            "is_premium",
        ]


class TopicSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id",
            "chapter",
            "title",
            "slug",
            "order_index",
            "description",
            "lesson_count",
            "question_count",
        ]

    def get_lesson_count(self, obj) -> int:
        return obj.lessons.count()

    def get_question_count(self, obj) -> int:
        return obj.questions.filter(is_published=True).count()


class TopicDetailSerializer(TopicSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + ["lessons"]


class ChapterSerializer(serializers.ModelSerializer):
    topic_count = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            "id",
            "title",
            "slug",
            "order_index",
            "description",
            "icon",
            "category",
            "topic_count",
            "question_count",
            "lesson_count",
        ]

    def get_topic_count(self, obj) -> int:
        return obj.topics.count()

    def get_question_count(self, obj) -> int:
        return obj.questions.filter(is_published=True).count()

    def get_lesson_count(self, obj) -> int:
        return Lesson.objects.filter(topic__chapter=obj).count()


class ChapterDetailSerializer(ChapterSerializer):
    topics = TopicDetailSerializer(many=True, read_only=True)

    class Meta(ChapterSerializer.Meta):
        fields = ChapterSerializer.Meta.fields + ["topics"]


class MCQImportSerializer(serializers.Serializer):
    """Validates sample-mcq.json import format."""

    chapter = serializers.CharField()
    topic = serializers.CharField()
    lesson = serializers.DictField(required=False)
    mcq = serializers.DictField()


class StudyNoteSerializer(serializers.ModelSerializer):
    chapter_slug = serializers.CharField(source="chapter.slug", read_only=True, allow_null=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True, allow_null=True)
    references = serializers.SerializerMethodField()

    class Meta:
        model = StudyNote
        fields = [
            "id",
            "chapter",
            "chapter_slug",
            "chapter_title",
            "topic_title",
            "content",
            "reference",
            "references",
            "verified",
            "verification_confidence",
            "verification_issues",
            "source_batch_id",
            "order_index",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "source_batch_id"]

    def get_references(self, obj) -> list:
        from api.services.notes_enrichment_service import references_for_study_note

        return references_for_study_note(obj)


class StudyNotesOrganizeSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=False, trim_whitespace=True)
    use_llm = serializers.BooleanField(required=False, default=False)


class StudyNotesEnrichSerializer(serializers.Serializer):
    use_llm = serializers.BooleanField(required=False, default=False)
    apply_corrections = serializers.BooleanField(required=False, default=True)
    note_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
    chapter_slug = serializers.CharField(required=False, allow_blank=True)


class StudyNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyNote
        fields = ["chapter", "topic_title", "content", "order_index"]


