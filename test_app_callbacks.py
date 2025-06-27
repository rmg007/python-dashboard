"""
Test script to diagnose callback registration issues in app.py.
This script will import the app from app.py but won't run the server.
"""

import sys
import traceback
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    try:
        print("\n=== Testing app.py callback registration ===")
        
        # Import the app module but don't run the server
        print("Importing app from app.py...")
        
        # First, modify sys.modules to avoid circular imports
        if 'app' in sys.modules:
            print("Removing existing 'app' from sys.modules to avoid conflicts")
            del sys.modules['app']
        
        # Import the app
        try:
            from app import app
            print("✅ Successfully imported app from app.py")
        except Exception as e:
            print(f"❌ Error importing app: {type(e).__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return 1
        
        # Check if callbacks were registered
        print("\n=== Checking registered callbacks ===")
        if hasattr(app, '_callback_list'):
            print(f"Number of callbacks registered: {len(app._callback_list)}")
            
            # Check for duplicate outputs
            print("\n=== Checking for duplicate outputs ===")
            outputs = {}
            for i, callback in enumerate(app._callback_list):
                if hasattr(callback, 'output') and callback.output:
                    for output in callback.output:
                        output_key = f"{output.component_id}.{output.component_property}"
                        if output_key in outputs:
                            print(f"⚠️ DUPLICATE OUTPUT FOUND: {output_key}")
                            print(f"  First defined in callback #{outputs[output_key]}")
                            print(f"  Duplicated in callback #{i}")
                        else:
                            outputs[output_key] = i
            
            if not outputs:
                print("No duplicate outputs found.")
        else:
            print("No _callback_list attribute found on app")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        print("-"*80)
        print("TRACEBACK:")
        traceback.print_exc()
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    print("Starting app.py callback registration test...")
    sys.exit(main())
