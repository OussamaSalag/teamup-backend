import glob
import re

for file_path in glob.glob('app/models/*.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Uuid import back to postgresql UUID
    content = content.replace('from sqlalchemy import Uuid', 'from sqlalchemy.dialects.postgresql import UUID')
    
    # Also handle cases where Uuid was imported alongside others
    content = content.replace(', Uuid', '')
    content = content.replace('Uuid, ', '')
    
    if 'UUID' not in content and 'from sqlalchemy.dialects.postgresql' not in content:
        if 'Uuid' not in content: # If we need UUID
            if 'UUID(as_uuid=True)' in content.replace('Uuid(as_uuid=True)', 'UUID(as_uuid=True)'):
                content = 'from sqlalchemy.dialects.postgresql import UUID\n' + content
                
    # Replace Uuid(as_uuid=True) usage
    content = content.replace('Uuid(as_uuid=True)', 'UUID(as_uuid=True)')
    
    # Remove native_enum=False
    content = re.sub(r',\s*native_enum=False', '', content)
    content = re.sub(r'native_enum=False\s*,?', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done switching back to PostgreSQL")
