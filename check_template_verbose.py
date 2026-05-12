import re
import sys

def check_balance_verbose(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex for tags
    it = re.finditer(r'{%\s*(if|endif|for|endfor|block|endblock|empty|else|elif)\b', content)
    
    stack = []
    
    for m in it:
        line_num = content[:m.start()].count('\n') + 1
        tag = m.group(1)
        
        print(f"[{line_num}] {tag}")
        
        if tag in ['if', 'for', 'block']:
            stack.append((tag, line_num))
        elif tag == 'empty':
            if not stack or stack[-1][0] != 'for':
                print(f"ERROR: 'empty' at line {line_num} but stack is {stack}")
        elif tag in ['else', 'elif']:
            if not stack or stack[-1][0] != 'if':
                print(f"ERROR: '{tag}' at line {line_num} but stack is {stack}")
        elif tag == 'endif':
            if not stack or stack[-1][0] != 'if':
                print(f"ERROR: 'endif' at line {line_num} but stack is {stack}")
            else:
                stack.pop()
        elif tag == 'endfor':
            if not stack or stack[-1][0] != 'for':
                print(f"ERROR: 'endfor' at line {line_num} but stack is {stack}")
            else:
                stack.pop()
        elif tag == 'endblock':
            if not stack or stack[-1][0] != 'block':
                print(f"ERROR: 'endblock' at line {line_num} but stack is {stack}")
            else:
                stack.pop()
                
    if stack:
        print(f"\nFinal Unclosed Stack: {stack}")
    else:
        print("\nBALANCED")

if __name__ == "__main__":
    check_balance_verbose(sys.argv[1])
