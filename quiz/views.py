from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.core import serializers

from quiz.models import Answer, Question, Quiz
from quiz.forms import QuizForm
from quiz.utils import template_choice

from django.contrib.sessions.models import Session


class QuizView(View):

    def get(self, request):
        form = QuizForm()
        return render(request, 'index.html', {'quiz_form': form})

    def post(self, request):
        form = QuizForm(request.POST)
        ctx = {}
        if form.is_valid():
            prog_lang = form.cleaned_data['prog_language']
            seniority = form.cleaned_data['seniority']
            user_name = form.cleaned_data['user_name']
            email = form.cleaned_data['email']
            number_of_questions = form.cleaned_data['number_of_questions']
            quiz = Quiz.objects.create(
                prog_language=prog_lang,
                seniority=seniority,
                user_name=user_name,
                email=email,
                number_of_questions=number_of_questions,
            )
            first_question = Question.objects.filter(prog_language=prog_lang, seniority=seniority).first()
            if first_question is None:
                raise Http404("Question not found.")
            ctx["prog_lang"] = prog_lang
            ctx["seniority"] = seniority
            ctx["number_of_questions"] = number_of_questions
            ctx["series"] = int(number_of_questions / 3)
            ctx["first_question_pk"] = first_question.pk
            ctx["quiz_pk"] = quiz.pk
        form = QuizForm()
        ctx["quiz_form"] = form

        return render(request, 'index.html', ctx)


class QuestionView(View):

    def get(self, request, pk):
        question = Question.objects.get(pk=pk)
        if not request.session.get("general_score"):
            request.session["general_score"] = 0
        gen_score = request.session.get("general_score")
        print(f"Actual general score: {gen_score}")
        ctx = {}
        if question:  
            answers = question.get_answers()
            ctx["question"] = question
            if question.question_type == "multiple choice":
                ctx["answers"] = list(answers)
        else:
            raise Http404("Question not found.")
        template = template_choice(question.question_type)
        return render(request, template, ctx)

    def post(self, request, pk):
        question = Question.objects.get(pk=pk)
        answers = question.get_answers()
        quiz_pk = request.GET.get("q")
        quiz = Quiz.objects.get(pk=quiz_pk)
        print(f"quiz_pk: {quiz_pk}")
        series = int(quiz.number_of_questions / 3)
        if question.question_type == "open":
            ans = answers[0].text
            user_answer = request.POST.get("ans")
            if ans == user_answer:
                gen_score = int(request.session.get("general_score"))
                gen_score += 1
                request.session["general_score"] = gen_score
        if question.question_type == "multiple choice":
            data = list(request.POST)
            data.remove('csrfmiddlewaretoken')
            data.sort()
            correct_answers_ids = [str(ans.pk) for ans in answers if ans.is_correct == True]
            correct_answers_ids.sort()
            if data == correct_answers_ids:
                gen_score = int(request.session.get("general_score"))
                gen_score += 1
                request.session["general_score"] = gen_score
        next_question_id = pk + 1
        return redirect(reverse("quiz:question-view", kwargs={'pk': next_question_id}) + f"?q={quiz_pk}")
