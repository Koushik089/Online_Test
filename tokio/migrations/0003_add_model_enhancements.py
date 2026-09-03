from django.db import migrations, models
import django.utils.timezone


def lowercase_correct_answer(apps, schema_editor):
    Question = apps.get_model('tokio', 'Question')
    for q in Question.objects.all():
        if q.correct_answer:
            q.correct_answer = q.correct_answer.lower()
            q.save(update_fields=['correct_answer'])


class Migration(migrations.Migration):

    dependencies = [
        ('tokio', '0002_question_examsession_userprofile_notification_and_more'),
    ]

    operations = [
        # Question new fields
        migrations.AddField(
            model_name='question',
            name='difficulty',
            field=models.CharField(max_length=10, null=True, blank=True, db_index=True, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]),
        ),
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.CharField(default='', max_length=255, blank=True),
        ),

        # ExamSession new fields
        migrations.AddField(
            model_name='examsession',
            name='duration_minutes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='ip_address',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='examsession',
            name='user_agent',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='examsession',
            index=models.Index(fields=['user', 'created_at'], name='tokio_examsess_user_created_idx'),
        ),

        # StudentResponse new fields
        migrations.AddField(
            model_name='studentresponse',
            name='answered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentresponse',
            name='response_time_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='studentresponse',
            index=models.Index(fields=['session', 'is_correct'], name='tokio_studentresp_session_correct_idx'),
        ),

        # Notification new field
        migrations.AddField(
            model_name='notification',
            name='level',
            field=models.CharField(default='info', max_length=10, choices=[('info', 'Info'), ('warn', 'Warning'), ('critical', 'Critical')]),
        ),

        # Data migration: normalize correct_answer to lowercase
        migrations.RunPython(lowercase_correct_answer, reverse_code=migrations.RunPython.noop),
    ]
