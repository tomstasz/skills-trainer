import random
import threading

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.template.response import TemplateResponse
from rest_framework import viewsets

from quiz.models import Question, Quiz, SENIORITY_CHOICES, Score, Technology, Seniority
from quiz.forms import QuizForm, UserEmailForm
from quiz.utils import (
    template_choice,
    update_score,
    del_session_keys,
    del_quiz_session_data,
    draw_questions,
    is_current_pk_used,
    prepare_technologies_in_session,
    save_number_of_finished_series,
    calculate_percentage,
    calculate_if_higher_seniority,
    set_initial_score_data,
    update_finished_series_status,
    update_seniority_status,
    update_technology_status,
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
        ctx = {}
        if (
            "timezone" in request.POST
            and request.session.get("django_timezone") != request.POST.get("timezone")
            and not "email" in request.POST
        ):
            request.session["django_timezone"] = request.POST["timezone"]
            return redirect("/")
        selected_technologies = list()
        form = QuizForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data["category"]
            technology = form.cleaned_data["technology"]
            user_name = form.cleaned_data["user_name"]
            email = form.cleaned_data["email"]
            number_of_questions = form.cleaned_data["number_of_questions"]
            quiz = Quiz.objects.create(
                user_name=user_name,
                email=email,
                number_of_questions=number_of_questions,
            )
            quiz.category.set(category)
            quiz.technology.set(technology)
            for tech in list(quiz.technology.all()):
                score_data = set_initial_score_data(quiz)
                Score.objects.create(technology=tech, quiz=quiz, score_data=score_data)
                selected_technologies.append(tech.name)
            ctx["selected_technologies"] = selected_technologies
            ctx["seniority_levels"] = SENIORITY_CHOICES
            request.session["quiz_pk"] = quiz.pk
            request.session["selected_technologies"] = selected_technologies
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
            first_question_technology = random.choice(list(quiz.technology.all()))
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
        elif request.POST and not "email" in request.POST:
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
        question = get_object_or_404(Question, uuid=uuid)
        if request.session.get("current_technology") is None:
            request.session["current_technology"] = question.technology.pk
        score = Score.objects.filter(
            quiz__pk=quiz_pk, technology__pk=request.session["current_technology"]
        ).first()
        if not is_current_pk_used(quiz_pk, question.pk):
            score.score_data["used_ids"].append(question.pk)
            score.score_data["seniority_level"] = question.seniority.level
        else:  # scenario in which original quiz link was used more than once or browser buttons were pushed (current question.pk already in base)
            current_seniority = score.score_data["seniority_level"]
            prepare_technologies_in_session(request, score)
            if (
                len(score.score_data["used_ids"]) % score.score_data["num_in_series"]
                == 0
            ):  # single serie of questions ends
                update_finished_series_status(score, current_seniority)
                update_seniority_status(score, current_seniority)
                score, quiz_finished = update_technology_status(request, score, quiz_pk)
                if quiz_finished:
                    return redirect(reverse("quiz:quiz-view"))
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
        if question.question_type == "multiple choice":
            ctx["answers"] = list(answers)
        template = template_choice(question.question_type)
        response = TemplateResponse(request, template, ctx)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    def post(self, request, uuid):
        quiz_pk = request.GET.get("q")
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
            correct_answers_ids = [
                str(ans.pk) for ans in answers if ans.is_correct == True
            ]
            correct_answers_ids.sort()
            if data == correct_answers_ids:
                score = update_score(score)
        if (
            len(score.score_data["used_ids"]) % score.score_data["num_in_series"] == 0
        ):  # single serie of questions ends
            current_seniority = score.score_data["seniority_level"]
            update_finished_series_status(score, current_seniority)
            seniority_change_flag = calculate_if_higher_seniority(
                score, current_seniority
            )
            update_seniority_status(score, current_seniority, seniority_change_flag)
            score, quiz_finished = update_technology_status(request, score, quiz_pk)
            if quiz_finished:
                return redirect(reverse("quiz:quiz-view"))
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


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class ResultFormView(View):
    def get(self, request):
        form = UserEmailForm()
        return render(request, "results.html", {"quiz_form": form})

    def post(self, request):
        form = UserEmailForm()
        ctx = {}
        if "email" in request.POST:
            quiz = Quiz.objects.filter(email=request.POST["email"]).first()
            ctx["results"] = calculate_percentage(quiz)
            ctx["quiz"] = quiz
        ctx["quiz_form"] = form
        return render(request, "results.html", ctx)
