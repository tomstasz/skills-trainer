from django import forms

from quiz.models import Quiz


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


class QuestionSearchForm(forms.Form):
    id = forms.IntegerField(required=False)
    uuid = forms.UUIDField(required=False)
