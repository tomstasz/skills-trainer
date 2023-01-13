from django.contrib import admin

from .models import Author, Answer, Category, Score, Technology, Quiz, Question
from modeltranslation.admin import TranslationAdmin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "company")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("user_name", "email", "seniority")
    readonly_fields = ("created_at",)


class QuestionAdmin(TranslationAdmin):
    list_display = (
        "category",
        "technology",
        "seniority",
        "question_type",
        "text",
    )
    readonly_fields = ("created_at",)


class AnswerAdmin(TranslationAdmin):
    list_display = ("question", "text", "is_correct")
    readonly_fields = ("created_at",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "technology", "quiz")
    readonly_fields = (
        "technology",
        "junior_score",
        "number_of_junior_series",
        "regular_score",
        "number_of_regular_series",
        "senior_score",
        "number_of_senior_series",
        "general_score",
    )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Technology, TechnologyAdmin)
admin.site.register(Score, ScoreAdmin)
