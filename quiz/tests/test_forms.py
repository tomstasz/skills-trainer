import pytest
from http import HTTPStatus

from quiz.models import SENIORITY_CHOICES, Technology, Category
from quiz.forms import QuizForm, QuestionSearchForm
from quiz.fixture_factories import (
    TechnologyDictFactory,
    CategoryDictFactory,
    QuizDictFactory,
)


class TestQuizForm:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.technology_data = TechnologyDictFactory.build(id=2)
        self.category_data = CategoryDictFactory.build(id=2)
        self.technology = Technology.objects.create(**self.technology_data)
        self.category = Category.objects.create(**self.category_data)
        self.form_data = {
            "user_name": "Test user",
            "email": "test@onet.pl",
            "mode": "training",
            "number_of_questions": "9",
            "category": ["2"],
            "technology": ["2"],
        }

    def test_create_quiz_form_instance(self):
        form = QuizForm(data=self.form_data)

        assert form.is_valid() == True
        for k, v in self.form_data.items():
            assert form[k].value() == v

    def test_not_create_quiz_form_instance__when_invalid_data(self):
        form = QuizForm(data={"xxx": "xxx"})

        assert form.is_valid() == False


class TestQuestionSearchForm:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.form_data = {"id": 999, "uuid": "ef830cb3460a4677a6ff051b69687850"}

    def test_create_question_search_form_instance(self):
        form = QuestionSearchForm(data=self.form_data)

        assert form.is_valid() == True
        for k, v in self.form_data.items():
            assert form[k].value() == v

    def test_not_create_question_search_form_instance__when_invalid_data(self):
        form = QuizForm(data={"xxx": "xxx"})

        assert form.is_valid() == False
