from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from academics.models import Department

class CustomUserCreationForm(forms.ModelForm):
    department_fk = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="Select Department",
        help_text="Select department (if applicable)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        help_text="Enter a strong password."
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password",
        help_text="Enter the same password as above."
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'department_fk', 'phone_number', 'password', 'confirm_password')
        help_texts = {
            'role': 'Select your primary role.',
            'department_fk': 'Select your department from the list.',
            'username': 'Required. Maximum 150 characters. Letters, digits and @/./+/-/_ only.',
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow signup for various roles with a default '--' option
        if 'role' in self.fields:
            self.fields['role'].choices = [('', '--')] + [
                ('SUPER_ADMIN', 'Super Admin'),
                ('ADMIN', 'Admin'),
                ('HOD', 'Head of Department'),
                ('FACULTY', 'Faculty Mentor'),
                ('STUDENT', 'Student'),
                ('LIBRARIAN', 'Librarian'),
                ('PLACEMENT_OFFICER', 'Placement Officer'),
            ]
            self.fields['role'].initial = ''
            self.fields['role'].required = True
        
        if 'department_fk' in self.fields:
            self.fields['department_fk'].label = "Department"
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role or role == '':
            raise forms.ValidationError("Please choose a role other than '--'.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class FacultyCreationForm(CustomUserCreationForm):
    employee_id = forms.CharField(max_length=50, required=True, help_text="Unique employee ID")
    designation = forms.CharField(max_length=100, required=False, help_text="Designation/Rank")
    
    class Meta(CustomUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'department_fk', 'employee_id', 'designation', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department_fk'].required = True
        self.fields['employee_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control'})

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("An user with this employee ID already exists.")
        return employee_id

class AdminCreationForm(CustomUserCreationForm):
    employee_id = forms.CharField(max_length=50, required=True, help_text="Unique employee ID")
    designation = forms.CharField(max_length=100, required=False, help_text="Designation/Rank")
    
    class Meta(CustomUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'department_fk', 'employee_id', 'designation', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department_fk' in self.fields:
            self.fields['department_fk'].required = False
        if 'employee_id' in self.fields:
            self.fields['employee_id'].widget.attrs.update({'class': 'form-control'})
        if 'designation' in self.fields:
            self.fields['designation'].widget.attrs.update({'class': 'form-control'})

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("A user with this employee ID already exists.")
        return employee_id


class HODCreationForm(CustomUserCreationForm):
    employee_id = forms.CharField(max_length=50, required=True, help_text="Unique employee ID")
    designation = forms.CharField(max_length=100, required=False, help_text="Designation/Rank")
    
    class Meta(CustomUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'department_fk', 'employee_id', 'designation', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department_fk'].required = True
        self.fields['employee_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control'})

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("A user with this employee ID already exists.")
        return employee_id

class AdminStudentCreationForm(CustomUserCreationForm):
    """Form for admins to create student accounts directly"""
    class Meta(CustomUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'department_fk', 'phone_number', 'password', 'confirm_password')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'role' in self.fields:
            del self.fields['role'] # Role is fixed to STUDENT in view
        self.fields['department_fk'].required = True
        self.fields['department_fk'].label = "Department"

class UserApprovalForm(forms.ModelForm):
    """Form for approving/rejecting users"""
    class Meta:
        model = User
        fields = ['is_approved', 'is_active']
        widgets = {
            'is_approved': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
        }
