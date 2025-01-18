from django.contrib import admin
from exams.models import Exam, Question, AnswerChoice, ExamApplication, Answer, Result

# Register your models here.
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_at')
    search_fields = ('title',)
    ordering = ('start_date',)

admin.site.register(Exam, ExamAdmin)

# Register Question model
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'text', 'question_type')
    search_fields = ('exam__title', 'text')
    list_filter = ('question_type',)
    ordering = ('exam',)

admin.site.register(Question, QuestionAdmin)

# Register AnswerChoice model
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    search_fields = ('question__text', 'text')
    list_filter = ('is_correct',)
    ordering = ('question__text',)  # Ordering by the question text

admin.site.register(AnswerChoice, AnswerChoiceAdmin)

# Register ExamApplication model
class ExamApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'application_date')
    search_fields = ('student__name', 'exam__title')
    ordering = ('application_date',)

admin.site.register(ExamApplication, ExamApplicationAdmin)

# Register Answer model
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('application', 'question', 'answer_text', 'answer_choice')
    search_fields = ('application__student__name', 'question__text')
    list_filter = ('answer_choice',)
    ordering = ('application',)

admin.site.register(Answer, AnswerAdmin)

# Register Result model
class ResultAdmin(admin.ModelAdmin):
    list_display = ('application', 'score', 'date_of_result')
    search_fields = ('application__student__name',)
    ordering = ('date_of_result',)

admin.site.register(Result, ResultAdmin)