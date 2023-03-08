import pytest
import requests
import requests_mock

from http import HTTPStatus
from unittest.mock import Mock, patch

from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from quiz.models import SENIORITY_CHOICES
from quiz.views import TIMEZONES
from quiz.forms import QuizForm

from django.urls import reverse


class TestQuizView:
    @pytest.fixture(autouse=True)
    def setup(self, db, client):
        self.url = "https://www.example.com/"
        # prepare session mock
        self.request = RequestFactory().get(self.url)
        middleware = SessionMiddleware(self.request)
        middleware.process_request(self.request)
        self.request.session.save()

        self.client = client
        self.quiz_url = reverse("quiz:quiz-view")

    def test_renders_quiz_form__when_get_request(self):
        quiz_form = QuizForm()
        response = self.client.get(self.quiz_url)

        assert response.status_code == HTTPStatus.OK
        assert response.context["quiz_form"].fields.keys() == quiz_form.fields.keys()
        assert response.context["timezones"] == TIMEZONES
        assert response.context["seniority_levels"] == SENIORITY_CHOICES

    def test_post_request_redirect__when_timezone__not_set(self):
        response = self.client.post(self.quiz_url, data={"timezone": ["Europe/Warsaw"]})

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.quiz_url
