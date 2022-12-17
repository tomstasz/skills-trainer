import random

from quiz.models import Question, Quiz


def template_choice(question_type):
    if question_type == "multiple choice":
        return "single_question.html"
    if question_type == "open":
        return "single_question_open.html"
    if question_type == "true/false":
        return "boolean_question.html"


def update_score(request):
    request.session["general_score"] += 1
    current_seniority = request.session.get("seniority_level")
    if current_seniority == 1:
        request.session["junior_score"] += 1
    if current_seniority == 2:
        request.session["regular_score"] += 1
    if current_seniority == 3:
        request.session["senior_score"] += 1


def del_session_keys(request):
    if request.session.get("general_score") is not None:
        del request.session["general_score"]
    if request.session.get("num_in_series") is not None:
        del request.session["num_in_series"]
    if request.session.get("seniority_level") is not None:
        del request.session["seniority_level"]
    if request.session.get("used_ids") is not None:
        del request.session["used_ids"]
    if request.session.get("next_question_level") is not None:
        del request.session["next_question_level"]
    if request.session.get("current_get_seniority") is not None:
        del request.session["current_get_seniority"]
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


def calculate_score_for_serie(request):
    gen_score = request.session.get("general_score")
    seniority_swicher = {
        1: junior(request),
        2: regular(request),
        3: senior(request),
        None: {},
    }
    current_seniority = request.session.get("seniority_level")
    results = seniority_swicher[current_seniority]
    results["general_score"] = gen_score
    return results


def junior(request):
    return {"junior_score": request.session.get("junior_score")}


def regular(request):
    return {
        "junior_score": request.session.get("junior_score"),
        "regular_score": request.session.get("regular_score"),
    }


def senior(request):
    return {
        "senior_score": request.session.get("senior_score"),
        "junior_score": request.session.get("junior_score"),
        "regular_score": request.session.get("regular_score"),
    }


def save_results(results, quiz_pk):
    quiz = Quiz.objects.get(pk=quiz_pk)
    for key, value in results.items():
        vars(quiz)[key] = value
    quiz.save()
