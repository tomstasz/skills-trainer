from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Author, Answer, Quiz, Question

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "company")

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("user_name", "prog_language", "seniority")
    readonly_fields = ("general_score", "junior_score", "regular_score", "senior_score")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_filter = ("created_at", "updated_at")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")
    list_filter = ("created_at", "updated_at")
