from modeltranslation.translator import TranslationOptions, translator

from quiz.models import Answer, Question, Quiz


class QuestionTranslationOptions(TranslationOptions):
    fields = ('text',)


class AnswerTranslationOptions(TranslationOptions):
    fields = ('text',)


translator.register(Question, QuestionTranslationOptions)
translator.register(Answer, AnswerTranslationOptions)
