import os

filepath = r'd:\Project\College_Management_System\library\templates\library\admin_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the broken if tag
text = text.replace('{% if record.book.available_copies <= 0 %}disabled title="No copies available" {%\n                                         endif %}', 
                    '{% if record.book.available_copies <= 0 %}disabled title="No copies available"{% endif %}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement done.")
