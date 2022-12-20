from rest_framework import serializers

from quiz.models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = (
            "id",
            "user_name",
            "email",
            "general_score",
            "junior_score",
            "regular_score",
            "senior_score",
            "seniority",
            "number_of_junior_series",
            "number_of_regular_series",
            "number_of_senior_series",
        )
