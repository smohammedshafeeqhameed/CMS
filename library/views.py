from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from .models import Book, BorrowRecord, BookCategory, Reservation, Fine
from django.db.models import Sum, Q, Count
from django.urls import reverse_lazy
from users.mixins import LibraryStaffRequiredMixin
from .forms import AdminIssueBookForm, AdminUpdateFineForm, BookForm

class LibraryBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.all().order_by('title')
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search) |
                Q(isbn__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BookCategory.objects.all()
        return context

class RequestBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        
        # Check if user already has a pending or active borrow for this book
        existing = BorrowRecord.objects.filter(
            user=request.user, 
            book=book, 
            status__in=['PENDING', 'ISSUED', 'OVERDUE']
        ).first()
        
        if existing:
            messages.warning(request, f"You already have an active request or borrowing for '{book.title}'.")
            return redirect('library:book_list')
            
        if book.available_copies <= 0:
            messages.info(request, "This book is currently unavailable. You can reserve it.")
            return redirect('library:book_list')
            
        # Create request
        BorrowRecord.objects.create(
            user=request.user,
            book=book,
            status='PENDING'
        )
        messages.success(request, f"Borrowing request for '{book.title}' has been submitted.")
        return redirect('library:my_books')

class ReserveBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        
        # Check if already reserved
        if Reservation.objects.filter(user=request.user, book=book, status='RESERVED').exists():
            messages.warning(request, "You have already reserved this book.")
            return redirect('library:book_list')
            
        Reservation.objects.create(user=request.user, book=book)
        messages.success(request, f"Book '{book.title}' has been reserved. We will notify you when it's available.")
        return redirect('library:my_books')

class MyBooksView(LoginRequiredMixin, ListView):
    model = BorrowRecord
    template_name = 'library/my_books.html'
    context_object_name = 'borrow_records'

    def get_queryset(self):
        return BorrowRecord.objects.filter(user=self.request.user).order_by('-request_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Current borrowed books
        context['active_borrows'] = BorrowRecord.objects.filter(user=user, status__in=['ISSUED', 'OVERDUE'])
        
        # History
        context['borrow_history'] = BorrowRecord.objects.filter(user=user, status='RETURNED').order_by('-return_date')
        
        # Pending Fines
        context['pending_fines'] = Fine.objects.filter(borrow_record__user=user, paid=False)
        context['total_fine'] = context['pending_fines'].aggregate(total=Sum('amount'))['total'] or 0.00
        
        # Summary counts
        context['total_borrowed'] = context['active_borrows'].count()
        context['overdue_count'] = context['active_borrows'].filter(status='OVERDUE').count()
        
        return context

# --- Admin Functionality ---

class AdminLibraryDashboardView(LoginRequiredMixin, LibraryStaffRequiredMixin, ListView):
    model = BorrowRecord
    template_name = 'library/admin_dashboard.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        queryset = BorrowRecord.objects.select_related('user', 'book').all()
        
        # Filters
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(book__title__icontains=search)
            )
            
        return queryset.order_by('-request_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_issued'] = BorrowRecord.objects.filter(status='ISSUED').count()
        context['total_overdue'] = BorrowRecord.objects.filter(status='OVERDUE').count()
        context['total_pending_requests'] = BorrowRecord.objects.filter(status='PENDING').count()
        return context

class AdminIssueBookView(LoginRequiredMixin, LibraryStaffRequiredMixin, CreateView):
    model = BorrowRecord
    form_class = AdminIssueBookForm
    template_name = 'library/admin_issue_form.html'
    success_url = reverse_lazy('library:admin_dashboard')

    def form_valid(self, form):
        form.instance.status = 'ISSUED'
        student_user = form.cleaned_data['student']
        form.instance.user = student_user
        
        # Check if student already has a pending/active record for this book
        existing = BorrowRecord.objects.filter(
            user=student_user, 
            book=form.cleaned_data['book'], 
            status__in=['ISSUED', 'OVERDUE']
        ).exists()
        
        if existing:
            messages.warning(self.request, f"Student '{student_user.get_full_name()}' already has an active borrow for this book.")
            return self.form_invalid(form)

        try:
            # The model's save() method handles quantity reduction and date setting
            response = super().form_valid(form)
            messages.success(self.request, f"Book issued successfully to {student_user.get_full_name()}.")
            return response
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class AdminApproveRequestView(LoginRequiredMixin, LibraryStaffRequiredMixin, View):
    def post(self, request, record_id):
        record = get_object_or_404(BorrowRecord, id=record_id, status='PENDING')
        
        try:
            # Check availability explicitly to show better error
            if record.book.available_copies <= 0:
                messages.error(request, f"Cannot issue '{record.book.title}'. No copies available.")
                return redirect('library:admin_dashboard')
                
            record.status = 'ISSUED'
            record.save() # Triggers date setting and and book count reduction
            
            messages.success(request, f"Request for '{record.book.title}' approved. Book issued to {record.user.get_full_name()}.")
        except ValueError as e:
            messages.error(request, str(e))
            
        return redirect('library:admin_dashboard')

class AdminReturnBookView(LoginRequiredMixin, LibraryStaffRequiredMixin, View):
    def post(self, request, record_id):
        record = get_object_or_404(BorrowRecord, id=record_id)
        if record.status in ['ISSUED', 'OVERDUE']:
            # The model's save() method handles availability increment and setting return_date if status is 'RETURNED'
            record.status = 'RETURNED'
            record.save() 
            
            # Fetch updated record to ensure return_date is set for fine check
            record.refresh_from_db()
            if record.return_date and record.due_date and record.return_date > record.due_date:
                days = (record.return_date - record.due_date).days
                if days > 0:
                    fine_amt = days * 5 # ₹5 per day
                    Fine.objects.get_or_create(borrow_record=record, defaults={'amount': fine_amt})
            
            messages.success(request, f"Book '{record.book.title}' marked as returned.")
        else:
            messages.warning(request, "This record is not in an active borrow state.")
            
        return redirect('library:admin_dashboard')

class AdminUpdateFineView(LoginRequiredMixin, LibraryStaffRequiredMixin, UpdateView):
    model = Fine
    form_class = AdminUpdateFineForm
    template_name = 'library/admin_fine_form.html'
    success_url = reverse_lazy('library:admin_dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Fine information updated successfully.")
        return super().form_valid(form)

# --- Book CRUD ---

class BookCreateView(LoginRequiredMixin, LibraryStaffRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, f"Book '{form.instance.title}' added successfully.")
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, LibraryStaffRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        messages.success(self.request, f"Book '{form.instance.title}' updated successfully.")
        return super().form_valid(form)

class BookDeleteView(LoginRequiredMixin, LibraryStaffRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:book_list')

    def delete(self, request, *args, **kwargs):
        book = self.get_object()
        title = book.title
        messages.success(request, f"Book '{title}' has been removed from the catalog.")
        return super().delete(request, *args, **kwargs)
