from django.contrib import admin

from .models import Author, Answer, Quiz, Question
from modeltranslation.admin import TranslationAdmin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "company")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("user_name", "email", "prog_language", "seniority")
    readonly_fields = (
        "general_score",
        "junior_score",
        "regular_score",
        "senior_score",
        "created_at",
        "number_of_junior_series",
        "number_of_regular_series",
        "number_of_senior_series",
    )


class QuestionAdmin(TranslationAdmin):
    list_display = ("seniority", "question_type", "text",)
    readonly_fields = ("created_at",)


class AnswerAdmin(TranslationAdmin):
    list_display = ("question", "text", "is_correct")
    readonly_fields = ("created_at",)


admin.site.register(Author, AuthorAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
