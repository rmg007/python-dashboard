import os
import sys
import traceback
from pathlib import Path

def check_file_syntax(filepath):
    """Check syntax of a single Python file."""
    try:
        # Try to compile the file
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        return True, None
    except SyntaxError as e:
        error_info = {
            'filename': filepath,
            'lineno': e.lineno,
            'offset': e.offset,
            'text': e.text,
            'msg': str(e)
        }
        return False, error_info
    except Exception as e:
        return False, {'error': str(e), 'traceback': traceback.format_exc()}

def check_directory(directory):
    """Check all Python files in a directory and its subdirectories."""
    root_dir = Path(directory)
    python_files = list(root_dir.rglob('*.py'))
    
    print(f"\nChecking {len(python_files)} Python files in {directory}...")
    
    issues_found = 0
    for filepath in python_files:
        # Skip virtual environment directories
        if 'venv' in str(filepath).split(os.sep):
            continue
            
        success, result = check_file_syntax(filepath)
        if not success:
            issues_found += 1
            print(f"\n❌ Syntax error in {filepath}")
            if isinstance(result, dict):
                if 'filename' in result:
                    print(f"   Line {result['lineno']}, Column {result['offset']}")
                    print(f"   {result['text']}" if result['text'] else "")
                    print(f"   {' ' * (result['offset']-1)}^")
                print(f"   Error: {result.get('msg', result.get('error', 'Unknown error'))}")
            else:
                print(f"   {result}")
    
    if issues_found == 0:
        print("✅ No syntax issues found in any Python files.")
    else:
        print(f"\nFound {issues_found} file(s) with syntax issues.")

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    check_directory(directory)
