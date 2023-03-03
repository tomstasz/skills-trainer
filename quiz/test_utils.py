import pytest
import requests
import requests_mock
import copy

from unittest.mock import Mock, patch
from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from quiz.models import (
    Answer,
    Author,
    Category,
    Technology,
    Seniority,
    Question,
    Quiz,
    Score,
)

from quiz.utils import (
    prepare_technologies_in_session,
    set_initial_score_data,
    SENIORITY_CHOICES,
    save_number_of_finished_series,
)

from quiz.fixture_factories import ScoreDictFactory, SCORE_DATA


class TestUtils:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.url = "https://www.example.com/"
        # prepare session mock
        self.request = RequestFactory().get(self.url)
        middleware = SessionMiddleware(self.request)
        middleware.process_request(self.request)
        self.request.session.save()

        self.client = Client()

        self.score_data = ScoreDictFactory.build()
        self.quiz_data = self.score_data["quiz"]
        self.category_data = self.score_data["quiz"]["category"]
        self.technology_data = self.score_data["quiz"]["technology"]
        self.seniority_data = self.score_data["seniority"]

        self.category = Category.objects.create(**self.category_data)
        self.technology = Technology.objects.create(**self.technology_data)
        self.seniority = Seniority.objects.create(**self.seniority_data)

        del self.score_data["quiz"]["category"]
        del self.score_data["quiz"]["technology"]

        self.quiz = Quiz.objects.create(**self.score_data["quiz"])
        self.quiz.category.set([self.category])
        self.quiz.technology.set([self.technology])

        self.score_data["quiz"] = self.quiz
        self.score_data["seniority"] = self.seniority
        self.score_data["technology"] = self.technology

        self.score = Score.objects.create(**self.score_data)

    def test_if_prepare_technologies_in_session__adds_technologies_to_session(self):
        session = self.request.session
        session["technologies"] = None
        prepare_technologies_in_session(self.request, self.score)

        assert self.score.score_data["technologies"] == session["technologies"]

    def test_if_prepare_technologies_in_session__does_not_add_technologies_if_technologies_already_in_session(
        self, db
    ):
        session = self.request.session
        expected_data = [1, 2]
        session["technologies"] = expected_data
        prepare_technologies_in_session(self.request, self.score)

        assert session["technologies"] == expected_data

    def test_if_set_initial_score_data__adds_correct_data(self):
        updated_score_data = set_initial_score_data(self.quiz)
        quiz_category = [category.pk for category in self.quiz.category.all()]
        quiz_technology = [technology.pk for technology in self.quiz.technology.all()]

        assert (
            int(self.quiz.number_of_questions / len(SENIORITY_CHOICES))
            == updated_score_data["num_in_series"]
        )
        assert (
            self.quiz.number_of_questions == updated_score_data["max_num_of_questions"]
        )
        for quiz_cat, score_cat in zip(quiz_category, updated_score_data["categories"]):
            assert quiz_cat == score_cat
        for quiz_tech, score_tech in zip(
            quiz_technology, updated_score_data["technologies"]
        ):
            assert quiz_tech == score_tech
        assert "finished_series" in updated_score_data.keys()

    def test_if_number_of_finished_series__is_saved(self):
        initial_score_data = set_initial_score_data(self.quiz)
        score = copy.deepcopy(self.score)
        score.score_data = initial_score_data
        score.score_data["finished_series"] = {"1": 1, "2": 1, "3": 1}

        assert score.score_data["number_of_junior_series"] == 0
        assert score.score_data["number_of_regular_series"] == 0
        assert score.score_data["number_of_senior_series"] == 0

        save_number_of_finished_series(score)

        assert score.score_data["number_of_junior_series"] == 1
        assert score.score_data["number_of_regular_series"] == 1
        assert score.score_data["number_of_senior_series"] == 1
