from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.utils.translation import activate

from quiz.models import Question, Quiz, SENIORITY_CHOICES
from quiz.forms import QuizForm
from quiz.utils import template_choice, update_score, del_session_keys, draw_questions, calculate_score_for_serie

TIMEZONES = {
    "----": "",
    "Warsaw": "Europe/Warsaw",
    "New York": "America/New_York",
}


class QuizView(View):
    def get(self, request):
        form = QuizForm()
        del_session_keys(request)
        return render(
            request, "index.html", {"quiz_form": form, "timezones": TIMEZONES}
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
        form = QuizForm(request.POST)
        if form.is_valid():
            prog_lang = form.cleaned_data["prog_language"]
            seniority = form.cleaned_data["seniority"]
            user_name = form.cleaned_data["user_name"]
            email = form.cleaned_data["email"]
            number_of_questions = form.cleaned_data["number_of_questions"]
            quiz = Quiz.objects.create(
                prog_language=prog_lang,
                seniority=seniority,
                user_name=user_name,
                email=email,
                number_of_questions=number_of_questions,
            )
            first_question = Question.objects.filter(
                prog_language=prog_lang, seniority=seniority
            ).first()
            if first_question is None:
                raise Http404("Question not found.")
            ctx["first_question_pk"] = first_question.pk
            ctx["quiz_pk"] = quiz.pk
        form = QuizForm()
        ctx["quiz_form"] = form
        ctx["timezones"] = TIMEZONES
        return render(request, "index.html", ctx)


class QuestionView(View):
    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except ObjectDoesNotExist:
            if request.session.get("general_score"):
                final_score = request.session["general_score"]
                quiz_pk = request.GET.get("q")
                quiz = Quiz.objects.get(pk=quiz_pk)
                quiz.general_score = final_score
                quiz.save()
                del_session_keys(request)
            return redirect(reverse("quiz:quiz-view"))
        if request.session.get("general_score") is None:
            request.session["general_score"] = 0
        if request.session.get("used_ids") is None:
            request.session["used_ids"] = list()
        used_ids = request.session["used_ids"]
        if pk not in used_ids:
            used_ids.append(pk)
        request.session["used_ids"] = used_ids
        ctx = {}
        answers = question.get_answers()
        ctx["question"] = question
        if question.question_type == "multiple choice":
            ctx["answers"] = list(answers)
        template = template_choice(question.question_type)
        return render(request, template, ctx)

    def post(self, request, pk):
        question = Question.objects.get(pk=pk)
        answers = question.get_answers()
        quiz_pk = request.GET.get("q")
        quiz = Quiz.objects.get(pk=quiz_pk)
        num_in_series = int(quiz.number_of_questions / len(SENIORITY_CHOICES))
        if request.session.get("num_in_series") is None:
            request.session["num_in_series"] = num_in_series - 1
        if request.session.get("seniority_level") is None:
            request.session["seniority_level"] = quiz.seniority
        if question.question_type == "open" or question.question_type == "true/false":
            ans = answers[0].text
            user_answer = request.POST.get("ans")
            if ans == user_answer:
                update_score(request, request.session["seniority_level"])
        if question.question_type == "multiple choice":
            data = list(request.POST)
            data.remove("csrfmiddlewaretoken")
            data.sort()
            correct_answers_ids = [
                str(ans.pk) for ans in answers if ans.is_correct == True
            ]
            correct_answers_ids.sort()
            if data == correct_answers_ids:
                update_score(request, request.session["seniority_level"])
        current_number = int(request.session.get("num_in_series"))
        current_number -= 1
        request.session["num_in_series"] = current_number
        next_question_pk = draw_questions(
            request.session.get("seniority_level"), used_ids=request.session["used_ids"]
        )
        if next_question_pk is None:
            # raise Http404("Question not found.")
            return redirect(reverse("quiz:quiz-view"))
        next_question = Question.objects.get(pk=next_question_pk)
        # single serie of question ends
        if request.session["num_in_series"] <= 0:
            calculate_score_for_serie(request, request.session["seniority_level"])
            request.session["seniority_level"] += 1
            if request.session["seniority_level"] > len(SENIORITY_CHOICES):
                print("Gratulacje - koniec testu!")
                return redirect(reverse("quiz:quiz-view"))
            request.session["num_in_series"] = num_in_series
            del request.session["used_ids"]
            request.session["used_ids"] = list()
            next_question_pk = draw_questions(
                request.session.get("seniority_level"),
                used_ids=request.session["used_ids"],
            )
            next_question = Question.objects.get(pk=next_question_pk)
            if next_question_pk is None:
                return redirect(reverse("quiz:quiz-view"))
                # raise Http404("Question not found.")
        return redirect(
            reverse("quiz:question-view", kwargs={"pk": next_question_pk})
            + f"?q={quiz_pk}"
        )
