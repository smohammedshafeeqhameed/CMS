import os

filepath = r'd:\Project\College_Management_System\library\templates\library\admin_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Highly direct replacement logic to ensure no whitespace/EOL mismatches
# Look for the pattern including the line numbers context we saw
old_pattern = '{% if record.book.available_copies <= 0 %}disabled title="No copies available" {%\n                                         endif %}'

# If it didn't find that, try a simpler multi-line match
if old_pattern not in text:
    import re
    text = re.sub(r'\{%\s*if\s+record.book.available_copies\s*<=\s*0\s*%\}disabled title="No copies available"\s*\{%[ \t\n\r]+endif\s*%\}', 
                  '{% if record.book.available_copies <= 0 %}disabled title="No copies available"{% endif %}', 
                  text)
else:
    text = text.replace(old_pattern, '{% if record.book.available_copies <= 0 %}disabled title="No copies available"{% endif %}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement (v3) done.")
