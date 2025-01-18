from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models import Max

# Gender Choices for students and teachers
GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


# Custom manager for the custom user model
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

# Role choices for user types
class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
    PARENT = 'parent', 'Parent'

# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Staff user (can log into admin)
    
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.ADMIN
    )
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Only full_name is required for superuser creation

    def __str__(self):
        return self.username
    


# Student model
class Student(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=10, unique=True)
    role_number = models.CharField(max_length=10, unique=True, editable=False)
    
    # Other fields here
    # Linking the user who created the record
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_students')

    profile_photo = models.ImageField(upload_to='students/', default='students/default-avatar.jpg', null=True)
    name = models.CharField(max_length=100)  # Full name can be stored as one field or use first_name, last_name
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    address = models.TextField()
    dob = models.DateField()

    # Parent-related fields
    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def __str__(self):
        return str(self.role_number)
    
    def save(self, *args, **kwargs):
        if not self.role_number:
            # Get the latest role_number from the database
            last_role_number = Student.objects.aggregate(Max('role_number'))['role_number__max']
            
            if last_role_number:
                # Extract the number from the last role_number, which is in the format ACLC000001
                last_number = int(last_role_number[4:])
                next_number = last_number + 1
            else:
                # If no role_number exists, start with ACLC000001
                next_number = 1

            # Generate the new role_number with the prefix ACLC and the incremented number
            self.role_number = f'ACLC{next_number:06}'

        super().save(*args, **kwargs)
    

# Parent model
class Parent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class StudentParent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    # Any other fields that are necessary to represent the connection


class Teacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='teachers/', default='media/img/default-avatar.jpg', null=True)
    full_name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()

    # Professional Information
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    joining_date = models.DateField(default=timezone.now)
    experience = models.PositiveIntegerField(help_text="Number of years of teaching experience")
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, blank=True, null=True, help_text="Specialized subjects or skills")
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Teacher's monthly salary")

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


# Course Model with extended features
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration of the course in hours or weeks")
    prerequisites = models.TextField(blank=True, null=True, help_text="Any prerequisite knowledge or courses required for this course")
    status = models.CharField(
        max_length=50,
        choices=[('Active', 'Active'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Active'
    )
    start_date = models.DateField(help_text="Course start date", null=True, blank=True)
    end_date = models.DateField(help_text="Course end date", null=True, blank=True)
    
    # Teachers associated with the course (Many-to-Many relationship with Teacher)
    teachers = models.ManyToManyField('Teacher', related_name='courses', blank=True)

    # Students associated with the course (Many-to-Many relationship with Student)
    students = models.ManyToManyField('Student', related_name='courses', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['name']


# Contact model
class Contact(models.Model):
    fullname = models.CharField(max_length=125)
    email = models.EmailField()
    subject = models.CharField(max_length=125)
    message = models.TextField()  # No max_length needed for TextField

    def __str__(self) -> str:
        return self.fullname

# CourseFees model
class CourseFees(models.Model):
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)  # Link to the course
    fees_for_course = models.DecimalField(max_digits=10, decimal_places=2)  # Total fee for the course

    def __str__(self):
        return f"Fees for {self.course_name.name}"

# FeesByStudent model
class FeesByStudent(models.Model):
    student_name = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to the student
    date_of_fees = models.DateField(auto_now=True)  # Automatically store payment date
    fees_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    payment_mode = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('online', 'Online')])  # Mode of payment
    installment_number = models.IntegerField(default=1)  # Installment number
    total_installments = models.IntegerField()  # Total installments

    def __str__(self):
        return f"{self.student_name} - {self.fees_amount} paid on {self.date_of_fees}"

# EnrollStudent model
class EnrollStudent(models.Model):
    student_name = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped')
    ], default='active')

    # Additional fields for fees and installments
    total_fees_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_fees_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_installments = models.IntegerField(default=1)
    paid_installments = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student_name} enrolled in {self.course_name.name}"

# TeacherSalaryPayment model
class TeacherSalaryPayment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('online', 'Online')])
