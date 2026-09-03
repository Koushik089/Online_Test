from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Backwards-compatible model enhancements:
# - New optional fields are added with null=True or defaults to avoid breaking existing rows
# - Indexes added in Meta for common read patterns

class AdminUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return self.email

class Subject(models.Model):
    key = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=60, default='fa-solid fa-book')
    duration_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    subject = models.CharField(max_length=60)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1)  # 'a', 'b', 'c', or 'd'

    # New optional fields (nullable/blank to preserve backward compatibility)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, null=True, blank=True, db_index=True)
    explanation = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, default='')
    # Marks for the question (nullable/default to 1 for backward compatibility)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text[:50]

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        db_index=True
    )

    bio = models.TextField(blank=True, null=True)

    # Student online/activity tracking
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_online(self):
        """True if last_activity was within the last 5 minutes."""
        if not self.last_activity:
            return False
        return (timezone.now() - self.last_activity).total_seconds() < 300

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    
class ExamSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions', db_index=True)
    subject = models.CharField(max_length=50, db_index=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False, db_index=True)
    warnings_count = models.IntegerField(default=0)

    # New metadata fields
    duration_minutes = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # Timing analytics fields (nullable for backward compatibility)
    total_response_time_seconds = models.FloatField(null=True, blank=True)
    avg_response_time_seconds = models.FloatField(null=True, blank=True)
    fastest_response_time_seconds = models.FloatField(null=True, blank=True)
    slowest_response_time_seconds = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.score}/{self.total_questions}"

class StudentResponse(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='responses', db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_responses', db_index=True)
    selected_answer = models.CharField(max_length=1, blank=True, null=True)  # 'a', 'b', 'c', 'd' or None
    is_correct = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)

    # New timing/analytics fields
    answered_at = models.DateTimeField(null=True, blank=True)
    response_time_seconds = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session', 'question')
        indexes = [
            models.Index(fields=['session', 'is_correct']),
        ]

    def __str__(self):
        return f"{self.session.user.username} - Q{self.question.id} ({self.selected_answer})"

class Notification(models.Model):
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warn', 'Warning'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # New severity/level field (default 'info' keeps it non-breaking)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


