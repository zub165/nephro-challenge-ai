from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_user_streak_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIKnowledgeEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("topic", models.CharField(blank=True, db_index=True, default="", max_length=150)),
                (
                    "content_type",
                    models.CharField(
                        choices=[("pearl", "Pearl"), ("mcq", "MCQ"), ("rule", "Rule"), ("admin", "Admin")],
                        default="rule",
                        max_length=20,
                    ),
                ),
                ("original_text", models.TextField(blank=True, default="")),
                ("corrected_text", models.TextField(blank=True, default="")),
                ("lesson_rule", models.TextField()),
                ("reference", models.TextField(blank=True, default="")),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("llama_audit", "LLaMA audit"),
                            ("rule_check", "Rule check"),
                            ("admin", "Admin"),
                            ("verification", "Verification"),
                        ],
                        default="rule_check",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("confidence", models.CharField(blank=True, default="medium", max_length=10)),
                ("use_count", models.PositiveIntegerField(default=0)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_ai_lessons",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["status", "topic"], name="api_aiknowl_status_8f2a1c_idx")],
            },
        ),
    ]
