from django import forms

from quiz.models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = ["created_at"]
        widgets = {
            "mode": forms.Select(attrs={"class": "form-control"}),
            "number_of_questions": forms.Select(attrs={"class": "form-control"}),
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "category": forms.SelectMultiple(attrs={"class": "form-control"}),
            "technology": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

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
    id = forms.IntegerField(
        required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    uuid = forms.UUIDField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
