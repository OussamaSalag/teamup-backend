import os
import glob
import re

for file_path in glob.glob('app/models/*.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace UUID import
    content = content.replace('from sqlalchemy.dialects.postgresql import UUID', 'from sqlalchemy import Uuid')
    
    # Replace UUID(as_uuid=True) usage
    content = content.replace('UUID(as_uuid=True)', 'Uuid(as_uuid=True)')
    
    # Add native_enum=False to any name="..._enum"
    content = re.sub(r'(name="[^"]+")(?!\s*,\s*native_enum=False)', r'\1, native_enum=False', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done fixing models")
