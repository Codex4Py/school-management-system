from django.db import models
from django.utils import timezone
from userapp.models import Teacher, Student

# Class Model (e.g., class subject or course)
class Class(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Math 101", "Grade 10"
    subject = models.CharField(max_length=100)  # e.g., "Mathematics", "History"
    grade_level = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Grade 5", "Grade 10"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    

# Exam Model
class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    class_obj = models.ForeignKey(Class, related_name='exams', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField()
    passing_marks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('IN_PROGRESS', 'In Progress'), 
                 ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')],
        default='DRAFT'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.class_obj.name}"

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


# Schedule Model (for managing class timings and teacher assignments)
class Schedule(models.Model):
    class_obj = models.ForeignKey(Class, related_name='schedules', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name='schedules', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)  # e.g., "Monday", "Tuesday"
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('class_obj', 'day_of_week', 'start_time')  # Prevent duplicate scheduling
    
    def __str__(self):
        return f"{self.class_obj.name} by {self.teacher.full_name} on {self.day_of_week} from {self.start_time} to {self.end_time}"


# Question Model
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(
        max_length=50, 
        choices=[('MCQ', 'Multiple Choice'), ('TEXT', 'Text'), ('TF', 'True/False')],
        default='MCQ'  # Added a default type (MCQ)
    )

    def __str__(self):
        return self.text


# AnswerChoice Model
class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'Correct' if self.is_correct else 'Incorrect'}: {self.text}"


# ExamApplication Model
class ExamApplication(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_applications')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} applied for {self.exam.title}"


# Answer Model
class Answer(models.Model):
    application = models.ForeignKey(ExamApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500, null=True, blank=True)
    answer_choice = models.ForeignKey(AnswerChoice, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Answer to {self.question.text}"


# Result Model
class Result(models.Model):
    application = models.ForeignKey(ExamApplication, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_of_result = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Result for {self.application.student.name} in {self.application.exam.title}"

    def calculate_score(self):
        correct_answers = self.application.answers.filter(answer_choice__is_correct=True)
        total_questions = self.application.exam.questions.count()
        if total_questions > 0:
            self.score = (len(correct_answers) / total_questions) * 100
        else:
            self.score = 0.0
        self.save()
