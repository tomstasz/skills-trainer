from django.urls import path, include
from rest_framework import routers
from .views import (
    QuestionView,
    QuizView,
    ResultsViewSet,
    ResultFormView,
    single_result_view,
)

router = routers.SimpleRouter()
router.register(r"api/result_list", ResultsViewSet)

app_name = "quiz"

urlpatterns = [
    path("", QuizView.as_view(), name="quiz-view"),
    path("<uuid:uuid>/", QuestionView.as_view(), name="question-view"),
    path("", include(router.urls)),
    path("find/", ResultFormView.as_view(), name="result-view"),
    path("training-result/<int:pk>", single_result_view, name="training-view"),
]
