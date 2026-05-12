from django import forms
from .models import StudentProfile
from users.models import User
from academics.models import Department, Course

class StudentProfileForm(forms.ModelForm):
    # Include department from User model as a dropdown
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="Select Department",
        help_text="Your registered academic department"
    )
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="Select Course",
        help_text="Your enrolled course"
    )

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'department', 'course', 'batch', 'current_semester', 'profile_photo', 'bio', 'cgpa', 'linkedin_url', 'github_url', 'resume', 'cover_letter', 'skills', 'stem_badge', 'aiml_cert']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Python, Django, Machine Learning...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.FileInput(attrs={'class': 'form-control'}),
            'stem_badge': forms.FileInput(attrs={'class': 'form-control'}),
            'aiml_cert': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['department'].initial = user.department_fk
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

        # Dynamic filtering for course dropdown
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['course'].queryset = Course.objects.filter(department_id=department_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk and self.instance.user.department_fk:
            self.fields['course'].queryset = self.instance.user.department_fk.courses.all().order_by('name')
        elif user and user.department_fk:
             self.fields['course'].queryset = user.department_fk.courses.all().order_by('name')


    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Save user fields
            if self.cleaned_data.get('department'):
                dept = self.cleaned_data['department']
                profile.user.department_fk = dept
                profile.user.department = dept.name
            if self.cleaned_data.get('first_name'):
                profile.user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name'):
                profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
        return profile
