from django import forms
from .models import BorrowRecord, Book, Fine
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AdminIssueBookForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='STUDENT', is_approved=True),
        label="Student",
        widget=forms.Select(attrs={'class': 'form-select search-select'})
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_copies__gt=0),
        label="Book",
        widget=forms.Select(attrs={'class': 'form-select search-select'})
    )
    issue_date = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    due_date = forms.DateTimeField(
        initial=lambda: timezone.now() + timezone.timedelta(days=14),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = BorrowRecord
        fields = ['student', 'book', 'issue_date', 'due_date', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure only available books are listed when creating a new record
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

class AdminUpdateFineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = ['amount', 'paid']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'location', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '13-digit ISBN'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Shelf A-101'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
