import os
import sys
import chardet
from pathlib import Path

def check_file_encoding(filepath):
    """Check the encoding of a file and detect any encoding issues."""
    try:
        # First, try to read with default encoding
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return 'utf-8', None
    except UnicodeDecodeError:
        try:
            # If UTF-8 fails, try to detect encoding
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Try reading with detected encoding
                try:
                    content = raw_data.decode(encoding)
                    return f"{encoding} (detected)", None
                except Exception as e:
                    return None, f"Failed to decode with detected encoding {encoding}: {e}"
                    
        except Exception as e:
            return None, f"Error detecting encoding: {e}"

def check_line_endings(filepath):
    """Check for mixed or non-UNIX line endings."""
    with open(filepath, 'rb') as f:
        content = f.read()
        
    crlf = b'\r\n' in content
    lf = b'\r\n' not in content and b'\n' in content
    cr = b'\r' in content.replace(b'\r\n', b'')
    
    line_endings = []
    if crlf: line_endings.append('CRLF (Windows)')
    if lf: line_endings.append('LF (Unix)')
    if cr: line_endings.append('CR (Old Mac)')
    
    if not line_endings:
        return 'No line endings found', False
    elif len(line_endings) > 1:
        return 'Mixed: ' + ', '.join(line_endings), True
    else:
        return line_endings[0], line_endings[0] != 'LF (Unix)'

def check_file(filepath):
    """Check a single file for encoding and line ending issues."""
    print(f"\nChecking {filepath}")
    print("=" * (len(str(filepath)) + 9))
    
    # Check encoding
    encoding, error = check_file_encoding(filepath)
    if error:
        print(f"❌ Encoding issue: {error}")
    else:
        print(f"✅ Encoding: {encoding}")
    
    # Check line endings
    line_ending, has_issue = check_line_endings(filepath)
    status = "⚠️ " if has_issue else "✅ "
    print(f"{status}Line endings: {line_ending}")
    
    return not (error or has_issue)

def main():
    # Install chardet if not available
    try:
        import chardet
    except ImportError:
        print("Installing chardet for encoding detection...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
    
    # Get all Python files in the current directory and subdirectories
    root_dir = Path('.')
    python_files = list(root_dir.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to check")
    
    # Check each file
    all_ok = True
    for filepath in python_files:
        # Skip virtual environment directories
        if 'venv' in str(filepath).split(os.sep):
            continue
            
        if not check_file(filepath):
            all_ok = False
    
    if all_ok:
        print("\n✅ All files have proper encoding and line endings")
    else:
        print("\n❌ Some files have encoding or line ending issues")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
