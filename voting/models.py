from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Candidate(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=150)
    biography = models.TextField(blank=True, null=True)
    votes_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.poll.title})"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')
        indexes = [
            models.Index(fields=['user', 'poll']),
        ]

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate.name} in {self.poll.title}"
