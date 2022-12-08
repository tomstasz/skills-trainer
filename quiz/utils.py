def template_choice(question_type):
    if question_type == "multiple choice":
        return 'single_question.html'
    if question_type == "open":
        return 'single_question_open.html'
