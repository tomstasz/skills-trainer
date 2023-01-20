from django.contrib import admin

from .models import (
    Author,
    Answer,
    Category,
    Score,
    Technology,
    Quiz,
    Question,
    Seniority,
)
from modeltranslation.admin import TranslationAdmin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "company")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("user_name", "email")
    readonly_fields = ("created_at",)


class QuestionAdmin(TranslationAdmin):
    list_display = (
        "technology",
        "category",
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
    list_display = ("technology", "quiz")
    readonly_fields = (
        "technology",
        "quiz",
        "seniority",
        "score_data",
    )


class SeniorityAdmin(admin.ModelAdmin):
    list_display = ("id", "level")


admin.site.register(Author, AuthorAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Technology, TechnologyAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Seniority, SeniorityAdmin)
