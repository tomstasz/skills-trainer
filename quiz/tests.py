import pytest
from unittest.mock import Mock, patch

from quiz.models import Author, Category, Technology, Seniority, Question
from quiz.fixture_factories import (
    AuthorDictFactory,
    CategoryDictFactory,
    TechnologyDictFactory,
    SeniorityDictFactory,
    QuestionDictFactory,
)


class TestAuthor:
    def test_author_created(self):
        self.author_data = AuthorDictFactory.build()
        self.author = Author(**self.author_data)

        assert self.author.name == self.author_data["name"]
        assert self.author.company == self.author_data["company"]


class TestCategory:
    def test_category_created(self):
        self.category_data = CategoryDictFactory.build()
        self.category = Category(**self.category_data)

        assert self.category.name == self.category_data["name"]


class TestTechnololgy:
    def test_technology_created(self):
        self.technology_data = TechnologyDictFactory.build()
        self.technology = Technology(**self.technology_data)

        assert self.technology.name == self.technology_data["name"]


class TestSeniority:
    def test_seniority_created(self):
        self.seniority_data = SeniorityDictFactory.build()
        self.seniority = Seniority(**self.seniority_data)

        assert self.seniority.level == self.seniority_data["level"]
