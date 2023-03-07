import random

from django.utils.html import strip_tags
from quiz.models import Question, SENIORITY_CHOICES, Score


MAX_SENIORITY_LEVEL = len(SENIORITY_CHOICES)
MULTIPLE_CHOICE = "multiple choice"


def template_choice(question_type):
    if question_type == "multiple choice":
        return "single_question.html"
    if question_type == "open":
        return "single_question_open.html"
    if question_type == "true/false":
        return "boolean_question.html"


def check_question_type_to_update_score(request, question, answers, score):
    if question.question_type == "open" or question.question_type == "true/false":
        ans = strip_tags(answers[0].text)
        user_answer = request.POST.get("ans")
        if ans == user_answer:
            score = update_score(score)
    if question.question_type == MULTIPLE_CHOICE:
        data = list(request.POST)
        data.remove("csrfmiddlewaretoken")
        data.sort()
        correct_answers_ids = [str(ans.pk) for ans in answers if ans.is_correct]
        correct_answers_ids.sort()
        if data == correct_answers_ids:
            score = update_score(score)
    return score


def update_score(score):
    score.score_data["general_score"] += 1
    current_seniority = score.score_data["seniority_level"]
    if current_seniority == 1:
        score.score_data["junior_score"] += 1
    if current_seniority == 2:
        score.score_data["regular_score"] += 1
    if current_seniority == 3:
        score.score_data["senior_score"] += 1
    return score


def del_session_keys(request):
    """Utility function cleaning session keys
    for local testing purposes"""
    if request.session.get("technologies") is not None:
        del request.session["technologies"]
    if request.session.get("current_technology") is not None:
        del request.session["current_technology"]
    if request.session.get("training") is not None:
        del request.session["training"]
    print("Session clear")


def del_quiz_session_data(request):
    if request.session.get("quiz_pk") is not None:
        del request.session["quiz_pk"]
    if request.session.get("selected_technologies") is not None:
        del request.session["selected_technologies"]


def draw_questions(seniority_level, categories, technology, used_ids=None):
    if used_ids is None:
        used_ids = list()
    ids = list(
        Question.objects.filter(
            seniority=seniority_level, category__in=categories, technology=technology
        )
        .exclude(id__in=used_ids)
        .values_list("pk", flat=True)
    )
    if not ids:
        return
    random.shuffle(ids)
    if len(ids) > 0:
        return ids[0]


def save_number_of_finished_series(score):
    """Saves each number of finished series under separate key in score json field"""
    num_of_finished_series = score.score_data["finished_series"]
    for k, v in SENIORITY_CHOICES:
        if num_of_finished_series[str(k)] > 0:
            score.score_data[f"number_of_{v}_series"] = num_of_finished_series[str(k)]
    score.save()
    return score


def set_initial_score_data(quiz):
    score_data = dict()
    score_data["general_score"] = 0
    score_data["junior_score"] = 0
    score_data["number_of_junior_series"] = 0
    score_data["regular_score"] = 0
    score_data["number_of_regular_series"] = 0
    score_data["senior_score"] = 0
    score_data["number_of_senior_series"] = 0
    score_data["used_ids"] = []
    score_data["seniority_level"] = 0
    score_data["num_in_series"] = int(quiz.number_of_questions / len(SENIORITY_CHOICES))
    score_data["max_num_of_questions"] = quiz.number_of_questions
    score_data["categories"] = [category.pk for category in quiz.category.all()]
    score_data["technologies"] = [technology.pk for technology in quiz.technology.all()]
    score_data["finished_series"] = {1: 0, 2: 0, 3: 0}

    return score_data


def calculate_percentage(quiz):
    """Calculate percentage of correct answers
    taking into account number of finished series
    from each seniority level in each technology"""

    single_series_length = quiz.number_of_questions / len(SENIORITY_CHOICES)
    general_multiplayer = 100 / quiz.number_of_questions
    ctx = {}
    scores = quiz.score_set.all()
    for score in scores:
        tech_result = {}
        num_of_finished_series = score.score_data["finished_series"]
        for k, v in SENIORITY_CHOICES:
            multiplayer = calculate_multiplayer(
                k, num_of_finished_series, single_series_length
            )
            points = score.score_data.get(f"{v}_score")
            series_score = round(points * multiplayer, 1)
            num_of_questions = int(
                single_series_length * num_of_finished_series[str(k)]
            )
            # We make sure to pass only series in which user participated
            if series_score or num_of_questions:
                tech_result[f"{v}_score"] = series_score
                tech_result[f"{v}_questions"] = num_of_questions
                tech_result["seniority"] = score.seniority.level
        tech_result["general_score"] = round(
            score.score_data["general_score"] * general_multiplayer, 1
        )
        ctx[score.technology.name] = tech_result
    return ctx


def calculate_if_higher_seniority(score, current_seniority):
    """Calculates single series punctation to check if certain percentage was achieved"""
    single_series_length = score.score_data["num_in_series"]
    num_of_finished_series = score.score_data["finished_series"]
    current_series_score = 0
    multiplayer = 0
    for k, v in SENIORITY_CHOICES:
        if k == current_seniority:
            multiplayer = calculate_multiplayer(
                k, num_of_finished_series, single_series_length
            )
            current_series_score = score.score_data[f"{v}_score"]
    result = current_series_score * multiplayer
    return True if result >= 66 else False


def calculate_multiplayer(key, num_of_finished_series, single_series_length):
    """Calculates multiplayer for single series, or for larger number of series
    if seniority was not changed (first series result didn't meet the match)"""
    multiplayer = (
        100 / (num_of_finished_series[str(key)] * single_series_length)
        if num_of_finished_series[str(key)] > 1
        else 100 / single_series_length
    )
    return multiplayer


def prepare_technologies_in_session(request, score):
    if request.session.get("technologies") is None:
        request.session["technologies"] = [
            technology for technology in score.score_data["technologies"]
        ]


def update_finished_series_status(score, current_seniority):
    """Updates current number of finished series from each level"""
    score.score_data["finished_series"][str(current_seniority)] += 1
    save_number_of_finished_series(score)
    return score


def update_seniority_status(score, current_seniority, seniority_change_flag=False):
    """Increases or decreases seniority level based on certain conditions"""
    current_seniority_finished_series = score.score_data["finished_series"][
        str(current_seniority)
    ]
    higher_seniority_finished_series = (
        score.score_data["finished_series"][str(current_seniority + 1)]
        if current_seniority != MAX_SENIORITY_LEVEL
        else 0
    )
    if (  # Upgrade seniority
        seniority_change_flag
        and current_seniority != MAX_SENIORITY_LEVEL
        and current_seniority_finished_series == 1
        and higher_seniority_finished_series == 0
    ):
        score.score_data["seniority_level"] += 1
    if not seniority_change_flag and current_seniority != 1:  # Downgrade seniority
        score.score_data["seniority_level"] -= 1
    return score


def update_technology_status(request, score, quiz_pk):
    """Switches to another technology or finishes quiz"""
    is_quiz_finished = False
    if (  # Technology is finished
        score.score_data["max_num_of_questions"] - len(score.score_data["used_ids"])
        <= 0
    ):
        current_technology = score.technology.pk
        score.save()
        if current_technology in request.session["technologies"]:
            request.session["technologies"].remove(current_technology)
        if len(request.session["technologies"]) == 0:  # Quiz is finished
            is_quiz_finished = True
        else:
            next_tech_in_list = request.session["technologies"][
                0
            ]  # We take next technology in list
            score = Score.objects.filter(
                quiz__pk=quiz_pk, technology__pk=next_tech_in_list
            ).first()
            request.session["current_technology"] = next_tech_in_list
            score.score_data["seniority_level"] = score.seniority.level
            score.save()
    return score, is_quiz_finished


def is_current_pk_used(quiz, question_pk):
    found_pk = False
    for score in quiz.score_set.all():
        if question_pk in score.score_data["used_ids"]:
            found_pk = True
    return found_pk


def is_max_questions_in_score_used(score):
    return (
        True
        if len(score.score_data["used_ids"]) == score.score_data["max_num_of_questions"]
        else False
    )


def is_max_series_in_score_used(score):
    used_series = sum(score.score_data["finished_series"].values())
    return True if len(SENIORITY_CHOICES) == used_series else False


def no_cache_response(response):  # pragma: no cover
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
