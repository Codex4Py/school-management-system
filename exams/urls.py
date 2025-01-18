from django.urls import path
from . import views

urlpatterns = [
    # Class-related URLs
    path('add-class/', views.add_class, name='add_class'),
    path('class/edit/<int:class_id>/', views.edit_class, name='edit_class'),
    path('classes/', views.class_list, name='class_list'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/delete/<int:class_id>/', views.delete_class, name='delete_class'),


    # Exam-related URLs
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:exam_id>/take/', views.exam_take, name='exam_take'),
    path('exams/<int:exam_id>/add_question/', views.add_question, name='add_question'),

    # Schedule-related URLs
    path('schedule-exam/', views.schedule_exam, name='schedule_exam'),
    path('schedules/', views.class_schedule_list, name='schedule_list'),
    path('create-schedule/', views.create_class_schedule, name='create_schedule'),
    path('schedule/<int:schedule_id>/edit/', views.edit_schedule, name='edit_schedule'),
    path('schedule/<int:schedule_id>/', views.schedule_detail, name='schedule_detail'),
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),

    
    # Exam application-related URLs
    path('exam_applications/', views.exam_application_list, name='exam_application_list'),
    path('exam/delete/<int:exam_id>/', views.delete_exam, name='delete_exam'),
    path('results/<int:result_id>/', views.result_detail, name='result_detail'),

    # Question and choices URLs
    path('questions/<int:question_id>/add_choices/', views.add_choices, name='add_choices'),
    path('question/delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('choice/delete/<int:choice_id>/', views.delete_answer_choice, name='delete_answer_choice'),

    path('class/confirm_delete/<int:class_id>/', views.confirm_delete_class, name='confirm_delete_class'),
]
