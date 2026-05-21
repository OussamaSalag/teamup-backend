import glob

print("Checking for Uuid or native_enum=False in models...")
found_issues = False
for file_path in glob.glob('app/models/*.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'import Uuid' in content or 'Uuid(' in content:
            print(f"ERROR: Found Uuid in {file_path}")
            found_issues = True
        if 'native_enum=False' in content:
            print(f"ERROR: Found native_enum=False in {file_path}")
            found_issues = True
            
if not found_issues:
    print("Models are clean! PostgreSQL dialects correctly applied.")
