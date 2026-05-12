from django import forms
from .models import AcademicAdvisor, Course, StudyMaterial, Subject, TimetableDocument
from users.models import User

class AcademicAdvisorForm(forms.ModelForm):
    class Meta:
        model = AcademicAdvisor
        fields = ['faculty', 'department', 'course', 'semester', 'academic_year', 'section', 'is_active']
        widgets = {
            'department': forms.HiddenInput(),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 16, 'placeholder': 'e.g. 1'}),
            'academic_year': forms.TextInput(attrs={'placeholder': 'e.g. 2024-2025'}),
            'section': forms.TextInput(attrs={'placeholder': 'e.g. A (Optional)'}),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['department'].initial = department
            self.fields['faculty'].queryset = User.objects.filter(
                role='FACULTY', 
                department_fk=department,
                is_approved=True
            )
            self.fields['course'].queryset = Course.objects.filter(
                department=department,
                is_active=True
            )
            # Add some styling classes
            for field in self.fields:
                if not isinstance(self.fields[field].widget, forms.HiddenInput):
                    self.fields[field].widget.attrs.update({
                        'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
                    })

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'duration_years', 'description', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply premium styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
            })
        if 'description' in self.fields:
            self.fields['description'].widget = forms.Textarea(attrs={
                'class': 'w-full h-32 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl p-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium',
                'rows': 4
            })


class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'file', 'department', 'course', 'semester', 'subject']
        widgets = {
            'department': forms.Select(attrs={'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'}),
            'course': forms.Select(attrs={'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'}),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 16, 'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'}),
            'subject': forms.Select(attrs={'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'}),
            'title': forms.TextInput(attrs={'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium', 'placeholder': 'Enter material title'}),
            'description': forms.Textarea(attrs={'class': 'w-full h-32 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl p-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium', 'rows': 4, 'placeholder': 'Optional description...'}),
            'file': forms.FileInput(attrs={'class': 'w-full py-3 bg-white/5 dark:bg-background-dark border border-dashed border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'}),
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if faculty:
            # Filter subjects to only those taught by this faculty or related to their department
            self.fields['subject'].queryset = Subject.objects.filter(
                Q(faculty=faculty) | Q(department=faculty.department_fk)
            ).distinct()
            
            # If the material is being edited, we keep the original faculty's material
            # No changes needed here for now.

from django.db.models import Q

class TimetableDocumentForm(forms.ModelForm):
    class Meta:
        model = TimetableDocument
        fields = ['title', 'file', 'department', 'course', 'semester', 'academic_year', 'section', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Odd Semester Timetable 2024'}),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 16, 'placeholder': 'e.g. 1'}),
            'academic_year': forms.TextInput(attrs={'placeholder': 'e.g. 2024-2025'}),
            'section': forms.TextInput(attrs={'placeholder': 'e.g. A (Optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply premium styling
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.FileInput):
                self.fields[field].widget.attrs.update({
                    'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full py-3 bg-white/5 dark:bg-background-dark border border-dashed border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
                })

