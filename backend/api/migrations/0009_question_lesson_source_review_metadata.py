from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_boardexam_boardexamattempt_boardexamattemptitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="review_status",
            field=models.CharField(
                choices=[
                    ("needs_review", "Needs review"),
                    ("in_review", "In review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="needs_review",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="reviewed_by",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="question",
            name="source_metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="lesson",
            name="review_status",
            field=models.CharField(
                choices=[
                    ("needs_review", "Needs review"),
                    ("in_review", "In review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="needs_review",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="lesson",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="reviewed_by",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="lesson",
            name="source_metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
