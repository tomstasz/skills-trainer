from django.urls import path
from .views import QuestionView, QuizView

app_name = 'quiz'

urlpatterns = [
    path("", QuizView.as_view(), name='quiz-view'),
    path("<int:pk>/", QuestionView.as_view(), name='question-view'),
]