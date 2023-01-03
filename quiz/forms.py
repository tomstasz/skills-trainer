from django import forms
from django.utils.translation import gettext_lazy as _

from quiz.models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = [
            "general_score",
            "junior_score",
            "regular_score",
            "senior_score",
            "number_of_junior_series",
            "number_of_regular_series",
            "number_of_senior_series",
            "created_at",
        ]

    field_order = [
        "user_name",
        "email",
        "category",
        "technology",
        "seniority",
        "number_of_questions",
    ]


class UserEmailForm(forms.ModelForm):
    email = forms.ModelChoiceField(
        queryset=Quiz.objects.values_list("email", flat=True)
    )

    class Meta:
        model = Quiz
        fields = ["email"]
        widgets = {"email": forms.Select()}
