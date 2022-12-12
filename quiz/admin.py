from django.contrib import admin

from .models import Author, Answer, Quiz, Question
from modeltranslation.admin import TranslationAdmin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "company")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("user_name", "prog_language", "seniority")
    readonly_fields = ("general_score", "junior_score", "regular_score", "senior_score")


class QuestionAdmin(TranslationAdmin):
    list_filter = ("created_at", "updated_at")


class AnswerAdmin(TranslationAdmin):
    list_display = ("question", "text", "is_correct")
    list_filter = ("created_at", "updated_at")


admin.site.register(Author, AuthorAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
