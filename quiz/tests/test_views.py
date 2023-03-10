from http import HTTPStatus

from quiz.views import TIMEZONES
from quiz.utils import SENIORITY_CHOICES

from quiz.tests.mixins import TestViewMixin


class TestQuizView(TestViewMixin):
    def test_renders_quiz_form__when_get_request(self):
        response = self.client.get(self.quiz_url)

        assert response.status_code == HTTPStatus.OK
        assert response.context["quiz_form"].as_p() == self.quiz_form.as_p()
        assert response.context["timezones"] == TIMEZONES
        assert response.context["seniority_levels"] == SENIORITY_CHOICES

    def test_post_request_redirect__when_timezone__not_set(self):
        timezone = ["Europe/Warsaw"]
        response = self.client.post(self.quiz_url, data={"timezone": timezone})

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.quiz_url

    class TestQuestionView(TestViewMixin):
        def test_get_request_return_corrrect_context_and_template(self, db, client):
            session = self.client.session
            session["technologies"] = [self.technology.pk]
            session["current_technology"] = self.question.technology.pk
            session.save()
            self.score.score_data["used_ids"] = []
            self.score.score_data["finished_series"] = {"1": 0, "2": 0, "3": 0}
            self.score.score_data["technologies"] = [1]
            self.score.save()

            response = self.client.get(self.question_url, data={"q": self.quiz.pk})

            assert response.status_code == HTTPStatus.OK
            assert response.context["question"] == self.question
            assert response.context["time"] == self.question.time
            assert response.context["quiz"] == self.quiz
            if self.question.question_type == "multiple_choice":
                assert response.templates[0].name == "single_question.html"
            elif self.question.question_type == "open":
                assert response.templates[0].name == "single_question_open.html"
            elif self.question.question_type == "true/false":
                assert response.templates[0].name == "boolean_question.html"

        def test_get_request_redirect__when_max_questions_in_score_used_and_quiz_finished(
            self, db, client
        ):
            session = self.client.session
            session["technologies"] = [self.technology.pk]
            session["current_technology"] = self.question.technology.pk
            session.save()
            self.score.score_data["used_ids"] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            self.score.save()

            response = self.client.get(self.question_url, data={"q": self.quiz.pk})

            assert response.status_code == HTTPStatus.FOUND
            assert response.url == self.result_url
