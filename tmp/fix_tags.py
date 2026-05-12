import os

filepath = r'd:\Project\College_Management_System\library\templates\library\admin_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Look for the broken if/endif block around line 200
    if '{% if record.book.available_copies <= 0 %}disabled title="No copies available" {% ' in line:
        # Check if the next line is the endif
        # We want to put them on the same line or fix the split
        new_lines.append(line.replace('{% ', '{%').strip() + ' ')
    elif 'endif %}' in line and len(new_lines) > 0 and 'available_copies' in new_lines[-1]:
        new_lines[-1] = new_lines[-1] + 'endif %}' + line.split('endif %}')[-1]
    else:
        new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Attempted line-based fix.")
