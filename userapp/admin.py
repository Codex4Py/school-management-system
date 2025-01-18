from django.contrib import admin
from .models import CustomUser, Parent, Student, Course, Contact, StudentParent


# Register Custom User model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

# Register Parent model
class ParentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone_number', 'relationship', 'occupation')  # Display Parent info

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    get_full_name.admin_order_field = 'first_name'  # Allow ordering by first_name
    get_full_name.short_description = 'Full Name'  # Display label in admin

admin.site.register(Parent, ParentAdmin)

# Register Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'student_id', 'course_name', 'parent_name', 'created_by']
    fields = ['name', 'email', 'student_id', 'gender', 'dob', 'address', 'course', 'parent']
    search_fields = ('name', 'email', 'student_id')
    list_filter = ('gender', 'course')

    def course_name(self, obj):
        return obj.course.name  # Assuming 'course' is a ForeignKey to the Course model
    course_name.short_description = 'Course'  # Optional: for better display in admin

    def parent_name(self, obj):
        return f'{obj.parent.first_name} {obj.parent.last_name}' if obj.parent else 'No Parent'  # Handle the null case
    parent_name.short_description = 'Parent'  # Optional: for better display in admin

admin.site.register(Student, StudentAdmin)

# Register Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'duration')
    search_fields = ('name', 'status')
    list_filter = ('status',)

admin.site.register(Course, CourseAdmin)


# Register Contact model
class ContactAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'subject', 'message')
    search_fields = ('fullname', 'email', 'subject')
    ordering = ('fullname',)

admin.site.register(Contact, ContactAdmin)

admin.site.register(StudentParent)
