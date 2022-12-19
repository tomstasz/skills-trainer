from django.urls import path, include
from rest_framework import routers
from .views import QuestionView, QuizView, ResultsViewSet

router = routers.SimpleRouter()
router.register(r"results", ResultsViewSet)

app_name = "quiz"

urlpatterns = [
    path("", QuizView.as_view(), name="quiz-view"),
    path("<int:pk>/", QuestionView.as_view(), name="question-view"),
    path("", include(router.urls)),
]
