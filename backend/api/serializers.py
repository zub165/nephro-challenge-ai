from django.contrib.auth import get_user_model, authenticate
from django.db import models
from rest_framework import serializers

from api.models import (
    AIGeneratedQuestion,
    Answer,
    Category,
    Choice,
    Leaderboard,
    Question,
    QuizAttempt,
)

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "specialty",
            "bio",
            "avatar",
            "streak_count",
            "xp_points",
            "rank_score",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "role",
            "streak_count",
            "xp_points",
            "rank_score",
            "created_at",
        ]

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
        return obj.questions.filter(is_published=True).count()


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_text", "is_correct", "order"]
        extra_kwargs = {
            "is_correct": {"write_only": True},
        }


class QuestionListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    choice_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "category_name",
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
    choices = ChoiceSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "category_name",
            "subcategory",
            "difficulty",
            "case_text",
            "labs",
            "question_text",
            "explanation",
            "clinical_pearl",
            "image_url",
            "choices",
            "times_answered",
            "times_correct",
            "created_at",
        ]


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
            "category",
            "category_name",
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
            "category",
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
        attempt = QuizAttempt.objects.create(user=user, **validated_data)
        score = 0
        for item in answers_data:
            question = Question.objects.get(id=item["question_id"])
            chosen = Choice.objects.get(id=item["chosen_choice_id"])
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
        attempt.save()
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



