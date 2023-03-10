import copy

from django.test import RequestFactory

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
    calculate_percentage,
    calculate_if_higher_seniority,
    calculate_multiplayer,
    update_finished_series_status,
    update_seniority_status,
    update_technology_status,
    is_current_pk_used,
    is_max_questions_in_score_used,
    is_max_series_in_score_used,
)
from quiz.fixture_factories import SCORE_DATA
from quiz.tests.mixins import TestUtilMixin

QUESTION_TYPES = ("open", "multiple choice", "true/false")


class TestUtils(TestUtilMixin):
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

    def test_number_of_finished_series(self):
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
        expected_results = (
            "single_question_open.html",
            "single_question.html",
            "boolean_question.html",
        )
        for question_type, expected_result in zip(QUESTION_TYPES, expected_results):
            template = template_choice(question_type)
            assert template == expected_result

    def test_update_score(self):
        score = update_score(self.null_score)

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
        self.question.question_type = QUESTION_TYPES[2]
        post_request = RequestFactory().post(
            path=self.url,
            data={"ans": self.answer[0].text, "csrfmiddlewaretoken": "xxx"},
        )
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, self.null_score
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
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, self.null_score
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
        self.question.question_type = QUESTION_TYPES[1]
        self.answer[0].is_correct = True
        post_request = RequestFactory().post(
            path=self.url,
            data={
                f"{self.answer[0].pk}": self.answer[0].text,
                "csrfmiddlewaretoken": "xxx",
            },
        )
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, self.null_score
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
        self.question.question_type = QUESTION_TYPES[2]
        post_request = RequestFactory().post(
            path=self.url, data={"ans": "wrong answer", "csrfmiddlewaretoken": "xxx"}
        )
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, self.null_score
        )

        assert score.score_data["general_score"] == 0
        assert score.score_data["junior_score"] == 0
        assert score.score_data["regular_score"] == 0
        assert score.score_data["senior_score"] == 0

    def test_check_question_type_to_update_score__not_changes_score_when_answer_is_wrong_and_question_is_multichoice_type(
        self,
    ):
        self.question.question_type = QUESTION_TYPES[1]
        post_request = RequestFactory().post(
            path=self.url,
            data={f"wrong pk": "wrong answer", "csrfmiddlewaretoken": "xxx"},
        )
        score = check_question_type_to_update_score(
            post_request, self.question, self.answer, self.null_score
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

    def test_calculate_percentage(self):
        ctx = calculate_percentage(self.quiz)

        expected_result = {
            self.score.technology.name: {
                "general_score": 55.6,
                "regular_score": 66.7,
                "senior_score": 33.3,
                "regular_questions": SCORE_DATA["number_of_regular_series"]
                * self.single_serie,
                "senior_questions": SCORE_DATA["number_of_senior_series"]
                * self.single_serie,
                "seniority": self.seniority.level,
            },
            self.next_score.technology.name: {
                "general_score": 55.6,
                "regular_score": 66.7,
                "senior_score": 33.3,
                "regular_questions": SCORE_DATA["number_of_regular_series"]
                * self.single_serie,
                "senior_questions": SCORE_DATA["number_of_senior_series"]
                * self.single_serie,
                "seniority": self.seniority.level,
            },
        }

        assert "junior_score" not in ctx[self.score.technology.name].keys()
        assert ctx == expected_result

    def test_calculate_multiplayer__if_num_of_finished_series_is_more_than_one(self):
        expected_result = 100 / (
            self.score.score_data["finished_series"]["2"] * self.single_serie
        )

        multiplayer = calculate_multiplayer(
            2, self.score.score_data["finished_series"], self.single_serie
        )

        assert multiplayer == expected_result

    def test_calculate_multiplayer__if_num_of_finished_series_is_equal_one(self):
        expected_result = 100 / self.single_serie

        multiplayer = calculate_multiplayer(
            3, self.score.score_data["finished_series"], self.single_serie
        )

        assert multiplayer == expected_result

    def test_calculate_if_higher_seniority__when_result_high(self):
        result = calculate_if_higher_seniority(self.score, 2)

        assert result == True

    def test_calculate_if_higher_seniority__when_result_too_low(self):
        result = calculate_if_higher_seniority(self.score, 3)

        assert result == False

    def test_update_finished_series_status(self):
        expected_result = {"1": 2, "2": 1, "3": 0}
        update_finished_series_status(self.null_score, 1)
        update_finished_series_status(self.null_score, 2)
        update_finished_series_status(self.null_score, 1)

        assert self.null_score.score_data["finished_series"] == expected_result

    def test_if_update_seniority_status__upgrade_seniority(self):
        update_finished_series_status(self.null_score, 1)
        update_seniority_status(self.null_score, 1, seniority_change_flag=True)

        assert self.null_score.score_data["seniority_level"] == 2

    def test_if_update_seniority_status__downgrade_seniority(self):
        self.null_score.score_data["seniority_level"] = 2
        update_seniority_status(self.null_score, 2, seniority_change_flag=False)

        assert self.null_score.score_data["seniority_level"] == 1

    def test_if_update_seniority_status__keep_current_seniority(self):
        update_finished_series_status(self.null_score, 1)
        update_finished_series_status(self.null_score, 2)
        self.null_score.score_data["seniority_level"] = 1
        update_seniority_status(self.null_score, 1, seniority_change_flag=True)

        assert self.null_score.score_data["seniority_level"] == 1

    def test_if_update_technology_status__change_technology(self):
        session = self.request.session
        session["technologies"] = [
            self.score.technology.pk,
            self.next_score.technology.pk,
        ]
        score, is_quiz_finished = update_technology_status(
            self.request, self.score, self.quiz.pk
        )

        assert self.score.technology.pk not in session["technologies"]
        assert is_quiz_finished == False
        assert len(session["technologies"]) == 1
        assert session["current_technology"] == self.next_score.technology.pk
        assert score.technology.pk == self.next_score.technology.pk

    def test_if_update_technology_status__not_remove_technology_when_no_current_tech_in_session(
        self,
    ):
        session = self.request.session
        session["technologies"] = [self.next_score.technology.pk]
        score, is_quiz_finished = update_technology_status(
            self.request, self.score, self.quiz.pk
        )

        assert len(session["technologies"]) == 1
        assert is_quiz_finished == False

    def test_if_update_technology_status__not_change_tech_and_finish_quiz(self):
        session = self.request.session
        session["technologies"] = [self.score.technology.pk]
        score, is_quiz_finished = update_technology_status(
            self.request, self.score, self.quiz.pk
        )

        assert len(session["technologies"]) == 0
        assert is_quiz_finished == True
        assert "current_technology" not in session.keys()
        assert score.technology.pk == self.score.technology.pk

    def test_if_update_technology_status__not_change_tech_if_used_ids_not_full(self):
        session = self.request.session
        session["technologies"] = [
            self.score.technology.pk,
            self.next_score.technology.pk,
        ]
        self.score.score_data["used_ids"] = []
        score, is_quiz_finished = update_technology_status(
            self.request, self.score, self.quiz.pk
        )

        assert len(session["technologies"]) == 2
        assert is_quiz_finished == False
        assert "current_technology" not in session.keys()
        assert score.technology.pk == self.score.technology.pk

    def test_is_current_pk_used__when_pk_used(self):
        self.score.score_data["used_ids"].append(29)
        self.score.save()
        result = is_current_pk_used(self.quiz, 29)

        assert result == True

    def test_is_current_pk_used__when_pk_not_used(self):
        result = is_current_pk_used(self.quiz, 9999999)

        assert result == False

    def test_is_max_questions_in_score_used__when_used_ids_is_not_full(self):
        assert (
            len(self.score.score_data["used_ids"]) < self.score.quiz.number_of_questions
        )
        result = is_max_questions_in_score_used(self.score)

        assert result == False

    def test_is_max_questions_in_score_used__when_used_ids_is_full(self):
        self.score.score_data["used_ids"] += [1, 2, 3, 4, 5, 6, 7, 8]
        assert (
            len(self.score.score_data["used_ids"])
            == self.score.quiz.number_of_questions
        )
        result = is_max_questions_in_score_used(self.score)

        assert result == True

    def test_is_max_series_in_score_used__when_all_series_used(self):
        result = is_max_series_in_score_used(self.score)

        assert result == True

    def test_is_max_series_in_score_used__when_not_all_series_used(self):
        result = is_max_series_in_score_used(self.null_score)

        assert result == False
