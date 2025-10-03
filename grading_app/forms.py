from django import forms
from .models import Upload

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['question_paper', 'model_answer', 'student_answers']
