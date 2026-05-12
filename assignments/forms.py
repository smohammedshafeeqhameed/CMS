from django import forms
from .models import Assignment, AssignmentSubmission
from academics.models import Subject

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'due_date', 'max_marks', 'attachment', 'is_active']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty:
            from django.db.models import Q
            from academics.models import AcademicAdvisor, Department
            
            # Base logic: subjects user is directly teaching
            query = Q(faculty=faculty)
            
            # Advisor logic: subjects in courses/semesteers advised
            advisor_mappings = AcademicAdvisor.objects.filter(faculty=faculty, is_active=True)
            for mapping in advisor_mappings:
                query |= Q(course=mapping.course, semester=mapping.semester)
            
            # HOD logic: all subjects in their department
            if faculty.role == 'HOD':
                # Find department(s) where this user is HOD
                dept_ids = Department.objects.filter(hod=faculty).values_list('id', flat=True)
                query |= Q(department_id__in=dept_ids)
            
            # Admin logic: all subjects
            if faculty.role in ['SUPER_ADMIN', 'ADMIN']:
                self.fields['subject'].queryset = Subject.objects.filter(is_active=True)
            else:
                self.fields['subject'].queryset = Subject.objects.filter(query, is_active=True).distinct()
        
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.FileInput)):
                self.fields[field].widget.attrs.update({
                    'class': 'w-full h-12 bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
                })
            elif isinstance(self.fields[field].widget, forms.FileInput):
                 self.fields[field].widget.attrs.update({
                    'class': 'w-full py-3 bg-white/5 dark:bg-background-dark border border-dashed border-slate-200 dark:border-slate-800 rounded-xl px-4 text-slate-900 dark:text-white font-medium'
                })

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional remarks...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submission_file'].widget.attrs.update({
            'class': 'w-full py-3 bg-white/5 dark:bg-background-dark border border-dashed border-slate-200 dark:border-slate-800 rounded-xl px-4 text-slate-900 dark:text-white font-medium'
        })
        self.fields['remarks'].widget.attrs.update({
            'class': 'w-full bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
        })

class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks_obtained', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full bg-white/5 dark:bg-background-dark border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-slate-900 dark:text-white font-medium'
            })
