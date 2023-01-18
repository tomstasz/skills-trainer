import uuid
from django.db import models

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField


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
)

LANGUAGE_CHOICES = (
    ("English", "English"),
    ("Polish", "Polish"),
    ("German", "German"),
)


class Quiz(models.Model):
    category = models.ManyToManyField("Category", verbose_name=_("category"))
    technology = models.ManyToManyField("Technology", verbose_name=_("technology"))
    user_name = models.CharField(_("User Name"), max_length=120)
    email = models.CharField(max_length=120, unique=True)
    number_of_questions = models.IntegerField(
        _("Number of questions"), choices=NUM_OF_QUESTIONS
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "quizes"

    def __str__(self):
        return f"{self.user_name} - {self.email}"


class Question(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    text = RichTextUploadingField(null=True, blank=True, config_name="special")
    question_type = models.CharField(max_length=64, choices=QUESTION_TYPE_CHOICES)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    technology = models.ForeignKey("Technology", on_delete=models.CASCADE)
    seniority = models.ForeignKey("Seniority", on_delete=models.PROTECT)
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, null=True, blank=True
    )
    time = models.IntegerField(default=30, help_text="duration in minutes")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.text}"

    def get_answers(self):
        return self.answer_set.all()

    def is_author(self):
        return True if self.author else False


class Answer(models.Model):
    text = RichTextUploadingField(null=True, blank=True, config_name="special")
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


class Category(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "technologies"

    def __str__(self):
        return self.name


class Score(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    technology = models.ForeignKey("Technology", on_delete=models.PROTECT)
    seniority = models.ForeignKey(
        "Seniority", on_delete=models.PROTECT, null=True, blank=True
    )
    general_score = models.IntegerField(default=0)
    junior_score = models.IntegerField(default=0)
    number_of_junior_series = models.IntegerField(default=0)
    regular_score = models.IntegerField(default=0)
    number_of_regular_series = models.IntegerField(default=0)
    senior_score = models.IntegerField(default=0)
    number_of_senior_series = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.technology} - {self.quiz}"


class Seniority(models.Model):
    level = models.IntegerField(choices=SENIORITY_CHOICES, verbose_name=_("Seniority"))

    class Meta:
        verbose_name_plural = "seniority"

    def __str__(self):
        return f"{self.level}"
