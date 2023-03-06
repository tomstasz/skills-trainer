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
    template_choice,
    check_question_type_to_update_score,
    update_score,
    del_quiz_session_data,
    del_session_keys,
    draw_questions,
    save_number_of_finished_series,
)

from quiz.fixture_factories import (
    ScoreDictFactory,
    SCORE_DATA,
    AnswerDictFactory,
    AuthorDictFactory,
    QuestionDictFactory,
)


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
        self.score.score_data["general_score"] = 0
        self.score.score_data["junior_score"] = 0
        self.score.score_data["regular_score"] = 0
        self.score.score_data["senior_score"] = 0
        self.score.score_data["seniority_level"] = 1

        self.answer_data = AnswerDictFactory.build()
        self.author_data = AuthorDictFactory.build()
        self.question_data = self.answer_data["question"]
        self.author = Author.objects.create(**self.author_data)

        self.question_data["category"] = self.category
        self.question_data["technology"] = self.technology
        self.question_data["seniority"] = self.seniority
        self.question_data["author"] = self.author
        self.question = Question.objects.create(**self.question_data)

        self.answer_data["question"] = self.question
        self.answer = [Answer.objects.create(**self.answer_data)]

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

    def test_template_choice(self):
        question_types = ("open", "multiple choice", "true/false")
        expected_results = (
            "single_question_open.html",
            "single_question.html",
            "boolean_question.html",
        )
        for question_type, expected_result in zip(question_types, expected_results):
            template = template_choice(question_type)
            assert template == expected_result

    def test_update_score(self):
        score = copy.deepcopy(self.score)
        score = update_score(score)

        assert score.score_data["general_score"] == 1
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 2
        score = update_score(score)

        assert score.score_data["general_score"] == 2
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 3
        score = update_score(score)

        assert score.score_data["general_score"] == 3
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 1

    def test_check_question_type_to_update_score__changes_score_when_question_is_boolean_type(
        self,
    ):
        self.question.question_type = "true/false"
        post_request = RequestFactory().post(
            path=self.url,
            data={"ans": self.answer[0].text, "csrfmiddlewaretoken": "xxx"},
        )
        score = copy.deepcopy(self.score)
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 1
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 2
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 2
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 3
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 3
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 1

    def test_check_question_type_to_update_score__changes_score_when_question_is_open_type(
        self,
    ):
        self.question.question_type = "open"
        post_request = RequestFactory().post(
            path=self.url,
            data={"ans": self.answer[0].text, "csrfmiddlewaretoken": "xxx"},
        )
        score = copy.deepcopy(self.score)
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 1
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 2
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 2
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 3
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 3
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 1

    def test_check_question_type_to_update_score__changes_score_when_question_is_multichoice_type(
        self,
    ):
        self.question.question_type = "multiple choice"
        self.answer[0].is_correct = True
        post_request = RequestFactory().post(
            path=self.url,
            data={
                f"{self.answer[0].pk}": self.answer[0].text,
                "csrfmiddlewaretoken": "xxx",
            },
        )
        score = copy.deepcopy(self.score)
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 1
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 2
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 2
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 0

        score.score_data["seniority_level"] = 3
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 3
        assert score.score_data["junior_score"] == 1
        assert score.score_data["regular_score"] == 1
        assert score.score_data["senior_score"] == 1

    def test_check_question_type_to_update_score__not_changes_score_when_answer_is_wrong(
        self,
    ):
        self.question.question_type = "true/false"
        post_request = RequestFactory().post(
            path=self.url, data={"ans": "wrong answer", "csrfmiddlewaretoken": "xxx"}
        )
        score = copy.deepcopy(self.score)
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 0
        assert score.score_data["junior_score"] == 0
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

    def test_check_question_type_to_update_score__not_changes_score_when_answer_is_wrong_and_question_is_multichoice_type(
        self,
    ):
        self.question.question_type = "multiple choice"
        post_request = RequestFactory().post(
            path=self.url,
            data={f"wrong pk": "wrong answer", "csrfmiddlewaretoken": "xxx"},
        )
        score = copy.deepcopy(self.score)
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, score
        )

        assert score.score_data["general_score"] == 0
        assert score.score_data["junior_score"] == 0
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

    def test_del_quiz_session_data(self):
        self.request.session["quiz_pk"] = "test quiz pk"
        self.request.session["selected_technologies"] = "test technologies"
        del_quiz_session_data(self.request)

        assert self.request.session.get("quiz_pk") == None
        assert self.request.session.get("selected_technologies") == None

    def test_del_session_keys(self):
        self.request.session["technologies"] = "test technologies"
        self.request.session["current_technology"] = "test current tech"
        self.request.session["training"] = "test training"
        del_session_keys(self.request)

        assert self.request.session.get("technologies") == None
        assert self.request.session.get("current_technology") == None
        assert self.request.session.get("training") == None

    def test_draw_questions__when_next_id_in_db(self, db):
        used_ids = None
        self.question.seniority.level = 1
        self.question.category.pk = 1
        self.question.technology.pk = 1
        drawn_ids = draw_questions(
            self.question.seniority.level,
            [self.question.category.pk],
            self.question.technology.pk,
            used_ids,
        )

        assert self.question.pk == drawn_ids

    def test_draw_questions__when_next_id_not_in_db(self, db):
        used_ids = None
        self.question.seniority.level = 2
        self.question.category.pk = 1
        self.question.technology.pk = 1
        drawn_ids = draw_questions(
            self.question.seniority.level,
            [self.question.category.pk],
            self.question.technology.pk,
            used_ids,
        )

        assert drawn_ids == None

    def test_save_number_of_finished_series(self):
        score = copy.deepcopy(self.score)
        score.score_data["number_of_junior_series"] = 0
        score.score_data["number_of_regular_series"] = 0
        score.score_data["number_of_senior_series"] = 0
        result = save_number_of_finished_series(score)

        assert (
            result.score_data["number_of_junior_series"]
            == result.score_data["finished_series"]["1"]
        )
        assert (
            result.score_data["number_of_regular_series"]
            == result.score_data["finished_series"]["2"]
        )
        assert (
            result.score_data["number_of_senior_series"]
            == result.score_data["finished_series"]["3"]
        )
