import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from library.models import BookCategory, Book
from django.utils import timezone

# Create Categories
categories = [
    ('Computer Science', 'Technical books on programming and algorithms'),
    ('Mathematics', 'Advanced mathematics and statistics'),
    ('General Science', 'Physics, Chemistry, and Biology'),
    ('Literature', 'Novels and classic literature'),
]

for name, desc in categories:
    cat, created = BookCategory.objects.get_or_create(name=name, defaults={'description': desc})
    if created:
        print(f"Created category: {name}")

# Create Sample Books
cs_cat = BookCategory.objects.get(name='Computer Science')
math_cat = BookCategory.objects.get(name='Mathematics')

books = [
    ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', cs_cat, 5),
    ('Clean Code', 'Robert C. Martin', '9780132350884', cs_cat, 3),
    ('Design Patterns', 'Erich Gamma', '9780201633610', cs_cat, 2),
    ('Fluent Python', 'Luciano Ramalho', '9781491946008', cs_cat, 4),
    ('Calculus', 'James Stewart', '9781285740621', math_cat, 6),
    ('Linear Algebra', 'Gilbert Strang', '9780980232776', math_cat, 10),
]

for title, author, isbn, cat, copies in books:
    book, created = Book.objects.get_or_create(
        isbn=isbn,
        defaults={
            'title': title,
            'author': author,
            'category': cat,
            'total_copies': copies,
            'available_copies': copies
        }
    )
    if created:
        print(f"Created book: {title}")
    else:
        print(f"Book already exists: {title}")
