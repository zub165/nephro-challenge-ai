from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_studynote_enrichment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]