from django.contrib import admin
from .models import BookCategory, Book, BorrowRecord, Reservation, Fine
from django.utils import timezone
from django.contrib import messages

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'available_copies', 'total_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)
    readonly_fields = ('available_copies',)

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'issue_date', 'due_date', 'return_date')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('user__username', 'book__title', 'book__isbn')
    raw_id_fields = ('user', 'book')
    actions = ['issue_books', 'mark_as_returned']

    def issue_books(self, request, queryset):
        issued_count = 0
        for record in queryset.filter(status='PENDING'):
            try:
                record.status = 'ISSUED'
                record.issue_date = timezone.now()
                record.due_date = record.issue_date + timezone.timedelta(days=14)
                record.save()
                issued_count += 1
            except ValueError as e:
                self.message_user(request, str(e), messages.ERROR)
        self.message_user(request, f"{issued_count} books successfully issued.")
    issue_books.short_description = "Issue selected pending requests"

    def mark_as_returned(self, request, queryset):
        returned_count = 0
        for record in queryset.filter(status__in=['ISSUED', 'OVERDUE']):
            record.status = 'RETURNED'
            record.save()
            returned_count += 1
        self.message_user(request, f"{returned_count} books successfully marked as returned.")
    mark_as_returned.short_description = "Mark selected active borrows as returned"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'reservation_date')
    list_filter = ('status',)
    search_fields = ('user__username', 'book__title')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('borrow_record', 'amount', 'paid', 'paid_date')
    list_filter = ('paid',)
    search_fields = ('borrow_record__user__username', 'borrow_record__book__title')
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        queryset.update(paid=True, paid_date=timezone.now())
    mark_as_paid.short_description = "Mark selected fines as paid"
