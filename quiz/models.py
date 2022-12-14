from django.db import models

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


PROG_LANG_CHOICES = (
    ("Java", "Java"),
    ("Python", "Python"),
    ("PHP", "PHP"),
    ("C++", "C++"),
)

SENIORITY_CHOICES = (
    (1, "junior"),
    (2, "regular"),
    (3, "senior"),
)

NUM_OF_QUESTIONS = (
    (6, 6),
    (9, 9),
    (12, 12),
)

QUESTION_TYPE_CHOICES = (
    ("multiple choice", "multiple choice"),
    ("open", "open"),
    ("true/false", "true/false"),
    ("image", "image"),
)

LANGUAGE_CHOICES = (
    ("English", "English"),
    ("Polish", "Polish"),
    ("German", "German"),
)


class Quiz(models.Model):
    prog_language = models.CharField(
        max_length=64, choices=PROG_LANG_CHOICES, verbose_name=_("Programming Language")
    )
    seniority = models.IntegerField(
        choices=SENIORITY_CHOICES, verbose_name=_("Seniority")
    )
    user_name = models.CharField(_("User Name"), max_length=120)
    email = models.CharField(max_length=120, unique=True)
    number_of_questions = models.IntegerField(
        _("Number of questions"), choices=NUM_OF_QUESTIONS
    )
    general_score = models.IntegerField(default=0)
    junior_score = models.IntegerField(default=0)
    regular_score = models.IntegerField(default=0)
    senior_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.prog_language} - {self.user_name}"


class Question(models.Model):
    text = models.CharField(max_length=240, null=True, blank=True)
    question_type = models.CharField(max_length=64, choices=QUESTION_TYPE_CHOICES)
    prog_language = models.CharField(
        max_length=64, choices=PROG_LANG_CHOICES, verbose_name=_("Programming Language")
    )
    seniority = models.IntegerField(choices=SENIORITY_CHOICES)
    image = models.ImageField(upload_to="../static/images", null=True, blank=True)
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, null=True, blank=True
    )
    time = models.IntegerField(default=30)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.seniority}: {self.text}"

    def get_answers(self):
        return self.answer_set.all()

    def is_author(self):
        return True if self.author else False


class Answer(models.Model):
    text = models.CharField(max_length=240, null=True, blank=True)
    image = models.ImageField(upload_to="../static/images", null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"question: {self.question.text}, answer: {self.text}, is_correct: {self.is_correct}"


class Author(models.Model):
    name = models.CharField(max_length=64)
    company = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} - {self.company}"
