import os

path = r'd:\Project\College_Management_System\students\templates\students\profile.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Try a more flexible match if needed, but let's start with what we saw
bad_part = '{% if profile.batch %} <span class="mx-3 opacity-30">|</span> Class of {{ profile.batch }}{% endif'
if bad_part in content:
    print("Found the bad part")
    # Find the next %}
    start_idx = content.find(bad_part)
    end_idx = content.find('%}', start_idx + len(bad_part))
    if end_idx != -1:
        # Check if there is only whitespace/newline between them
        between = content[start_idx + len(bad_part) : end_idx]
        print(f"Between: {repr(between)}")
        
        new_content = content[:start_idx + len(bad_part)] + ' %}' + content[end_idx + 2:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Fixed by inserting missing %}")
    else:
        print("Could not find closing %}")
else:
    print("Bad part not found")
