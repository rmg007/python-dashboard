import sys
import importlib
import traceback

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath('.'))

# List of modules to test
MODULES_TO_TEST = [
    'app',
    'callbacks.export_callbacks',
    'callbacks.kpi_callbacks',
    'callbacks.layout_callbacks',
    'callbacks.visual_callbacks',
    'components.admin.audit_callbacks',
    'components.admin.merge_callbacks',
    'components.admin.session_callbacks',
    'components.admin.user_management',
    'components.charts',
    'components.datatable',
    'components.export_components',
    'components.export_utils',
    'components.kpis',
    'components.refresh_controls',
    'db.connection',
    'db.export_queries',
    'db.job_logger',
    'db.migrations',
    'db.queries',
    'db.user_queries',
    'etl.refresh_pipeline',
    'housekeeping.file_cleanup',
    'layout.base',
    'layout.layout_manager',
    'layout.sidebar',
    'pages.admin',
    'scheduler.export_scheduler',
    'scheduler.schedule_jobs',
]

def test_import(module_name):
    """Test importing a single module."""
    try:
        print(f"\nTesting import of {module_name}...")
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Import error in {module_name}: {e}")
        print(traceback.format_exc())
        return False
    except Exception as e:
        print(f"❌ Error in {module_name}: {e}")
        print(traceback.format_exc())
        return False

def main():
    print("Testing imports...")
    print("==================")
    
    failed_imports = []
    
    for module_name in MODULES_TO_TEST:
        if not test_import(module_name):
            failed_imports.append(module_name)
    
    print("\nTest Summary:")
    print("============")
    print(f"Total modules tested: {len(MODULES_TO_TEST)}")
    print(f"Successful imports: {len(MODULES_TO_TEST) - len(failed_imports)}")
    print(f"Failed imports: {len(failed_imports)}")
    
    if failed_imports:
        print("\nFailed modules:")
        for module in failed_imports:
            print(f"- {module}")
    
    print("\nImport test completed.")

if __name__ == "__main__":
    main()
