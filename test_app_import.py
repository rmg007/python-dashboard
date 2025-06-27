"""
Simple script to test importing the app module with detailed error reporting.
"""
import sys
import os
import traceback

def setup_console_encoding():
    """Set up console encoding to handle Unicode characters."""
    import sys
    import io
    if sys.platform.startswith('win'):
        if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    # Set up console encoding first
    setup_console_encoding()
    
    # Add the project root to the Python path
    project_root = os.path.abspath('.')
    sys.path.insert(0, project_root)
    
    print("Python version:", sys.version)
    print("Working directory:", os.getcwd())
    print("Project root:", project_root)
    
    print("\nPython path:")
    for i, path in enumerate(sys.path, 1):
        print(f"{i}. {path}")
    
    print("\nTrying to import app...")
    try:
        import app
        print("[SUCCESS] Successfully imported app")
        print(f"App module location: {app.__file__}")
        return True
    except ImportError as e:
        print(f"\n[ERROR] Import error: {e}")
        print("\nTraceback:")
        traceback.print_exc()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nTraceback:")
        traceback.print_exc()
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
