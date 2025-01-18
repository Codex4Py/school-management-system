from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from .models import Class, Schedule, Exam, ExamApplication, Question, AnswerChoice, Answer, Result, Teacher, Student
from django.contrib.auth.models import User
from django.contrib import messages
from userapp.models import Course


# Add a new class
def add_class(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        grade_level = request.POST.get('grade_level')
        
        class_obj = Class.objects.create(
            name=name,
            subject=subject, 
            grade_level=grade_level
        )
        
        return redirect('class_detail', class_id=class_obj.id)
    return render(request, 'examspage/add_class.html')


def edit_class(request, class_id):
    # Retrieve the class object using get_object_or_404
    class_obj = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        # Get the updated data from the form
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        grade_level = request.POST.get('grade_level')

        # Validate the form data
        if name and subject and grade_level:
            # Update the class object with new data
            class_obj.name = name
            class_obj.subject = subject
            class_obj.grade_level = grade_level
            class_obj.save()  # Save the updated class data to the database

            return redirect('class_detail', class_id=class_obj.id)  # Redirect to the class detail page
        else:
            # If the form data is not valid, show an error message
            error_message = "All fields are required."
            return render(request, 'examspage/edit_class.html', {
                'class_obj': class_obj,
                'error_message': error_message
            })

    # If it's a GET request, pre-fill the form with current class data
    return render(request, 'examspage/edit_class.html', {
        'class_obj': class_obj
    })


# List all classes
def class_list(request):
    classes = Class.objects.all()
    return render(request, 'examspage/class_list.html', {'classes': classes})

# Class detail
def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    schedules = class_obj.schedules.all()
    return render(request, 'examspage/class_detail.html', {
        'class': class_obj,
        'schedules': schedules
    })

# Schedule an exam
def schedule_exam(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        class_id = request.POST.get('class_id')
        start_date = parse_datetime(request.POST.get('start_date'))
        end_date = parse_datetime(request.POST.get('end_date'))
        total_marks = request.POST.get('total_marks')
        passing_marks = request.POST.get('passing_marks')
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        exam = Exam.objects.create(
            title=title,
            description=description,
            class_obj=class_obj,
            start_date=start_date,
            end_date=end_date,
            total_marks=total_marks,
            passing_marks=passing_marks
        )
        
        return redirect('exam_detail', exam_id=exam.id)
        
    classes = Class.objects.all()
    return render(request, 'examspage/schedule_exam.html', {'classes': classes})

# Exam detail
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'examspage/exam_detail.html', {'exam': exam})

# List all class schedules
def class_schedule_list(request):
    schedules = Schedule.objects.all()
    return render(request, 'examspage/class_schedule_list.html', {'schedules': schedules})


# Create a new class schedule
@login_required
def create_class_schedule(request):
    # if not request.user.is_admin:
    #     return HttpResponse("Only admin members can create class schedules.")

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        teacher_id = request.POST.get('teacher_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            class_obj = get_object_or_404(Class, id=class_id)
            teacher = get_object_or_404(Teacher, id=teacher_id)

            # Check for schedule conflicts
            existing_schedule = Schedule.objects.filter(
                class_obj=class_obj,
                day_of_week=day_of_week,
                start_time=start_time
            ).first()

            if existing_schedule:
                messages.error(request, 'A schedule already exists for this time slot.')
                return redirect('create_schedule')

            schedule = Schedule.objects.create(
                class_obj=class_obj,
                teacher=teacher,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Class schedule created successfully.')
            return redirect('schedule_detail', schedule_id=schedule.id)

        except Exception as e:
            messages.error(request, f'Error creating schedule: {str(e)}')
            return redirect('create_schedule')

    classes = Class.objects.all()
    teachers = Teacher.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    context = {
        'classes': classes,
        'teachers': teachers,
        'days': days
    }
    return render(request, 'examspage/create_class_schedule.html', context)



# Edit an existing schedule
@login_required
def edit_schedule(request, schedule_id):
    if not request.user.is_staff:
        return HttpResponse("Only staff members can edit class schedules.")

    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            teacher = get_object_or_404(Teacher, id=teacher_id)

            # Check for schedule conflicts excluding current schedule
            existing_schedule = Schedule.objects.filter(
                class_obj=schedule.class_obj,
                day_of_week=day_of_week,
                start_time=start_time
            ).exclude(id=schedule_id).first()

            if existing_schedule:
                messages.error(request, 'A schedule already exists for this time slot.')
                return redirect('edit_schedule', schedule_id=schedule_id)

            schedule.teacher = teacher
            schedule.day_of_week = day_of_week
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.save()

            messages.success(request, 'Schedule updated successfully.')
            return redirect('schedule_detail', schedule_id=schedule.id)

        except Exception as e:
            messages.error(request, f'Error updating schedule: {str(e)}')
            return redirect('edit_schedule', schedule_id=schedule_id)

    teachers = Teacher.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    context = {
        'schedule': schedule,
        'teachers': teachers,
        'days': days
    }
    return render(request, 'examspage/edit_schedule.html', context)



# Schedule detail
def schedule_detail(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    return render(request, 'examspage/schedule_detail.html', {'schedule': schedule})

# List all exams
def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'examspage/exam_list.html', {'exams': exams})

# Create a new exam (Admin or Superuser)
@login_required
def exam_create(request):
    if request.user.is_superuser:  # Only superuser can create exams
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            start_date = parse_datetime(request.POST.get("start_date"))
            end_date = parse_datetime(request.POST.get("end_date"))
            exam = Exam.objects.create(
                title=title, description=description, start_date=start_date, end_date=end_date
            )
            return redirect('exam_list')
        return render(request, 'examspage/exam_create.html')
    else:
        return HttpResponse("You do not have permission to create exams.")

# View details of an exam and apply for it
@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == "POST":
        student = request.user.student
        if not ExamApplication.objects.filter(student=student, exam=exam).exists():
            ExamApplication.objects.create(student=student, exam=exam)
            return redirect('exam_take', exam_id=exam.id)
        else:
            return HttpResponse("You have already applied for this exam.")
    return render(request, 'examspage/exam_detail.html', {'exam': exam})

# View the exam questions and allow the student to submit answers
@login_required
def exam_take(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    student = request.user.student
    application = get_object_or_404(ExamApplication, student=student, exam=exam)

    if request.method == "POST":
        # Process the answers
        for question in exam.questions.all():
            answer_text = request.POST.get(f'question_{question.id}_text', '')
            answer_choice = request.POST.get(f'question_{question.id}_choice', None)

            # Create or update the answer
            answer, created = Answer.objects.get_or_create(
                application=application,
                question=question
            )
            if answer_choice:
                answer.answer_choice = AnswerChoice.objects.get(id=answer_choice)
            if answer_text:
                answer.answer_text = answer_text
            answer.save()

        # Once all answers are submitted, calculate score and redirect to result
        result = Result.objects.create(application=application, score=0)  # Temporary score, to be calculated later
        result.calculate_score()  # Calculate the score based on answers
        return redirect('result_detail', result_id=result.id)

    # Display the exam questions
    questions = exam.questions.all()
    return render(request, 'examspage/exam_take.html', {'exam': exam, 'questions': questions})

# Display the result of an exam
@login_required
def result_detail(request, result_id):
    result = get_object_or_404(Result, pk=result_id)
    return render(request, 'examspage/result_detail.html', {'result': result})

# Exam application list (Admin or Superuser only)
@login_required
def exam_application_list(request):
    if request.user.is_superuser:
        applications = ExamApplication.objects.all()
        return render(request, 'examspage/exam_application_list.html', {'applications': applications})
    else:
        return HttpResponse("You do not have permission to view this list.")

# Add a question to an exam (Admin or Superuser only)
@login_required
def add_question(request, exam_id):
    if request.user.is_superuser:
        exam = get_object_or_404(Exam, pk=exam_id)

        if request.method == "POST":
            text = request.POST.get('text')
            question_type = request.POST.get('question_type')
            # Create the question
            question = Question.objects.create(
                exam=exam,
                text=text,
                question_type=question_type
            )
            return redirect('add_choices', question_id=question.id)

        return render(request, 'examspage/add_question.html', {'exam': exam})

    else:
        return HttpResponse("You do not have permission to add questions.")

# Add answer choices for a question (Admin or Superuser only)
@login_required
def add_choices(request, question_id):
    if request.user.is_superuser:
        question = get_object_or_404(Question, pk=question_id)

        if request.method == "POST":
            choice_text = request.POST.get('choice_text')
            is_correct = request.POST.get('is_correct') == 'on'  # checkbox handling for correct answer
            # Create the answer choice
            AnswerChoice.objects.create(
                question=question,
                text=choice_text,
                is_correct=is_correct
            )
            return redirect('add_choices', question_id=question.id)

        return render(request, 'examspage/add_choices.html', {'question': question})

    else:
        return HttpResponse("You do not have permission to add choices.")

# Edit a question
@login_required
def edit_question(request, question_id):
    if request.user.is_superuser:
        question = get_object_or_404(Question, pk=question_id)

        if request.method == "POST":
            text = request.POST.get('text')
            question_type = request.POST.get('question_type')
            # Update the question
            question.text = text
            question.question_type = question_type
            question.save()
            return redirect('edit_question', question_id=question.id)

        return render(request, 'examspage/edit_question.html', {'question': question})

    else:
        return HttpResponse("You do not have permission to edit questions.")

# Edit an answer choice
@login_required
def edit_choice(request, choice_id):
    if request.user.is_superuser:
        choice = get_object_or_404(AnswerChoice, pk=choice_id)

        if request.method == "POST":
            choice_text = request.POST.get('choice_text')
            is_correct = request.POST.get('is_correct') == 'on'  # checkbox handling for correct answer
            # Update the answer choice
            choice.text = choice_text
            choice.is_correct = is_correct
            choice.save()
            return redirect('edit_choice', choice_id=choice.id)

        return render(request, 'examspage/edit_choice.html', {'choice': choice})

    else:
        return HttpResponse("You do not have permission to edit choices.")


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Class

def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    class_obj.delete()
    messages.success(request, f'Class "{class_obj.name}" deleted successfully.')
    return redirect('class_list')  # Redirect back to the class list


from .models import Schedule

def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.delete()
    messages.success(request, f'Schedule on {schedule.day_of_week} deleted successfully.')
    return redirect('class_schedule_list')  # Redirect back to the class schedule list


from .models import Exam

def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.delete()
    messages.success(request, f'Exam "{exam.title}" deleted successfully.')
    return redirect('exam_list')  # Redirect back to the exam list


from .models import Question

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    messages.success(request, f'Question deleted successfully.')
    return redirect('exam_detail', exam_id=question.exam.id)  # Redirect back to the exam details page


from .models import AnswerChoice

def delete_answer_choice(request, choice_id):
    choice = get_object_or_404(AnswerChoice, id=choice_id)
    question_id = choice.question.id  # To redirect back to the question after deleting the choice
    choice.delete()
    messages.success(request, f'Answer choice deleted successfully.')
    return redirect('add_choices', question_id=question_id)  # Redirect back to the question choices


def confirm_delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, f'Class "{class_obj.name}" deleted successfully.')
        return redirect('class_list')
    return render(request, 'examspage/confirm_delete.html', {'object': class_obj})