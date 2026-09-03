from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tokio', '0004_add_timing_analytics'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='marks',
            field=models.IntegerField(default=1),
        ),
    ]
