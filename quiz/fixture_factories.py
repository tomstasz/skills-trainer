from datetime import datetime
import factory

from factory.fuzzy import FuzzyText, FuzzyInteger, FuzzyChoice

from quiz.models import Question


SCORE_DATA = {
    "general_score": 5,
    "junior_score": 0,
    "number_of_junior_series": 0,
    "regular_score": 4,
    "number_of_regular_series": 2,
    "senior_score": 1,
    "number_of_senior_series": 1,
    "used_ids": [11, 3, 5, 29, 9, 28, 26, 27, 19],
    "seniority_level": 2,
    "num_in_series": 3,
    "max_num_of_questions": 9,
    "categories": [1, 2],
    "technologies": [1, 2, 4],
    "finished_series": {"1": 0, "2": 2, "3": 1},
}


class CategoryDictFactory(factory.DictFactory):
    name = FuzzyText(length=10)


class TechnologyDictFactory(factory.DictFactory):
    name = FuzzyText(length=10)


class SeniorityDictFactory(factory.DictFactory):
    level = FuzzyChoice([1, 2, 3])


class AuthorDictFactory(factory.DictFactory):
    name = factory.Faker("name")
    company = FuzzyText(length=30)


class QuestionDictFactory(factory.DictFactory):
    text = FuzzyText(length=100)
    uuid = factory.Faker("uuid4")
    question_type = FuzzyChoice(["multiple choice", "open", "true/false"])
    category = factory.SubFactory(CategoryDictFactory)
    technology = factory.SubFactory(TechnologyDictFactory)
    seniority = factory.SubFactory(SeniorityDictFactory)
    author = factory.SubFactory(AuthorDictFactory)
    time = FuzzyInteger(0, 30)
    created_at = factory.LazyFunction(datetime.now)


class AnswerDictFactory(factory.DictFactory):
    text = FuzzyText(length=20)
    is_correct = FuzzyChoice([True, False])
    question = factory.SubFactory(QuestionDictFactory)
    created_at = factory.LazyFunction(datetime.now)


class QuizDictFactory(factory.DictFactory):
    uuid = factory.Faker("uuid4")
    category = factory.SubFactory(CategoryDictFactory)
    technology = factory.SubFactory(TechnologyDictFactory)
    user_name = factory.Faker("name")
    email = factory.Faker("email")
    number_of_questions = FuzzyChoice([9])
    created_at = factory.LazyFunction(datetime.now)
    mode = FuzzyChoice(["recruitment", "training"])


class ScoreDictFactory(factory.DictFactory):
    quiz = factory.SubFactory(QuizDictFactory)
    seniority = factory.SubFactory(SeniorityDictFactory)
    score_data = SCORE_DATA
