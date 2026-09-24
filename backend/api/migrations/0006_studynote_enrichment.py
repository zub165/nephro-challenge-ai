from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_merge_streak_and_learning"),
    ]

    operations = [
        migrations.AddField(
            model_name="studynote",
            name="reference",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="studynote",
            name="verified",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="studynote",
            name="verification_confidence",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AddField(
            model_name="studynote",
            name="verification_issues",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
