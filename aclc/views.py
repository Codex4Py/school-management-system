from django.shortcuts import render
from userapp.models import Student, EnrollStudent,FeesByStudent, Course, Teacher, TeacherSalaryPayment
from django.db.models import Sum, Count


def home(request):
    return render(request, 'index.html')

def about_view(request):
    total_students = Student.objects.count()
    total_enrolled_students = EnrollStudent.objects.count()
    total_fee_paid = FeesByStudent.objects.aggregate(Sum('fees_amount'))['fees_amount__sum'] or 0
    total_courses = Course.objects.count()
    total_teachers = Teacher.objects.count()
    total_teacher_salary_paid = TeacherSalaryPayment.objects.aggregate(Sum('amount'))['amount__sum'] or 0  # Use 'amount' instead of 'amount_paid'
    
    # Pass these values to the template
    context = {
        'total_students': total_students,
        'total_enrolled_students': total_enrolled_students,
        'total_fee_paid': total_fee_paid,
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_teacher_salary_paid': total_teacher_salary_paid,
    }
    return render(request, 'about.html', context)

def course_view(request):
    return render(request, 'course.html')

def details_view(request):
    return render(request, 'detail.html')

def feature_view(request):
    return render(request, 'feature.html')

def team_view(request):
    return render(request, 'team.html')

def testimonial_view(request):
    return render(request, 'testimonial.html')