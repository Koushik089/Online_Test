from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tokio', '0003_add_model_enhancements'),
    ]

    operations = [
        migrations.AddField(
            model_name='examsession',
            name='total_response_time_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='avg_response_time_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='fastest_response_time_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='slowest_response_time_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
