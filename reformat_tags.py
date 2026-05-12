import re
import os

path = r'd:\Project\College_Management_System\students\templates\students\profile.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix multi-line tags: {{ ... }} and {% ... %}
# This regex matches {{ and then anything until }} including newlines
def fix_tag(match):
    tag = match.group(0)
    # Replace multiple spaces/newlines with a single space
    fixed = re.sub(r'\s+', ' ', tag)
    return fixed

content = re.sub(r'\{\{.*?\}\}', fix_tag, content, flags=re.DOTALL)
content = re.sub(r'\{%.*?%\}', fix_tag, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Reformated tags to single lines.")
