"""
Minimal test script to diagnose DuplicateCallback error.
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
        print("\n=== Creating minimal Dash app ===")
        from dash import Dash, html, dcc
        
        # Create a minimal app with a simple layout
        app = Dash(__name__, suppress_callback_exceptions=True)
        app.layout = html.Div([
            html.Div(id="refresh-status"),
            html.Button("Refresh", id="refresh-btn"),
            html.Div(id="last-refresh-time"),
            html.Div(id="last-refresh-store", style={"display": "none"})
        ])
        
        # Import only the refresh_controls module
        print("\n=== Importing refresh_controls module ===")
        from components import refresh_controls
        
        # Modify the _registered_refresh_callbacks set to ensure it's empty
        print("\n=== Checking _registered_refresh_callbacks set ===")
        if hasattr(refresh_controls, '_registered_refresh_callbacks'):
            refresh_controls._registered_refresh_callbacks.clear()
            print(f"Cleared _registered_refresh_callbacks set")
        
        # Register refresh callbacks
        print("\n=== Registering refresh callbacks ===")
        refresh_controls.register_refresh_callbacks(app)
        print("✅ First registration successful")
        
        # Try running the server to see if it works
        print("\n=== Starting server (will run for 1 second) ===")
        import threading
        import time
        
        def stop_server():
            time.sleep(1)
            import os
            os._exit(0)
        
        # Start a thread to stop the server after 1 second
        threading.Thread(target=stop_server).start()
        
        try:
            app.run_server(debug=False, port=8051)
        except SystemExit:
            print("Server stopped as expected")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        print("-"*80)
        print("TRACEBACK:")
        traceback.print_exc()
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    print("Starting minimal test...")
    sys.exit(main())
