from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_studynote"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="longest_streak",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="last_streak_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
