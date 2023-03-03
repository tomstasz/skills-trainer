import pytest
import requests
import requests_mock

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

from quiz.utils import prepare_technologies_in_session

from quiz.fixture_factories import ScoreDictFactory


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

    def test_if_prepare_technologies_in_session__adds_technologies_to_session(self, db):
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
