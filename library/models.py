from django.db import models
from django.conf import settings
from django.utils import timezone

class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Book Categories"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, related_name='books')
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=100, blank=True, help_text="Shelf/Row location")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Requested'),
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    request_date = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Transition to ISSUED
        if self.status == 'ISSUED' and not self.issue_date:
            if self.book.available_copies > 0:
                self.book.available_copies -= 1
                self.book.save()
                self.issue_date = timezone.now()
                if not self.due_date:
                    self.due_date = self.issue_date + timezone.timedelta(days=14)
            else:
                raise ValueError("No copies available for this book.")
        
        # Transition to RETURNED
        if self.status == 'RETURNED' and not self.return_date:
            self.return_date = timezone.now()
            self.book.available_copies += 1
            self.book.save()
            
            # Check for existing reservations for this book
            next_reservation = Reservation.objects.filter(book=self.book, status='RESERVED').order_by('reservation_date').first()
            if next_reservation:
                # Mark reservation as AVAILABLE for pick-up
                next_reservation.status = 'AVAILABLE'
                next_reservation.save()

        # Automatically check for overdue status
        if self.status == 'ISSUED' and self.due_date and self.due_date < timezone.now():
            self.status = 'OVERDUE'
            
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == 'ISSUED' and self.due_date and self.due_date < timezone.now():
            return True
        return self.status == 'OVERDUE'

    @property
    def current_fine(self):
        # Calculates fine if overdue
        if self.is_overdue:
            overdue_days = (timezone.now() - self.due_date).days
            if overdue_days > 0:
                return overdue_days * 5 # Assuming 5 units per day
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('RESERVED', 'Reserved'),
        ('AVAILABLE', 'Available for Pick-up'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library_reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RESERVED')

    def __str__(self):
        return f"{self.user.username} reserved {self.book.title}"

class Fine(models.Model):
    borrow_record = models.OneToOneField(BorrowRecord, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Fine of {self.amount} for {self.borrow_record.book.title}"
