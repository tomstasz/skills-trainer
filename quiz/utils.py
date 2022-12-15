import random

from quiz.models import Question


def template_choice(question_type):
    if question_type == "multiple choice":
        return "single_question.html"
    if question_type == "open":
        return "single_question_open.html"
    if question_type == "true/false":
        return "boolean_question.html"


def update_score(request, seniority_level):
    # gen_score = int(request.session.get("general_score"))
    # gen_score += 1
    request.session["general_score"] += 1
    # if request.session.get(seniority_level) is not None:
    #     request.session[seniority_level] += 1



def del_session_keys(request):
    if request.session.get("general_score") is not None:
        del request.session["general_score"]
    if request.session.get("num_in_series") is not None:
        del request.session["num_in_series"]
    if request.session.get("seniority_level") is not None:
        del request.session["seniority_level"]
    if request.session.get("used_ids") is not None:
        del request.session["used_ids"]
    # if request.session.get("django_timezone") is not None:
    #     del request.session["django_timezone"]
    print("Session clear")


def draw_questions(seniority_level, used_ids):
    ids = list(
        Question.objects.filter(seniority=seniority_level)
        .exclude(id__in=used_ids)
        .values_list("pk", flat=True)
    )
    if not ids:
        return
    random.shuffle(ids)
    if len(ids) > 0:
        return ids[0]
    return

def calculate_score_for_serie(request, seniority):
    pass