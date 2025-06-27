"""
Test script specifically focused on refresh callbacks to diagnose DuplicateCallback errors.
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
        print("Creating minimal Dash app...")
        from dash import Dash
        app = Dash(__name__, suppress_callback_exceptions=True)
        
        print("Importing refresh_controls module...")
        from components import refresh_controls
        
        # Check if the module has the expected set
        print(f"_registered_refresh_callbacks set exists: {hasattr(refresh_controls, '_registered_refresh_callbacks')}")
        if hasattr(refresh_controls, '_registered_refresh_callbacks'):
            print(f"Current content of _registered_refresh_callbacks: {refresh_controls._registered_refresh_callbacks}")
        
        print("Registering refresh callbacks first time...")
        refresh_controls.register_refresh_callbacks(app)
        
        print("First registration successful!")
        
        # Try registering again to see if our duplicate prevention works
        print("Registering refresh callbacks second time...")
        refresh_controls.register_refresh_callbacks(app)
        
        print("Second registration successful!")
        
        # Check the set after registrations
        if hasattr(refresh_controls, '_registered_refresh_callbacks'):
            print(f"Content of _registered_refresh_callbacks after registrations: {refresh_controls._registered_refresh_callbacks}")
        
        print("Test completed successfully!")
        return 0
    except Exception as e:
        print("\n" + "="*80)
        print(f"ERROR: {str(e)}")
        print("-"*80)
        print("TRACEBACK:")
        traceback.print_exc()
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
