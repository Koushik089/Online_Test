from django import forms
from .models import Question

class AdminLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'marks', 'difficulty', 'explanation', 'tags']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows':3}),
            'explanation': forms.Textarea(attrs={'rows':3}),
        }

    def clean_correct_answer(self):
        val = self.cleaned_data.get('correct_answer')
        if not val or val.lower() not in ('a','b','c','d'):
            raise forms.ValidationError('Correct answer must be one of: a, b, c, d')
        return val.lower()

    def clean_marks(self):
        m = self.cleaned_data.get('marks')
        if m is None:
            return 1
        if m <= 0:
            raise forms.ValidationError('Marks must be a positive integer')
        return m
