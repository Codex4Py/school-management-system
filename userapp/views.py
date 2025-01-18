from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import uuid


from .models import StudentParent
from django.http import HttpResponseForbidden

from .models import UserRole, Contact, Student, Course
from userapp.models import CustomUser
from .models import CourseFees, FeesByStudent, EnrollStudent, Teacher, TeacherSalaryPayment, Parent, StudentParent

from decimal import Decimal, InvalidOperation  # Add the necessary import
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.timezone import datetime
from openpyxl import Workbook
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test


# Ensure you use the correct user model
CustomUser = get_user_model()


def is_admin(user):
    return user.is_staff  # or check user role if needed


# @login_required
# @user_passes_test(is_admin)
def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Check if the user is already active
    if user.is_active:
        messages.info(request, f'{user.username} is already active.')
        return redirect('manage_user')  # Redirect to a user list or appropriate page

    # Activate the user
    user.is_active = True
    user.save()
    messages.success(request, f'{user.username} has been activated.')
    return redirect('manage_user')  # Redirect to a user list or appropriate page


# @login_required
# @user_passes_test(is_admin)
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Check if the user is already inactive
    if not user.is_active:
        messages.info(request, f'{user.username} is already deactivated.')
        return redirect('manage_user')  # Redirect to a user list or appropriate page

    # Deactivate the user
    user.is_active = False
    user.save()
    messages.success(request, f'{user.username} has been deactivated.')
    return redirect('manage_user')  # Redirect to a user list or appropriate page



def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role')

        # Validation: Check if passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        
        if not full_name or not email or not username:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        # Validate role
        if role not in [choice[0] for choice in UserRole.choices]:
            messages.error(request, "Invalid role selected.")
            return redirect('signup')

        try:
            user = CustomUser.objects.create_user(
                username=username, 
                email=email, 
                password=password, 
                full_name=full_name,
                role=role
            )
            messages.success(request, "Account created successfully!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('signup')

    return render(request, 'user/signup.html', {'roles': UserRole.choices})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")

            # Redirect based on the user's role
            if user.role == UserRole.ADMIN:
                return redirect('admin_dashboard')  
            elif user.role == UserRole.TEACHER:
                return redirect('teacher_dashboard')
            elif user.role == UserRole.PARENT:
                return redirect('parent_dashboard')
            elif user.role == UserRole.STUDENT:
                return redirect('student_dashboard')
            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'user/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


# Student Dashboard View
@login_required(login_url='login')
def student_dashboard(request):
    if request.user.role != UserRole.STUDENT:
        return redirect('home')  # Or some other role-based redirection
    return render(request, 'user/dashboard/student_dashboard.html')


# Teacher Dashboard View
@login_required(login_url='login')
def teacher_dashboard(request):
    if request.user.role != UserRole.TEACHER:
        return redirect('home')
    return render(request, 'user/dashboard/teacher_dashboard.html')

# Parent Dashboard View
@login_required(login_url='login')
def parent_dashboard(request):
    students = Student.objects.all()
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'students': students
    }
    if request.user.role != UserRole.PARENT:
        return redirect('home')
    return render(request, 'user/dashboard/parent_dashboard.html', context)


# Admin Dashboard View
@login_required(login_url='login')
def admin_dashboard(request):
    if request.user.role != UserRole.ADMIN:
        return redirect('home')
    
    total_parent = Parent.objects.count()
    total_students = Student.objects.count()
    total_enrolled_students = EnrollStudent.objects.count()
    total_fee_paid = FeesByStudent.objects.aggregate(Sum('fees_amount'))['fees_amount__sum'] or 0
    total_courses = Course.objects.count()
    total_teachers = Teacher.objects.count()
    total_teacher_salary_paid = TeacherSalaryPayment.objects.aggregate(Sum('amount'))['amount__sum'] or 0  # Use 'amount' instead of 'amount_paid'
  
    users = CustomUser.objects.all()

    # Pass these values to the template
    context = {
        'total_parent':total_parent,
        'users': users,
        'total_students': total_students,
        'total_enrolled_students': total_enrolled_students,
        'total_fee_paid': total_fee_paid,
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_teacher_salary_paid': total_teacher_salary_paid,

    }
    return render(request, 'user/dashboard/admin_dashboard.html', context)


def manage_user(request):
    users = CustomUser.objects.all()
    return render(request, 'user/dashboard/manage_user.html', {'users': users})


def contact_view(request):
    if request.method == "POST":
        full_name = request.POST.get('fullname')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        msg = request.POST.get('msg')

        # Validate required fields
        if not full_name or not email or not subject or not msg:
            messages.error(request, "All fields are required.")
            return redirect('contact')
        
        # Create and save the contact entry
        data = Contact(fullname=full_name, email=email, subject=subject, message=msg)
        data.save()
        messages.success(request, "Your message has been sent successfully.")
        return redirect('contact')
    
    return render(request, 'contact.html')


@login_required(login_url='login')
def admin_profile_view(request):
    admin = request.user

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
        'admin': admin,
    }
    return render(request, 'user/profile/admin_profile.html', context) 




@login_required(login_url='login')
def student_profile_view(request, student_id):
    try:
        # Attempt to get the student object
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        # Handle the case where the student does not exist
        return redirect('admission_form')

        # return render(request, 'user/profile/student_not_found.html', {'student_id': student_id})
    
    # Retrieve all courses for context
    courses = Course.objects.all()
    
    # Prepare the context with student and courses
    context = {
        'courses': courses,
        'student': student
    }
    
    # Render the student profile page
    return render(request, 'user/profile/student_profile.html', context)




def student_profile_admin(request, student_id):
    try:
        # Try to retrieve the student by ID
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        # If the student does not exist, redirect to the admission form
        return redirect('admission_form')

    # Retrieve all courses for context
    courses = Course.objects.all()

    # Prepare the context with student and courses
    context = {
        'courses': courses,
        'student': student
    }

    # Render the student profile template
    return render(request, 'exampage/student_profile_main.html', context)




@login_required(login_url='login')
def parent_profile_view(request):
    parent = request.user  # Get the logged-in user
    # Get the Parent instance for the logged-in user
    try:
        parentData = Parent.objects.get(user=parent)  # Query the Parent model based on the user
    except Parent.DoesNotExist:
        parentData = None  # If no Parent data exists, set it to None or handle as needed
    
    if parentData:
        # If parentData exists, filter StudentParent based on the Parent instance
        connections = StudentParent.objects.filter(parent=parentData)
    else:
        # If no Parent data exists, set connections to an empty queryset or handle accordingly
        connections = StudentParent.objects.none()

    # Get all students, but we'll filter them based on connections
    studentData = Student.objects.all()
    
    context = {
        'studentData': studentData,
        'parentData': parentData,
        'parent': parent,
        'connections': connections  # Send only the relevant connections
    }
    
    return render(request, 'user/profile/parent_profile.html', context)


def parent_profile_admin(request, parent_id):
    parents = Parent.objects.get(id=parent_id)
    studentData = Student.objects.all()
    context = {
        'studentData': studentData,
        'parents': parents,
        }
    return render(request, 'user/profile/parent_profile.html', context)


@login_required(login_url='login')
def add_parent_details(request):
    # Get the parent object associated with the logged-in user if it exists
    parent = Parent.objects.filter(user=request.user).first()
    
    # Check if the form is submitted via POST
    if request.method == 'POST':
        # Retrieve data from the POST request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        relationship = request.POST.get('relationship')
        occupation = request.POST.get('occupation')
        address = request.POST.get('address')

        # Perform form validation (optional but recommended)
        if not first_name or not last_name or not email:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'user/profile/add_parent_details.html', {'parent': parent})

        # If the parent object exists, update it; otherwise, create a new one
        if parent:
            parent.first_name = first_name
            parent.last_name = last_name
            parent.email = email
            parent.phone_number = phone_number
            parent.relationship = relationship
            parent.occupation = occupation
            parent.address = address
            parent.save()
            messages.success(request, "Parent details updated successfully!")
        else:
            parent = Parent(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                relationship=relationship,
                occupation=occupation,
                address=address,
            )
            parent.save()
            messages.success(request, "Parent details added successfully!")

        # After saving, redirect to the parent profile page or another relevant page
        return redirect('parent_profile')  # Or adjust to your desired redirect view

    # If it's not a POST request, render the form with existing parent details if available
    return render(request, 'user/profile/add_parent_details.html', {'parent': parent})
    

def delete_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')


# delete my account
def delete_my_account(request):
    user = request.user
    user.delete()
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('login')


@login_required(login_url='login')
def teacher_profile_view(request):
    teacher = request.user  # the logged-in user (assumed to be a teacher)
    # Assuming each user has a related teacher profile
    try:
        teachers = Teacher.objects.get(user=request.user)  # Retrieve the teacher instance related to the user
    except Teacher.DoesNotExist:
        return redirect('add_teacher')  # 'add-teacher' is the name of the URL pattern to create the teacher profile

    context = {
        'teachers': teachers,
        'teacher': teacher,
    }
    return render(request, 'user/profile/teacher_profile.html', context)



@login_required(login_url='login')
def add_new_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validation
        if not all([first_name, last_name, email, user_type, password, confirm_password]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_new_user')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('add_new_user')

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('add_new_user')

        try:
            # Create username from email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            # Ensure unique username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Create new user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                full_name=f"{first_name} {last_name}",
                role=user_type,
                is_active=True
            )           

            messages.success(request, "User created successfully.")
            return redirect('add_new_user')

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect('add_new_user')
    return render(request, 'user/add_new_user.html')# Assuming StudentParent and Parent models are in the same app



@login_required(login_url='login')  # Ensure user is logged in
def add_student_for_parent(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')  # Get selected student ID from dropdown
        
        # Fetch the student using .filter() to avoid exceptions
        student = Student.objects.filter(id=student_id).first()  # Use filter() to avoid exceptions
        if not student:
            messages.error(request, "Student not found.")
            return redirect('parent_profile')

        # Check if the user is a parent (based on the role)
        if request.user.role != UserRole.PARENT:
            messages.error(request, "You are not authorized to add students as a parent.")
            return redirect('parent_profile')  # Redirect to a page, like the home or profile page
        
        # Fetch the Parent instance associated with the logged-in user using .filter() to avoid exceptions
        parent = Parent.objects.filter(user=request.user).first()  # Use filter() to avoid exceptions
        if not parent:
            messages.error(request, "You need to create a parent record first.")
            return redirect('parent_profile')  # Redirect to a page where they can create the parent record
        
        # Check if the Student-Parent relationship already exists
        existing_relationship = StudentParent.objects.filter(student=student, parent=parent).first()
        if existing_relationship:
            messages.error(request, "This student is already linked to the parent.")
            return redirect('parent_profile')

        # Create a new StudentParent object to connect the student and parent
        student_parent = StudentParent(parent=parent, student=student)
        student_parent.save()
        
        # Add success message
        messages.success(request, "Student has been added successfully.")
        return redirect('parent_profile')  # Redirect to the same page or another view

    # Get a list of all students to populate the selection dropdown
    students = Student.objects.all()
    context = {
        'students': students
    }
    return render(request, 'user/add_student_of_parent.html', context)  # Pass students to the template



@login_required(login_url='login')  # Ensure the user is logged in
def remove_student_for_parent(request, student_id):
    # Fetch the student using .filter() to avoid exceptions
    student = Student.objects.filter(id=student_id).first()
    if not student:
        messages.error(request, "Student not found.")
        return redirect('parent_profile')  # Redirect to parent profile or another page
    
    # Check if the user is a parent (based on the role)
    if request.user.role != UserRole.PARENT:
        messages.error(request, "You are not authorized to remove students as a parent.")
        return redirect('parent_profile')  # Redirect to parent profile or another page
    
    # Fetch the Parent instance associated with the logged-in user
    parent = Parent.objects.filter(user=request.user).first()
    if not parent:
        messages.error(request, "You need to create a parent record first.")
        return redirect('parent_profile')  # Redirect to a page where they can create the parent record
    
    # Check if the Student-Parent relationship exists
    student_parent = StudentParent.objects.filter(student=student, parent=parent).first()
    if not student_parent:
        messages.error(request, "This student is not linked to the parent.")
        return redirect('parent_profile')  # Redirect to parent profile or another page
    
    # Remove the Student-Parent relationship
    student_parent.delete()
    
    # Add success message
    messages.success(request, "Student has been removed successfully.")
    return redirect('parent_profile')  # Redirect to the parent profile or another page




# Create your views here.
@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'accounts/profile.html')

# View to list all courses
def all_Course(request):
    return render(request, 'accounts/all-course.html')

def course_list(request):
    courses = Course.objects.all()  # Get all courses
    return render(request, 'accounts/course_list.html', {'courses': courses})

# View to create a new course (handles POST request directly)
@login_required(login_url='/login/')
def create_course(request):
    if request.method == 'POST':
        # Collecting POST data from the request
        name = request.POST.get('name')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        prerequisites = request.POST.get('prerequisites', '')  # Optional field
        status = request.POST.get('status', 'Active')  # Default 'Active' status

        # Validate input
        if not name or not description or not duration:
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/create_course.html')

        # Creating the new course entry
        course = Course.objects.create(
            name=name,
            description=description,
            duration=duration,
            prerequisites=prerequisites,
            status=status
        )

        return redirect('course_list')  # Redirect to the list of courses after creation

    return render(request, 'accounts/create_course.html')  # If GET, show the form for creating a course

# View to edit an existing course
@login_required(login_url='/login/')
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        # Collecting updated data from the request
        course.name = request.POST.get('name', course.name)
        course.description = request.POST.get('description', course.description)
        course.duration = request.POST.get('duration', course.duration)
        course.prerequisites = request.POST.get('prerequisites', course.prerequisites)
        course.status = request.POST.get('status', course.status)

        course.save()  # Save the updated course

        return redirect('course_list')  # Redirect to the list of courses after editing

    return render(request, 'accounts/edit_course.html', {'course': course})  # If GET, show the form to edit the course

# View to delete a course
@login_required(login_url='/login/')
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.delete()  # Delete the course
        return redirect('course_list')  # Redirect to the list of courses after deletion

    return render(request, 'accounts/confirm_delete.html', {'course': course})  # Confirm before deleting


@login_required(login_url='/login/')
def admission_form(request):
    # Fetch all available courses to show in the form
    courses = Course.objects.all()

    if request.method == 'POST':
        # Getting form data from the request
        name = request.POST.get('name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course')
        address = request.POST.get('address')

        profile_photo = request.FILES.get('profile_photo')
        father_name = request.POST.get('father_name')
        father_occupation = request.POST.get('father_occupation')
        father_phone = request.POST.get('father_phone')
        mother_name = request.POST.get('mother_name')
        
        user_id = request.POST.get('user')

        # Validate the data if needed (basic checks)
        if not name or not email or not dob or not gender or not course_id or not address:
            messages.error(request, 'Please fill out all fields.')
            return render(request, 'accounts/admission_form.html', {
                'courses': courses
            })

        try:
            # Find the selected course object
            selected_course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            messages.error(request, 'Invalid course selected.')
            return render(request, 'accounts/admission_form.html', {
                'courses': courses
            })

        try:
            # Find the logged-in user and set as user for the new student
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid user selected.')
            return render(request, 'accounts/admission_form.html', {
                'courses': courses
            })

        # Generate a student ID (for example, unique to each student)
        student_id = f"ACLC{str(uuid.uuid4().int)[:10]}"

        # Create and save a new Student record
        student = Student(
            user=user,
            student_id=student_id,
            role_number=uuid.uuid4(),  # Automatically generated role number
            name=name,
            email=email,
            dob=dob,
            gender=gender,
            course=selected_course,
            address=address,
            profile_photo=profile_photo,
            father_name=father_name,
            father_occupation=father_occupation,
            father_phone=father_phone,
            mother_name=mother_name,
            created_by=request.user  # assuming logged-in user is the one who created the record
        )
        student.save()

        # Redirect or show a success message after form submission
        return redirect('success', student_id=student.id)

    # Render the form if the request is GET
    return render(request, 'accounts/admission_form.html', {'courses': courses})



@login_required(login_url='/login/')
def show_student(request, student_id):
        student = get_object_or_404(Student, id=student_id)
        courses = Course.objects.all()
        context = {
            'courses': courses,
            'student': student
        }
        return render(request, 'accounts/student_information.html', context)



@login_required(login_url='/login/')
def edit_student(request, student_id):
    # Fetch the student to be edited
    student = get_object_or_404(Student, id=student_id)
    
    # Fetch all available courses to show in the form
    courses = Course.objects.all()

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course')
        address = request.POST.get('address')

        profile_photo = request.FILES.get('profile_photo')
        father_name = request.POST.get('father_name')
        father_occupation = request.POST.get('father_occupation')
        father_phone = request.POST.get('father_phone')
        mother_name = request.POST.get('mother_name')

        # Validate the data if needed
        if not name or not email or not dob or not gender or not course_id or not address:
            messages.error(request, 'Please fill out all fields.')
            return render(request, 'accounts/edit_student.html', {
                'courses': courses,
                'student': student
            })

        try:
            # Find the selected course object
            selected_course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            messages.error(request, 'Invalid course selected.')
            return render(request, 'accounts/edit_student.html', {
                'courses': courses,
                'student': student
            })

        # Update the student record
        student.name = name
        student.email = email
        student.dob = dob
        student.gender = gender
        student.course = selected_course
        student.address = address

        # Updated the student record
        student.profile_photo = profile_photo
        student.father_name = father_name
        student.father_occupation = father_occupation
        student.father_phone = father_phone
        student.mother_name = mother_name

        student.save()
        
        # Redirect to the student list page after successful update
        messages.success(request, 'Student data updated successfully!')
        return redirect('student_list')

    # Render the edit form if the request is GET
    return render(request, 'accounts/edit_student.html', {
        'courses': courses,
        'student': student
    })

@login_required(login_url='/login/')
def success_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'accounts/success.html', {'student': student})

def student_list(request):
    query = request.GET.get('search', '')  # Get the search query from the GET request
    students = Student.objects.all()  # Get all students

    if query:
        # Filter students based on the search term (search in name and email)
        students = students.filter(name__icontains=query) | students.filter(email__icontains=query)
    
    return render(request, 'accounts/student_list.html', {
        'students': students,
        'search_query': query
    })

@login_required(login_url='/login/')
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('student_list')

@login_required(login_url='/login/')
def export_students_to_excel(request):
    # Create a workbook and add a sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    # Add the headers (matching the table in the template)
    headers = ["Sr.No.", "ID", "Name", "Email", "Course"]
    ws.append(headers)

    # Get the student data from the database
    students = Student.objects.all()

    # Add student data to the worksheet, including Sr.No.
    for index, student in enumerate(students, start=1):
        row = [
            index,  # Sr.No.
            student.student_id,  # ID
            student.name,
            student.email,
            student.course.name  # Assuming 'course' is a related field
        ]
        ws.append(row)

    # Set the response as an Excel file
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'
    wb.save(response)
    return response


# Dashboard view
@login_required(login_url='/login/')
def home_view(request):
    # Dashboard data
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
    return render(request, 'fees/admin_home.html', context)


# View to list all courses fees
def course_fees_list(request):
    course_fees = CourseFees.objects.all()
    return render(request, 'fees/course_fees_list.html', {'course_fees': course_fees})

# View to add a new course fee
@login_required(login_url='/login/')
def add_course_fee(request):
    if request.method == 'POST':
        course_name_id = request.POST.get('course_name')  # get course id from POST
        fees_for_course = request.POST.get('fees_for_course')  # get the fee amount
        course_name = get_object_or_404(Course, id=course_name_id)  # fetch the course instance

        # Create and save new course fee record
        CourseFees.objects.create(course_name=course_name, fees_for_course=fees_for_course)
        return redirect('course_fees_list')
    else:
        courses = Course.objects.all()
        return render(request, 'fees/add_course_fee.html', {'courses': courses})

# View to edit a course fee
@login_required(login_url='/login/')
def edit_course_fee(request, course_fee_id):
    course_fee = get_object_or_404(CourseFees, id=course_fee_id)

    if request.method == 'POST':
        course_name_id = request.POST.get('course_name')  # get updated course id
        fees_for_course = request.POST.get('fees_for_course')  # get updated fee amount
        course_name = get_object_or_404(Course, id=course_name_id)  # fetch the course instance

        # Update course fee
        course_fee.course_name = course_name
        course_fee.fees_for_course = fees_for_course
        course_fee.save()

        return redirect('course_fees_list')

    else:
        courses = Course.objects.all()
        return render(request, 'fees/edit_course_fee.html', {'course_fee': course_fee, 'courses': courses})

# View to delete a course fee
@login_required(login_url='/login/')
def delete_course_fee(request, course_fee_id):
    course_fee = get_object_or_404(CourseFees, id=course_fee_id)
    course_fee.delete()
    return redirect('course_fees_list')

# View to list all fees paid by students
@login_required(login_url='/login/')
def fees_by_student_list(request):
    fees_by_students = FeesByStudent.objects.all()
    return render(request, 'fees/fees_by_student_list.html', {'fees_by_students': fees_by_students})

# View to add a fee payment by a student
@login_required(login_url='/login/')
def add_fee_payment(request):
    if request.method == 'POST':
        student_name_id = request.POST.get('student_name')
        fees_amount = request.POST.get('fees_amount')
        payment_mode = request.POST.get('payment_mode')
        installment_number = request.POST.get('installment_number')
        total_installments = request.POST.get('total_installments')

        student_name = get_object_or_404(Student, id=student_name_id)

        # Create and save the fee payment record
        FeesByStudent.objects.create(
            student_name=student_name,
            fees_amount=fees_amount,
            payment_mode=payment_mode,
            installment_number=installment_number,
            total_installments=total_installments
        )
        return redirect('fees_by_student_list')

    else:
        students = Student.objects.all()
        return render(request, 'fees/add_fee_payment.html', {'students': students})

# View to list all enrolled students
def enrolled_students_list(request):
    enrolled_students = EnrollStudent.objects.all()
    return render(request, 'fees/enrolled_students_list.html', {'enrolled_students': enrolled_students})


# View to enroll a student in a course
@login_required(login_url='/login/')
def enroll_student(request):
    if request.method == 'POST':
        student_name_id = request.POST.get('student_name')
        enrolled_course_id = request.POST.get('enrolled_course')
        total_fees_paid = request.POST.get('total_fees_paid')
        total_fees_due = request.POST.get('total_fees_due')
        total_installments = request.POST.get('total_installments')
        paid_installments = request.POST.get('paid_installments')

        student_name = get_object_or_404(Student, id=student_name_id)
        enrolled_course = get_object_or_404(Course, id=enrolled_course_id)

        # Create and save the enrollment record
        EnrollStudent.objects.create(
            student_name=student_name,
            course_name =enrolled_course,
            total_fees_paid=total_fees_paid,
            total_fees_due=total_fees_due,
            total_installments=total_installments,
            paid_installments=paid_installments
        )
        return redirect('enrolled_students_list')

    else:
        students = Student.objects.all()
        courses = Course.objects.all()
        course_fees = CourseFees.objects.all()
        return render(request, 'fees/enroll_student.html', {'students': students, 'courses': courses, 'course_fees': course_fees})


@login_required(login_url='/login/')
def edit_enrollment_student(request, enrollment_id):
    # Get the existing enrollment object using the enrollment_id
    enrollment = get_object_or_404(EnrollStudent, id=enrollment_id)

    if request.method == 'POST':
        # Get the updated data from the form
        student_name_id = request.POST.get('student_name')
        enrolled_course_id = request.POST.get('enrolled_course')
        fees_for_course_id = request.POST.get('fees_for_course')
        total_fees_paid = request.POST.get('total_fees_paid')
        total_fees_due = request.POST.get('total_fees_due')
        total_installments = request.POST.get('total_installments')
        paid_installments = request.POST.get('paid_installments')

        # Update the enrollment object with the new data
        student_name = get_object_or_404(Student, id=student_name_id)
        enrolled_course = get_object_or_404(Course, id=enrolled_course_id)
        fees_for_course = get_object_or_404(CourseFees, id=fees_for_course_id)

        # Update the enrollment record
        enrollment.student_name = student_name
        enrollment.enrolled_course = enrolled_course
        enrollment.fees_for_course = fees_for_course
        enrollment.total_fees_paid = total_fees_paid
        enrollment.total_fees_due = total_fees_due
        enrollment.total_installments = total_installments
        enrollment.paid_installments = paid_installments
        enrollment.save()

        return redirect('enrolled_students_list')  # Redirect to a list of enrolled students after saving

    else:
        # If it's a GET request, pass the current enrollment data to the template
        students = Student.objects.all()
        courses = Course.objects.all()
        course_fees = CourseFees.objects.all()
        return render(request, 'fees/edit_enrolled_students_list.html', {
            'enrollment': enrollment,
            'students': students,
            'courses': courses,
            'course_fees': course_fees
        })
    
@login_required(login_url='/login/')
def delete_enrollment_student(request, enrollment_id):
    # Get the enrollment object to delete
    enrollment = get_object_or_404(EnrollStudent, id=enrollment_id)
    
    # Delete the enrollment object
    enrollment.delete()

    # Redirect back to the list of enrolled students after deletion
    return redirect('enrolled_students_list')

# View to list all teachers
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'fees/teacher_list.html', {'teachers': teachers})



# View to list all teachers
def parent_list(request):
    parents = Parent.objects.all()
    return render(request, 'accounts/parent_list.html', {'parents': parents})


@login_required(login_url='/login/')
def add_teacher(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        user_id = request.POST.get('user_id')
        full_name = request.POST.get('full_name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        department = request.POST.get('department')
        designation = request.POST.get('designation')
        joining_date = request.POST.get('joining_date')
        experience = request.POST.get('experience')
        qualification = request.POST.get('qualification')
        specialization = request.POST.get('specialization')
        profile_photo = request.FILES.get('profile_photo')
        salary = request.POST.get('salary')  # Handling image upload
        
        # Validate the form fields
        if not full_name or not email or not phone_number:
            return render(request, 'fees/add_teacher.html', {
                'error_message': 'Full Name, Email, and Phone Number are required.',
            })

        # Convert the joining date and dob into proper Date format
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
            joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date() if joining_date else None
        except ValueError:
            return render(request, 'fees/add_teacher.html', {
                'error_message': 'Invalid date format. Use YYYY-MM-DD.',
            })
        
        try:
            experience = int(experience) if experience else 0
        except ValueError:
            return render(request, 'fees/add_teacher.html', {
                'error_message': 'Experience should be a valid number.',
            })

        # Create and save the Teacher instance
        try:
            teacher = Teacher.objects.create(
                user_id=user_id,
                full_name=full_name,
                dob=dob,
                gender=gender,
                phone_number=phone_number,
                email=email,
                address=address,
                department=department,
                designation=designation,
                joining_date=joining_date or timezone.now().date(),
                experience=experience,
                qualification=qualification,
                specialization=specialization,
                profile_photo=profile_photo or 'media/img/default-avatar.png',  # Default photo if not provided
                salary = salary,
            )
        except ValidationError as e:
            return render(request, 'fees/add_teacher.html', {
                'error_message': str(e),
            })

        # Redirect to the teacher list page after successful addition
        return redirect('teacher_list')

    else:
        courses = Course.objects.all()
        # For GET requests, render the form to add a teacher
        return render(request, 'fees/add_teacher.html', {'courses' : courses})



@login_required(login_url='/login/')
def delete_teacher(request, teacher_id):
    # Retrieve the teacher to be deleted
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        # Delete the teacher from the database
        teacher.delete()
        # Redirect to the list of teachers or another relevant page
        return redirect('teacher_list')  # Assuming you have a teacher list page

    return render(request, 'fees/confirm_delete_teacher.html', {'teacher': teacher})


@login_required(login_url='/login/')
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        teacher.name = request.POST.get('name')
        teacher.address = request.POST.get('address')
        teacher.phone = request.POST.get('phone')
        teacher.qualifications = request.POST.get('qualifications')
        expert_subject_id = request.POST.get('expert_subject')
        teacher.salary = request.POST.get('salary')
        teacher.date_of_joining = request.POST.get('date_of_joining')

        # Handling the checkbox for `is_active`
        teacher.is_active = request.POST.get('is_active') == 'on'  # Convert 'on' to True, anything else to False

        expert_subject = get_object_or_404(Course, id=expert_subject_id)
        teacher.expert_subject = expert_subject

        teacher.save()
        return redirect('teacher_list')

    else:
        courses = Course.objects.all()
        return render(request, 'fees/edit_teacher.html', {'teacher': teacher, 'courses': courses})


# View to list all salary payments
@login_required(login_url='/login/')
def teacher_salary_payment_list(request):
    salary_payments = TeacherSalaryPayment.objects.all()
    return render(request, 'fees/teacher_salary_payment_list.html', {'salary_payments': salary_payments})



@login_required(login_url='/login/')
def add_teacher_salary_payment(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        amount_paid = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')

        # Get teacher object based on the ID
        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Create and save the salary payment record
        TeacherSalaryPayment.objects.create(
            teacher=teacher,
            amount=amount_paid,
            payment_method=payment_mode
        )

        # Redirect to the teacher salary payment list view
        return redirect('teacher_salary_payment_list')

    else:
        teachers = Teacher.objects.all()
        return render(request, 'fees/add_teacher_salary_payment.html', {'teachers': teachers})

@login_required(login_url='/login/')
def delete_teacher_salary_payment(request, payment_id):
    salary_payment = get_object_or_404(TeacherSalaryPayment, id=payment_id)
    salary_payment.delete()
    return redirect('teacher_salary_payment_list')



@login_required(login_url='/login/')
def edit_fee_payment(request, fee_payment_id):
    # Get the existing fee payment object
    fee_payment = get_object_or_404(FeesByStudent, id=fee_payment_id)

    if request.method == 'POST':
        # Get updated data from form
        student_name_id = request.POST.get('student_name')
        fees_amount = request.POST.get('fees_amount')
        payment_mode = request.POST.get('payment_mode')
        installment_number = request.POST.get('installment_number')
        total_installments = request.POST.get('total_installments')

        # Get student object
        student_name = get_object_or_404(Student, id=student_name_id)

        # Update fee payment record
        fee_payment.student_name = student_name
        fee_payment.fees_amount = fees_amount
        fee_payment.payment_mode = payment_mode
        fee_payment.installment_number = installment_number
        fee_payment.total_installments = total_installments
        fee_payment.save()

        return redirect('fees_by_student_list')

    else:
        students = Student.objects.all()
        return render(request, 'fees/edit_fee_payment.html', {
            'fee_payment': fee_payment,
            'students': students
        })
    

@login_required(login_url='/login/')
def delete_fee_payment(request, fee_payment_id):
    # Get the fee payment object to delete
    fee_payment = get_object_or_404(FeesByStudent, id=fee_payment_id)
    
    # Delete the fee payment
    fee_payment.delete()
    
    # Redirect back to the fees by student list
    return redirect('fees_by_student_list')

