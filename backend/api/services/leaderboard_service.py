"""Leaderboard rankings from quiz attempts."""

from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from api.models import Answer, QuizAttempt, User


def _attempts_for_period(period: str):
    qs = QuizAttempt.objects.select_related("user")
    today = timezone.localdate()
    if period == "daily":
        return qs.filter(completed_at__date=today)
    if period == "weekly":
        return qs.filter(completed_at__date__gte=today - timedelta(days=7))
    if period == "monthly":
        return qs.filter(completed_at__date__gte=today.replace(day=1))
    return qs


def build_leaderboard(period: str = "all_time", limit: int = 100) -> list[dict]:
    attempts_qs = _attempts_for_period(period)
    aggregates = (
        attempts_qs.values("user_id", "user__username")
        .annotate(
            score=Sum("score"),
            quiz_count=Count("id"),
        )
        .order_by("-score", "-quiz_count")
    )

    user_ids = [row["user_id"] for row in aggregates[:limit]]
    streak_map = dict(
        User.objects.filter(id__in=user_ids).values_list("id", "streak_count")
    )

    attempt_ids_by_user: dict[int, list[int]] = {}
    for row in aggregates[:limit]:
        attempt_ids_by_user[row["user_id"]] = list(
            attempts_qs.filter(user_id=row["user_id"]).values_list("id", flat=True)
        )

    all_attempt_ids = [aid for ids in attempt_ids_by_user.values() for aid in ids]
    answer_stats = (
        Answer.objects.filter(quiz_attempt_id__in=all_attempt_ids)
        .values("quiz_attempt__user_id")
        .annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        )
    )
    accuracy_map = {
        row["quiz_attempt__user_id"]: (
            round((row["correct"] / row["total"]) * 100, 1) if row["total"] else 0.0
        )
        for row in answer_stats
    }

    results: list[dict] = []
    for row in aggregates[:limit]:
        uid = row["user_id"]
        results.append({
            "user": uid,
            "username": row["user__username"],
            "score": int(row["score"] or 0),
            "quiz_count": row["quiz_count"],
            "accuracy": accuracy_map.get(uid, 0.0),
            "streak": streak_map.get(uid, 0),
        })

    for index, entry in enumerate(results, start=1):
        entry["rank"] = index
    return results


def user_leaderboard_rank(user: User, period: str = "all_time") -> dict:
    board = build_leaderboard(period=period, limit=10_000)
    for entry in board:
        if entry["user"] == user.id:
            return {"rank": entry["rank"], "score": entry["score"]}
    return {"rank": None, "score": 0}


def refresh_user_stats(user: User) -> None:
    """Update XP/rank and streak after a quiz attempt."""
    with transaction.atomic():
        locked = User.objects.select_for_update().get(pk=user.pk)
        attempts = QuizAttempt.objects.filter(user=locked)
        total_score = attempts.aggregate(total=Sum("score"))["total"] or 0
        locked.xp_points = int(total_score) * 10
        locked.rank_score = float(total_score)

        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        active_today = attempts.filter(completed_at__date=today).exists()

        if active_today:
            if locked.last_streak_date == today:
                pass
            elif locked.last_streak_date == yesterday:
                locked.streak_count = max(locked.streak_count, 0) + 1
            else:
                locked.streak_count = 1
            locked.last_streak_date = today
            locked.longest_streak = max(locked.longest_streak, locked.streak_count)

        locked.save(
            update_fields=[
                "xp_points",
                "rank_score",
                "streak_count",
                "longest_streak",
                "last_streak_date",
            ]
        )

    user.streak_count = locked.streak_count
    user.longest_streak = locked.longest_streak
    user.last_streak_date = locked.last_streak_date
    user.xp_points = locked.xp_points
    user.rank_score = locked.rank_score
