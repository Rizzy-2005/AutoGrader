from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    


class Upload(models.Model):
    STATUS_CHOICES = [
        ('N', 'Not Processed'),
        ('GRADED', 'Graded'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    question_paper = models.FileField(upload_to='uploads/questions/')
    model_answer = models.FileField(upload_to='uploads/answers/')
    student_answers = models.FileField(upload_to='uploads/students/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='N')  # ✅ new field

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.question_paper.name}"


# 🌟 NEW: Model to store the structured grading result
class GradingResult(models.Model):
    upload = models.OneToOneField(Upload, on_delete=models.CASCADE, related_name='grading_result')
    result_json = models.JSONField(default=list) 
    full_gemini_response = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    def total_marks_awarded(self):
        """Sum up awarded marks from the result JSON"""
        return sum(item.get('marks', 0) for item in self.result_json)

    @property
    def total_possible_marks(self):
        """Sum up maximum possible marks from the result JSON"""
        return sum(item.get('max_marks', 0) for item in self.result_json)

    def __str__(self):
        return f"Result for Upload {self.upload.id} - {self.total_marks_awarded()}/{self.total_possible_marks}"

    

