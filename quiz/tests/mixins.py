import pytest
import copy

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

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
from quiz.forms import QuizForm
from quiz.utils import SENIORITY_CHOICES

from quiz.fixture_factories import (
    ScoreDictFactory,
    AnswerDictFactory,
    AuthorDictFactory,
)


class TestUtilMixin:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.url = "https://www.example.com/"
        # prepare session mock
        self.request = RequestFactory().get(self.url)
        middleware = SessionMiddleware(self.request)
        middleware.process_request(self.request)
        self.request.session.save()

        self.score_data = ScoreDictFactory.build()
        self.next_score_data = ScoreDictFactory.build()
        self.quiz_data = self.score_data["quiz"]
        self.category_data = self.score_data["quiz"]["category"]
        self.technology_data = self.score_data["quiz"]["technology"]
        self.next_technology_data = self.next_score_data["quiz"]["technology"]
        self.seniority_data = self.score_data["seniority"]

        self.category = Category.objects.create(**self.category_data)
        self.technology = Technology.objects.create(**self.technology_data)
        self.next_technology = Technology.objects.create(**self.next_technology_data)
        self.seniority = Seniority.objects.create(**self.seniority_data)

        del self.score_data["quiz"]["category"]
        del self.score_data["quiz"]["technology"]

        self.quiz = Quiz.objects.create(**self.score_data["quiz"])
        self.quiz.category.set([self.category])
        self.quiz.technology.set([self.technology, self.next_technology])
        self.single_serie = int(self.quiz.number_of_questions / len(SENIORITY_CHOICES))

        self.score_data["quiz"] = self.quiz
        self.score_data["seniority"] = self.seniority
        self.score_data["technology"] = self.technology

        self.next_score_data["quiz"] = self.quiz
        self.next_score_data["seniority"] = self.seniority
        self.next_score_data["technology"] = self.next_technology
        self.next_score = Score.objects.create(**self.next_score_data)

        self.score = Score.objects.create(**self.score_data)
        self.null_score = copy.deepcopy(self.score)
        self.null_score.score_data["general_score"] = 0
        self.null_score.score_data["junior_score"] = 0
        self.null_score.score_data["regular_score"] = 0
        self.null_score.score_data["senior_score"] = 0
        self.null_score.score_data["seniority_level"] = 1
        self.null_score.score_data["finished_series"] = {"1": 0, "2": 0, "3": 0}

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


class TestViewMixin:
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
        self.quiz_form = QuizForm()

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

        self.answer_data = AnswerDictFactory.build()
        self.next_answer_data = AnswerDictFactory.build()
        self.author_data = AuthorDictFactory.build()
        self.question_data = self.answer_data["question"]
        self.next_question_data = self.next_answer_data["question"]
        self.author = Author.objects.create(**self.author_data)

        self.question_data["category"] = self.category
        self.question_data["technology"] = self.technology
        self.question_data["seniority"] = self.seniority
        self.question_data["author"] = self.author
        self.next_question_data["category"] = self.category
        self.next_question_data["technology"] = self.technology
        self.next_question_data["seniority"] = self.seniority
        self.next_question_data["author"] = self.author

        self.question = Question.objects.create(**self.question_data)
        self.next_question = Question.objects.create(**self.next_question_data)

        self.answer_data["question"] = self.question
        self.answer = [Answer.objects.create(**self.answer_data)]

        self.next_answer_data["question"] = self.next_question
        self.next_answer = [Answer.objects.create(**self.next_answer_data)]

        self.question_url = reverse(
            "quiz:question-view", kwargs={"uuid": self.question.uuid}
        )
        self.next_question_url = reverse(
            "quiz:question-view", kwargs={"uuid": self.next_question.uuid}
        )
        self.result_url = reverse("quiz:training-view", kwargs={"uuid": self.quiz.uuid})
