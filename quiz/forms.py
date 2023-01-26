from django import forms
from django.utils.translation import gettext_lazy as _

from quiz.models import Quiz, Technology, MODE_CHOICES


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = ["created_at"]
        widgets = {"mode": forms.Select}

    field_order = [
        "user_name",
        "email",
        "mode",
        "number_of_questions",
        "category",
        "technology",
    ]


class UserEmailForm(forms.ModelForm):
    email = forms.ModelChoiceField(
        queryset=Quiz.objects.values_list("email", flat=True)
    )

    class Meta:
        model = Quiz
        fields = ["email"]
        widgets = {"email": forms.Select}
