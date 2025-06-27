print("Testing imports one by one...")

def test_import(module_name):
    try:
        print(f"\nTesting import of {module_name}...")
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing {module_name}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

# List of modules to test
modules_to_test = [
    'os',
    'logging',
    'pathlib',
    'flask',
    'dash',
    'dash_bootstrap_components',
    'dotenv',
    'db.connection',
    'db.migrations',
    'scheduler.schedule_jobs',
    'components.refresh_controls',
    'etl.refresh_pipeline',
    'housekeeping.file_cleanup',
    'layout.base'
]

# Test each import
for module in modules_to_test:
    if not test_import(module):
        print(f"\n❌ Failed to import {module}, stopping test")
        break
else:
    print("\n✅ All modules imported successfully")
