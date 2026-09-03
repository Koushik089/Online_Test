from django.db import models
from django.contrib.auth.models import User

# ✅ Admin model linked with Django User
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django auth User
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ✅ Question Model
class Question(models.Model):
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1)  # 'a', 'b', 'c', or 'd'

    def __str__(self):
        return self.question_text

# ✅ Student Answer Model
class StudentAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1)  # 'a', 'b', 'c', or 'd'
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Q{self.question.id}"
