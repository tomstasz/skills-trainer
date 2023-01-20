import random
import threading

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from rest_framework import viewsets

from quiz.models import Question, Quiz, SENIORITY_CHOICES, Score, Technology, Seniority
from quiz.forms import QuizForm, UserEmailForm
from quiz.utils import (
    template_choice,
    update_score,
    del_session_keys,
    del_quiz_session_data,
    draw_questions,
    save_number_of_finished_series,
    calculate_percentage,
    calculate_if_higher_seniority,
    set_initial_score_data,
    get_question_and_score,
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
        question, score = get_question_and_score(quiz_pk, uuid)
        if question.pk not in score.score_data["used_ids"]:
            score.score_data["used_ids"].append(question.pk)
            score.score_data["seniority_level"] = question.seniority.level
        else:
            print("USED PK")
        score.save()
        ctx = {}
        answers = question.get_answers()
        ctx["question"] = question
        ctx["time"] = question.time
        if question.question_type == "multiple choice":
            ctx["answers"] = list(answers)
        template = template_choice(question.question_type)
        return render(request, template, ctx)

    def post(self, request, uuid):
        quiz_pk = request.GET.get("q")
        question, score = get_question_and_score(quiz_pk, uuid)
        answers = question.get_answers()
        if request.session.get("current_num_of_questions") is None:
            request.session["current_num_of_questions"] = score.score_data[
                "max_num_of_questions"
            ]
            request.session["technologies"] = [
                technology for technology in score.score_data["technologies"]
            ]
        # different question types check
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
        request.session["current_num_of_questions"] -= 1
        if (
            len(score.score_data["used_ids"]) % score.score_data["num_in_series"] == 0
        ):  # single serie of questions ends
            current_seniority = score.score_data["seniority_level"]
            current_technology = score.technology.pk
            score.score_data["finished_series"][str(current_seniority)] += 1
            save_number_of_finished_series(score)
            seniority_change_flag = calculate_if_higher_seniority(
                score, current_seniority
            )
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
            if (  # Downgrade seniority
                not seniority_change_flag and current_seniority != 1
            ):
                score.score_data["seniority_level"] -= 1
            if (  # Technology is finished
                score.score_data["max_num_of_questions"]
                - len(score.score_data["used_ids"])
                <= 0
            ):
                score.save()
                request.session["technologies"].remove(current_technology)
                if len(request.session["technologies"]) == 0:  #  Quiz is finished
                    return redirect(reverse("quiz:quiz-view"))
                else:
                    next_tech_in_list = request.session["technologies"][
                        0
                    ]  # We take next technology in list
                    score = Score.objects.filter(
                        quiz__pk=quiz_pk, technology__pk=next_tech_in_list
                    ).first()
                    score.score_data["seniority_level"] = score.seniority.level
                    request.session["current_num_of_questions"] = score.score_data[
                        "max_num_of_questions"
                    ]
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
