import pytest
from unittest.mock import Mock, patch

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
from quiz.fixture_factories import (
    AnswerDictFactory,
    AuthorDictFactory,
    CategoryDictFactory,
    TechnologyDictFactory,
    SeniorityDictFactory,
    QuestionDictFactory,
    QuizDictFactory,
    ScoreDictFactory,
)


class TestAuthor:
    def test_author_created(self, db):
        self.author_data = AuthorDictFactory.build()
        self.author = Author.objects.create(**self.author_data)

        assert self.author.name == self.author_data["name"]
        assert self.author.company == self.author_data["company"]


class TestCategory:
    def test_category_created(self, db):
        self.category_data = CategoryDictFactory.build()
        self.category = Category.objects.create(**self.category_data)

        assert self.category.name == self.category_data["name"]


class TestTechnololgy:
    def test_technology_created(self, db):
        self.technology_data = TechnologyDictFactory.build()
        self.technology = Technology.objects.create(**self.technology_data)

        assert self.technology.name == self.technology_data["name"]


class TestSeniority:
    def test_seniority_created(self, db):
        self.seniority_data = SeniorityDictFactory.build()
        self.seniority = Seniority.objects.create(**self.seniority_data)

        assert self.seniority.level == self.seniority_data["level"]


class TestQuestion:
    def test_question_created(self, db):
        self.question_data = QuestionDictFactory.build()
        self.category_data = self.question_data["category"]
        self.technology_data = self.question_data["technology"]
        self.seniority_data = self.question_data["seniority"]
        self.author_data = self.question_data["author"]

        self.question_data["category"] = Category.objects.create(**self.category_data)
        self.question_data["technology"] = Technology.objects.create(
            **self.technology_data
        )
        self.question_data["seniority"] = Seniority.objects.create(
            **self.seniority_data
        )
        self.question_data["author"] = Author.objects.create(**self.author_data)

        self.question = Question.objects.create(**self.question_data)

        assert self.question_data["text"] == self.question.text
        assert self.question_data["uuid"] == self.question.uuid
        assert self.question_data["question_type"] == self.question.question_type
        assert self.question_data["time"] == self.question.time
        assert self.question_data["created_at"] == self.question.created_at

        assert self.category_data["name"] == self.question.category.name
        assert self.technology_data["name"] == self.question.technology.name
        assert self.seniority_data["level"] == self.question.seniority.level
        assert self.author_data["name"] == self.question.author.name
        assert self.author_data["company"] == self.question.author.company


class TestAnswer:
    def test_answer_created(self, db):
        self.answer_data = AnswerDictFactory.build()
        self.question_data = self.answer_data["question"]
        self.question_data["category"] = Category.objects.create(
            **self.question_data["category"]
        )
        self.question_data["technology"] = Technology.objects.create(
            **self.question_data["technology"]
        )
        self.question_data["seniority"] = Seniority.objects.create(
            **self.question_data["seniority"]
        )
        self.question_data["author"] = Author.objects.create(
            **self.question_data["author"]
        )

        self.question = Question.objects.create(**self.question_data)
        self.answer_data["question"] = self.question

        self.answer = Answer.objects.create(**self.answer_data)

        assert self.answer_data["text"] == self.answer.text
        assert self.answer_data["is_correct"] == self.answer.is_correct
        assert self.answer_data["created_at"] == self.answer.created_at

        assert self.question_data["text"] == self.answer.question.text
        assert self.question_data["uuid"] == self.answer.question.uuid


class TestQuiz:
    def test_quiz_created(self, db):
        self.quiz_data = QuizDictFactory.build()
        self.category_data = self.quiz_data["category"]
        self.technology_data = self.quiz_data["technology"]

        self.category = Category.objects.create(**self.category_data)
        self.technology = Technology.objects.create(**self.technology_data)

        del self.quiz_data["category"]
        del self.quiz_data["technology"]

        self.quiz = Quiz.objects.create(**self.quiz_data)

        self.quiz.category.set([self.category])
        self.quiz.technology.set([self.technology])

        assert self.quiz_data["uuid"] == self.quiz.uuid
        assert self.quiz_data["user_name"] == self.quiz.user_name
        assert self.quiz_data["email"] == self.quiz.email
        assert self.quiz_data["number_of_questions"] == self.quiz.number_of_questions
        assert self.quiz_data["created_at"] == self.quiz.created_at
        assert self.quiz_data["mode"] == self.quiz.mode

        assert self.category_data["name"] == self.quiz.category.first().name
        assert self.technology_data["name"] == self.quiz.technology.first().name


class TestScore:
    def test_score_created(self, db):
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

        assert self.quiz_data["uuid"] == self.score.quiz.uuid
        assert self.category_data["name"] == self.score.quiz.category.first().name
        assert self.technology_data["name"] == self.score.quiz.technology.first().name
        assert self.seniority_data["level"] == self.score.seniority.level
        assert self.score.quiz.technology.first().name == self.score.technology.name
