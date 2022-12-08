from django import forms

from quiz.models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = ["general_score", "junior_score", "regular_score", "senior_score"]

    field_order = ["user_name", "email", "prog_language", "seniority", "number_of_questions"]
