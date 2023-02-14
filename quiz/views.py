import json
import secrets

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.template.response import TemplateResponse
from rest_framework import viewsets

from quiz.models import Question, Quiz, SENIORITY_CHOICES, Score, Seniority
from quiz.forms import QuizForm, UserEmailForm, QuestionSearchForm
from quiz.utils import (
    template_choice,
    update_score,
    del_session_keys,
    del_quiz_session_data,
    draw_questions,
    is_current_pk_used,
    is_max_questions_in_score_used,
    is_max_series_in_score_used,
    prepare_technologies_in_session,
    calculate_percentage,
    calculate_if_higher_seniority,
    set_initial_score_data,
    update_finished_series_status,
    update_seniority_status,
    update_technology_status,
    no_cache_response,
)
from quiz.serializers import QuizSerializer

TIMEZONES = {
    "----": "",
    _("Warsaw"): "Europe/Warsaw",
    _("New York"): "America/New_York",
}

MAX_SENIORITY_LEVEL = len(SENIORITY_CHOICES)


class QuizView(View):
    def get(self, request):
        form = QuizForm()
        del_session_keys(request)
        return render(
            request,
            "index.html",
            {
                "quiz_form": form,
                "timezones": TIMEZONES,
                "seniority_levels": SENIORITY_CHOICES,
            },
        )

    def post(self, request):
        ctx = dict()
        if (
            "timezone" in request.POST
            and request.session.get("django_timezone") != request.POST.get("timezone")
            and "email" not in request.POST
        ):
            request.session["django_timezone"] = request.POST["timezone"]
            return redirect("/")
        selected_technologies = list()
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            for tech in list(quiz.technology.all()):
                score_data = set_initial_score_data(quiz)
                Score.objects.create(technology=tech, quiz=quiz, score_data=score_data)
                selected_technologies.append(tech.name)
            ctx["selected_technologies"] = selected_technologies
            ctx["seniority_levels"] = SENIORITY_CHOICES
            request.session["quiz_pk"] = quiz.pk
            request.session["selected_technologies"] = selected_technologies
        else:
            ctx["quiz_form_err"] = form

        if (
            "tech-submit" in request.POST
            and all(  # check if seniority is set for all chosen technologies
                [
                    i in request.POST.keys()
                    for i in request.session["selected_technologies"]
                ]
            )
        ):
            quiz = get_object_or_404(Quiz, pk=request.session.get("quiz_pk"))
            for technology in quiz.technology.all():
                if request.POST.get(technology.name):
                    score = Score.objects.filter(
                        quiz__pk=quiz.pk, technology__pk=technology.pk
                    ).first()
                    seniority = Seniority.objects.get(
                        level=request.POST[technology.name]
                    )
                    score.seniority = seniority
                    score.score_data["seniority_level"] = seniority.level
                    score.save()
            first_question_technology = secrets.choice(list(quiz.technology.all()))
            first_question_seniority = quiz.score_set.get(
                technology=first_question_technology.pk
            ).seniority.level
            first_question_pk = draw_questions(
                first_question_seniority,
                list(quiz.category.all()),
                first_question_technology.pk,
            )
            first_question = get_object_or_404(Question, pk=first_question_pk)
            ctx["first_question_uuid"] = first_question.uuid
            ctx["quiz_pk"] = quiz.pk
            del_quiz_session_data(request)
        elif request.POST and "email" not in request.POST:
            ctx["message"] = _(
                """Quiz will not be generated without setting seniority levels.
                                Please try to fill the fields again."""
            )
            quiz = get_object_or_404(Quiz, pk=request.session.get("quiz_pk"))
            quiz.delete()
            print("Quiz DELETED")
            del_quiz_session_data(request)
        form = QuizForm()
        ctx["quiz_form"] = form
        ctx["timezones"] = TIMEZONES
        return render(request, "index.html", ctx)


class QuestionView(View):
    def get(self, request, uuid):
        quiz_pk = request.GET.get("q")
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        question = get_object_or_404(Question, uuid=uuid)
        if request.session.get("current_technology") is None:
            request.session["current_technology"] = question.technology.pk
        score = Score.objects.filter(
            quiz__pk=quiz_pk, technology__pk=request.session["current_technology"]
        ).first()
        prepare_technologies_in_session(request, score)
        if not is_current_pk_used(
            quiz, question.pk
        ) and not is_max_questions_in_score_used(score):
            score.score_data["used_ids"].append(question.pk)
            score.score_data["seniority_level"] = question.seniority.level
        else:  # scenario in which original quiz link was used more than once or browser buttons were pushed
            current_seniority = score.score_data["seniority_level"]
            if (
                len(score.score_data["used_ids"]) % score.score_data["num_in_series"]
                == 0
            ):  # single series of questions ends
                if not is_max_series_in_score_used(score):
                    update_finished_series_status(score, current_seniority)
                    seniority_change_flag = calculate_if_higher_seniority(
                        score, current_seniority
                    )
                    update_seniority_status(
                        score, current_seniority, seniority_change_flag
                    )
                score, is_quiz_finished = update_technology_status(
                    request, score, quiz_pk
                )
                if is_quiz_finished:
                    quiz_uuid = quiz.uuid
                    return redirect(
                        reverse("quiz:training-view", kwargs={"uuid": quiz_uuid})
                    )
            next_question_pk = draw_questions(
                seniority_level=score.score_data["seniority_level"],
                categories=score.score_data["categories"],
                technology=score.technology.pk,
                used_ids=score.score_data["used_ids"],
            )
            next_question = get_object_or_404(Question, pk=next_question_pk)
            score.save()
            return redirect(
                reverse("quiz:question-view", kwargs={"uuid": next_question.uuid})
                + f"?q={quiz_pk}"
            )
        score.save()
        ctx = {}
        answers = question.get_answers()
        ctx["question"] = question
        ctx["time"] = question.time
        ctx["quiz"] = quiz
        if question.question_type == "multiple choice":
            ctx["answers"] = list(answers)
        template = template_choice(question.question_type)
        response = TemplateResponse(request, template, ctx)
        response = no_cache_response(response)
        return response

    def post(self, request, uuid):
        quiz_pk = request.GET.get("q")
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        question = get_object_or_404(Question, uuid=uuid)
        score = Score.objects.filter(
            quiz__pk=quiz_pk, technology__pk=request.session["current_technology"]
        ).first()
        answers = question.get_answers()
        prepare_technologies_in_session(request, score)
        if question.question_type == "open" or question.question_type == "true/false":
            ans = strip_tags(answers[0].text)
            user_answer = request.POST.get("ans")
            if ans == user_answer:
                score = update_score(score)
        if question.question_type == "multiple choice":
            data = list(request.POST)
            data.remove("csrfmiddlewaretoken")
            data.sort()
            correct_answers_ids = [str(ans.pk) for ans in answers if ans.is_correct]
            correct_answers_ids.sort()
            if data == correct_answers_ids:
                score = update_score(score)
        continue_submit = request.POST.get("continue-submit")
        is_quiz_finished = False
        if (
            len(score.score_data["used_ids"]) % score.score_data["num_in_series"] == 0
            and continue_submit is None
        ):  # single series of questions ends
            current_seniority = score.score_data["seniority_level"]
            if not is_max_series_in_score_used(score):
                update_finished_series_status(score, current_seniority)
                seniority_change_flag = calculate_if_higher_seniority(
                    score, current_seniority
                )
                update_seniority_status(score, current_seniority, seniority_change_flag)
            score, is_quiz_finished = update_technology_status(request, score, quiz_pk)
        score.save()
        if not is_quiz_finished:
            next_question_pk = draw_questions(
                seniority_level=score.score_data["seniority_level"],
                categories=score.score_data["categories"],
                technology=score.technology.pk,
                used_ids=score.score_data["used_ids"],
            )
            next_question = get_object_or_404(Question, pk=next_question_pk)
            next_uuid = next_question.uuid
        else:
            next_uuid = None
        if (
            quiz.mode == "training" and continue_submit is None
        ):  # continue_submit: button leading to next question
            ctx = dict()
            ctx["question"] = question
            ctx["time"] = question.time
            ctx["quiz"] = quiz
            ctx["answers"] = answers
            ctx["correct_answers"] = [answer for answer in answers if answer.is_correct]
            ctx["next_uuid"] = next_uuid
            if question.question_type == "multiple choice":
                ctx["answers"] = list(answers)
            template = template_choice(question.question_type)
            response = TemplateResponse(request, template, ctx)
            response = no_cache_response(response)
            return response
        else:
            if is_quiz_finished:
                quiz_uuid = quiz.uuid
                return redirect(
                    reverse("quiz:training-view", kwargs={"uuid": quiz_uuid})
                )
            return redirect(
                reverse("quiz:question-view", kwargs={"uuid": next_uuid})
                + f"?q={quiz_pk}"
            )


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class ResultFormView(View):
    """View rendering results charts for recruiters"""

    def get(self, request):
        form = UserEmailForm()
        return render(request, "results.html", {"quiz_form": form})

    def post(self, request):
        form = UserEmailForm()
        ctx = dict()
        if "email" in request.POST:
            quiz = Quiz.objects.filter(email=request.POST["email"]).first()
            ctx["results"] = calculate_percentage(quiz)
            ctx["quiz"] = quiz
            json_object = json.dumps(calculate_percentage(quiz), indent=4)
            ctx["json_obj"] = json_object
        ctx["quiz_form"] = form
        return render(request, "results.html", ctx)


@require_http_methods(["GET", "POST"])
def single_result_view(request, uuid):
    """View rendering results charts for user"""
    quiz = get_object_or_404(Quiz, uuid=uuid)
    ctx = dict()
    if quiz.mode == "training":
        request.session["training"] = True
    if request.session.get("training"):
        ctx["training"] = True
    ctx["results"] = calculate_percentage(quiz)
    ctx["quiz"] = quiz
    json_object = json.dumps(calculate_percentage(quiz), indent=4)
    ctx["json_obj"] = json_object
    return render(request, "single_result.html", ctx)


class QuestionSearchView(View):
    def get(self, request):
        form = QuestionSearchForm()
        return render(request, "question-search.html", {"question_form": form})

    def post(self, request):
        form = QuestionSearchForm(request.POST)
        ctx = dict()
        if form.is_valid():
            pk = form.cleaned_data["id"] if form.cleaned_data["id"] else None
            uuid = form.cleaned_data["uuid"] if form.cleaned_data["uuid"] else None
            question = Question.objects.filter(Q(id=pk) | Q(uuid=uuid)).first()
            answers = question.get_answers() if question else None
            ctx["question"] = question
            ctx["answers"] = answers
            if question is not None and question.question_type == "multiple choice":
                ctx["answers"] = list(answers)
            ctx["question_form"] = form

        return render(request, "question-search.html", ctx)
