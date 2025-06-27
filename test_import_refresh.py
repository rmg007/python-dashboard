"""
Simple test script to check if we can import the refresh_controls module and its functions.
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
        print("\n=== Testing import of refresh_controls module ===")
        
        # Try importing the module
        print("Importing components.refresh_controls...")
        from components import refresh_controls
        print("✅ Successfully imported refresh_controls module")
        
        # Check if register_refresh_callbacks exists
        print("\nChecking for register_refresh_callbacks function...")
        if hasattr(refresh_controls, 'register_refresh_callbacks'):
            print(f"✅ register_refresh_callbacks function exists")
        else:
            print(f"❌ register_refresh_callbacks function not found")
            print(f"Available attributes: {dir(refresh_controls)}")
        
        # Check the _registered_refresh_callbacks set
        print("\nChecking _registered_refresh_callbacks set...")
        if hasattr(refresh_controls, '_registered_refresh_callbacks'):
            print(f"✅ _registered_refresh_callbacks exists: {refresh_controls._registered_refresh_callbacks}")
        else:
            print(f"❌ _registered_refresh_callbacks not found")
        
        # Try importing the register_refresh_callbacks function directly
        print("\nImporting register_refresh_callbacks directly...")
        try:
            from components.refresh_controls import register_refresh_callbacks
            print("✅ Successfully imported register_refresh_callbacks function")
        except Exception as e:
            print(f"❌ Error importing register_refresh_callbacks: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
        
        # Create a minimal Dash app and try to register callbacks
        print("\n=== Testing callback registration with minimal app ===")
        try:
            from dash import Dash
            app = Dash(__name__, suppress_callback_exceptions=True)
            print("✅ Created minimal Dash app")
            
            # Try registering callbacks
            print("Registering refresh callbacks...")
            register_refresh_callbacks(app)
            print("✅ Successfully registered refresh callbacks")
            
            # Check if callbacks were registered
            if hasattr(app, '_callback_list'):
                print(f"Number of callbacks registered: {len(app._callback_list)}")
            else:
                print("No _callback_list attribute found on app")
                
        except Exception as e:
            print(f"❌ Error during callback registration: {type(e).__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
        
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
    print("Starting refresh_controls import test...")
    sys.exit(main())
