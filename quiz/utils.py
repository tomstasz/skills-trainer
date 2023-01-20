import random

from django.shortcuts import get_object_or_404

from quiz.models import Question, Quiz, SENIORITY_CHOICES, Score, Technology


def template_choice(question_type):
    if question_type == "multiple choice":
        return "single_question.html"
    if question_type == "open":
        return "single_question_open.html"
    if question_type == "true/false":
        return "boolean_question.html"


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
    if request.session.get("current_num_of_questions") is not None:
        del request.session["current_num_of_questions"]
    if request.session.get("technologies") is not None:
        del request.session["technologies"]
    # if request.session.get("django_timezone") is not None:
    #     del request.session["django_timezone"]
    print("Session clear")


def del_quiz_session_data(request):
    if request.session.get("quiz_pk") is not None:
        del request.session["quiz_pk"]
    if request.session.get("selected_technologies") is not None:
        del request.session["selected_technologies"]


def draw_questions(seniority_level, categories, technology, used_ids=[]):
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
    return


def save_number_of_finished_series(score):
    num_of_finished_series = score.score_data["finished_series"]
    for k, v in SENIORITY_CHOICES:
        if num_of_finished_series[str(k)] > 0:
            score.score_data[f"number_of_{v}_series"] = num_of_finished_series[str(k)]
    return score


def set_initial_score_data(quiz):
    score_data = dict()
    score_data["general_score"] = 0
    score_data["junior_score"] = 0
    score_data["number_of_junior_series"] = 0
    score_data["regular_score"] = 0
    score_data["number_of_junior_series"] = 0
    score_data["senior_score"] = 0
    score_data["number_of_junior_series"] = 0
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

    single_serie_length = quiz.number_of_questions / len(SENIORITY_CHOICES)
    general_multiplayer = 100 / quiz.number_of_questions
    ctx = {}
    scores = quiz.score_set.all()
    for score in scores:
        tech_result = {}
        num_of_finished_series = score.score_data["finished_series"]
        for k, v in SENIORITY_CHOICES:
            multiplayer = calculate_multiplayer(
                k, num_of_finished_series, single_serie_length
            )
            points = score.score_data.get(f"{v}_score")
            serie_score = round(points * multiplayer, 1)
            num_of_questions = int(single_serie_length * num_of_finished_series[str(k)])
            # We make sure to pass only series in which user participated
            if serie_score or num_of_questions:
                tech_result[f"{v}_score"] = serie_score
                tech_result[f"{v}_questions"] = num_of_questions
                tech_result["seniority"] = score.seniority.level
        tech_result["general_score"] = round(
            score.score_data["general_score"] * general_multiplayer, 1
        )
        ctx[score.technology.name] = tech_result
    return ctx


def calculate_if_higher_seniority(score, current_seniority):
    """Calculates single serie punctation to check if certain percentage was achieved"""
    single_serie_length = score.score_data["num_in_series"]
    num_of_finished_series = score.score_data["finished_series"]
    for k, v in SENIORITY_CHOICES:
        if k == current_seniority:
            multiplayer = calculate_multiplayer(
                k, num_of_finished_series, single_serie_length
            )
            current_serie_score = score.score_data[f"{v}_score"]
    result = current_serie_score * multiplayer
    return True if result >= 66 else False


def calculate_multiplayer(key, num_of_finished_series, single_serie_length):
    """Calculates multiplayer for single serie, or for larger number of series
    if seniority was not changed (first serie result didnt meet the match)"""
    multiplayer = (
        100 / (num_of_finished_series[str(key)] * single_serie_length)
        if num_of_finished_series[str(key)] > 1
        else 100 / single_serie_length
    )
    return multiplayer


def get_question_and_score(quiz_pk, uuid):
    question = get_object_or_404(Question, uuid=uuid)
    score = Score.objects.filter(
        quiz__pk=quiz_pk, technology__pk=question.technology.pk
    ).first()
    return question, score
