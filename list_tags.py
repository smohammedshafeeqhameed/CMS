import re
import sys

def list_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex for all template tags
    it = re.finditer(r'{%\s*(if|endif|for|endfor|block|endblock|empty|else|elif|firstof|extends|load|url)\b.*?%}', content, re.DOTALL)
    
    for m in it:
        line_num = content[:m.start()].count('\n') + 1
        tag_content = m.group(0).replace('\n', ' ')
        print(f"L{line_num:3}: {tag_content}")

if __name__ == "__main__":
    list_tags(sys.argv[1])
