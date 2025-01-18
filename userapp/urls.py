from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/manage-user/', views.manage_user, name='manage_user'),

    path('activate/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    
    path('profile/admin/', views.admin_profile_view, name='admin_profile'),

    path('profile/student/<int:student_id>/', views.student_profile_view, name='student_profile'),
    path('profile/student/<int:student_id>/', views.student_profile_admin, name='student_profile_admin'),

    path('profile/parent/add/', views.add_parent_details, name='add_parent_details'),
    path('profile/parent/', views.parent_profile_view, name='parent_profile'),
    path('profile/parent/<int:parent_id>/', views.parent_profile_admin, name='parent_profile_admin'),
    path('parent_list/', views.parent_list, name='parent_list'),


    path('add_student_for_parent/', views.add_student_for_parent, name='add_student_for_parent'),
    path('remove_student/<int:student_id>/', views.remove_student_for_parent, name='remove_student'),

    path('add_new_user/', views.add_new_user, name='add_new_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_my_account/', views.delete_my_account, name='delete_my_account'),

    path("profile/", views.profile_view, name="profile"),
    path('admission/', views.admission_form, name='admission_form'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path("student-info/<int:student_id>/", views.show_student, name="show_student"),

    path('all-course/', views.all_Course, name='all_course'),
    path('course-list/', views.course_list, name='course_list'),
    path('create-course/', views.create_course, name='create_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('success/<int:student_id>/', views.success_view, name='success'),

    path('students/', views.student_list, name='student_list'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('students/export/', views.export_students_to_excel, name='export_students_to_excel'),


    path("home/", views.home_view, name="adminhome"),
    path("fees-course-fee/", views.add_course_fee, name="add_course_fee"),
    path('course-fees/', views.course_fees_list, name='course_fees_list'),
    
    # Edit and Delete course fees, require the course_fee_id for identifying which course fee to edit or delete
    path('edit-course-fee/<int:course_fee_id>/', views.edit_course_fee, name="edit_course_fee"),
    path('delete-course-fee/<int:course_fee_id>/', views.delete_course_fee, name="delete_course_fee"),
    
    # Fees by student list view
    path('fees-by-student-list/', views.fees_by_student_list, name="fees_by_student_list"),
    
    # Enroll student in a course
    path('enroll-student/', views.enroll_student, name='enroll_student'),
    
    # List of enrolled students
    path('enrolled-students-list/', views.enrolled_students_list, name='enrolled_students_list'),
    path('enroll/student/edit/<int:enrollment_id>/', views.edit_enrollment_student, name='edit_enrollment_student'),
    path('delete-enrollment-student/<int:enrollment_id>/', views.delete_enrollment_student, name='delete_enrollment_student'),

    # Add a fee payment for a student
    path('add-fee-payment/', views.add_fee_payment, name='add_fee_payment'),
    
    # Teacher views
    path('profile/teacher/', views.teacher_profile_view, name='teacher_profile'),
    path('teacher-list/', views.teacher_list, name='teacher_list'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    
    # Teacher salary payment views
    path('teacher-salary-payment-list/', views.teacher_salary_payment_list, name='teacher_salary_payment_list'),
    path('add-teacher-salary-payment/', views.add_teacher_salary_payment, name='add_teacher_salary_payment'),
    path('delete-teacher-salary-payment/<int:payment_id>/', views.delete_teacher_salary_payment, name='delete_teacher_salary_payment'),

    path('edit-fee-payment/<int:fee_payment_id>/', views.edit_fee_payment, name='edit_fee_payment'),
    path('delete-fee-payment/<int:fee_payment_id>/', views.delete_fee_payment, name='delete_fee_payment'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
