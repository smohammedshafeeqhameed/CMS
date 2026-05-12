import os
import shutil
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from library.models import Book, BookCategory

class Command(BaseCommand):
    help = 'Populate the library with dummy books and categories'

    def handle(self, *args, **kwargs):
        # Define categories
        categories_data = [
            {'name': 'Computer Science', 'description': 'Books related to programming, algorithms, and systems.'},
            {'name': 'Mathematics', 'description': 'Books covering calculus, algebra, and discrete math.'},
            {'name': 'Physics', 'description': 'Books on classical mechanics, quantum physics, and relativity.'},
            {'name': 'Literature', 'description': 'Classical and modern literary works.'},
            {'name': 'History', 'description': 'Global and regional historical accounts.'},
        ]

        # Create categories
        categories = {}
        for cat_data in categories_data:
            cat, created = BookCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Category '{cat.name}' created."))

        # Define books data with image paths from the artifact directory
        artifact_dir = r"C:\Users\hp\.gemini\antigravity\brain\97e56136-dcf9-4e78-9a7b-e4dbdb883042"
        books_data = [
            {
                'title': 'Advanced Algorithms',
                'author': 'Thomas H. Cormen',
                'isbn': '9780262033848',
                'category': 'Computer Science',
                'image': 'cs_book_cover_1772976790810.png',
                'location': 'Shelf A-1'
            },
            {
                'title': 'Calculus and Beyond',
                'author': 'James Stewart',
                'isbn': '9781285740621',
                'category': 'Mathematics',
                'image': 'math_book_cover_1772976871337.png',
                'location': 'Shelf B-2'
            },
            {
                'title': 'Quantum Mechanics',
                'author': 'Richard Feynman',
                'isbn': '9780465062881',
                'category': 'Physics',
                'image': 'physics_book_cover_1772976887565.png',
                'location': 'Shelf C-3'
            },
            {
                'title': 'The Art of Storytelling',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'category': 'Literature',
                'image': 'literature_book_cover_1772976908513.png',
                'location': 'Shelf D-4'
            },
            {
                'title': 'Modern World Civilizations',
                'author': 'Will Durant',
                'isbn': '9781567310122',
                'category': 'History',
                'image': 'history_book_cover_1772977069881.png',
                'location': 'Shelf E-5'
            },
        ]

        # Ensure media directory for book covers exists
        covers_dir = os.path.join(settings.MEDIA_ROOT, 'book_covers')
        if not os.path.exists(covers_dir):
            os.makedirs(covers_dir)

        # Create books
        for book_data in books_data:
            category = categories[book_data['category']]
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults={
                    'title': book_data['title'],
                    'author': book_data['author'],
                    'category': category,
                    'total_copies': 5,
                    'available_copies': 5,
                    'location': book_data['location'],
                }
            )

            if created:
                image_path = os.path.join(artifact_dir, book_data['image'])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        book.cover_image.save(book_data['image'], File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f"Book '{book.title}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Book '{book.title}' already exists."))

        self.stdout.write(self.style.SUCCESS("Library population complete!"))
