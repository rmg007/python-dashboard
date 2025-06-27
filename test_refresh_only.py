"""
Ultra-minimal test script to diagnose DuplicateCallback error in refresh callbacks.
"""

import sys
import traceback
import os
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    try:
        print("\n=== Creating minimal Dash app ===")
        from dash import Dash, html, dcc, Input, Output, State
        
        # Create a minimal app with only the components needed for refresh callbacks
        app = Dash(__name__, suppress_callback_exceptions=True)
        app.layout = html.Div([
            html.Div(id="refresh-status"),
            html.Button("Refresh", id="refresh-btn"),
            html.Div(id="last-refresh-time"),
            html.Div(id="last-refresh-store", style={"display": "none"}),
            html.Button("History", id="history-btn"),
            html.Button("Close", id="close-history"),
            html.Div(id="job-history-modal"),
            html.Div(id="job-history-content")
        ])
        
        # Define a simple callback to test if the app works
        @app.callback(
            Output("refresh-status", "children"),
            Input("refresh-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def test_callback(n_clicks):
            return f"Button clicked {n_clicks} times"
        
        print("✅ Basic app and test callback created successfully")
        
        # Now try to register the refresh callbacks
        print("\n=== Importing refresh_controls module ===")
        from components import refresh_controls
        
        # Clear the registry to ensure we start fresh
        print("\n=== Clearing callback registry ===")
        if hasattr(refresh_controls, '_registered_refresh_callbacks'):
            refresh_controls._registered_refresh_callbacks.clear()
            print(f"✅ Cleared _registered_refresh_callbacks set")
        
        # Register refresh callbacks with detailed error handling
        print("\n=== Registering refresh callbacks ===")
        try:
            refresh_controls.register_refresh_callbacks(app)
            print("✅ Refresh callbacks registered successfully")
        except Exception as e:
            print(f"❌ Error registering refresh callbacks: {type(e).__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return 1
        
        # Try running the server briefly
        print("\n=== Starting server (will run for 2 seconds) ===")
        import threading
        import time
        
        def stop_server():
            time.sleep(2)
            print("Stopping server...")
            os._exit(0)
        
        # Start a thread to stop the server after 2 seconds
        threading.Thread(target=stop_server, daemon=True).start()
        
        try:
            print("Starting server on port 8051...")
            app.run_server(debug=False, port=8051)
        except SystemExit:
            print("Server stopped as expected")
        except Exception as e:
            print(f"❌ Error running server: {type(e).__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return 1
        
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
    print("Starting ultra-minimal refresh test...")
    sys.exit(main())
