import glob
import re

for file_path in glob.glob('app/models/*.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove native_enum=False from PrimaryKeyConstraint and UniqueConstraint
    content = re.sub(r'(Constraint\([^)]+?)\s*,\s*native_enum=False', r'\1', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed constraints")
