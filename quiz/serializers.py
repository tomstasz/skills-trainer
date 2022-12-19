from rest_framework import serializers

from quiz.models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = (
            "id",
            "user_name",
            "general_score",
            "junior_score",
            "regular_score",
            "senior_score",
            "seniority",
        )
