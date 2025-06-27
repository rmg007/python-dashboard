"""
Test script to verify if our changes to refresh_controls.py have resolved the DuplicateCallback error.
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
        from dash import Dash, html, dcc
        import logging
        
        # Configure logging to both console and file
        log_file = os.path.join(os.path.dirname(__file__), 'test_refresh_debug.log')
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='w'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger = logging.getLogger(__name__)
        logger.info(f"Logging to {log_file}")
        
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
        
        print("✅ Basic app created successfully")
        
        # Now try to register the refresh callbacks
        print("\n=== Importing refresh_controls module ===")
        from components.refresh_controls import register_refresh_callbacks
        
        # Register refresh callbacks with detailed error handling
        print("\n=== Registering refresh callbacks ===")
        try:
            # Inspect the refresh_controls module
            import inspect
            from components import refresh_controls
            print(f"refresh_controls module location: {inspect.getfile(refresh_controls)}")
            print(f"_registered_refresh_callbacks: {refresh_controls._registered_refresh_callbacks}")
            
            # Register callbacks
            register_refresh_callbacks(app)
            print("✅ Refresh callbacks registered successfully")
            print(f"_registered_refresh_callbacks after registration: {refresh_controls._registered_refresh_callbacks}")
        except Exception as e:
            print(f"❌ Error registering refresh callbacks: {type(e).__name__}: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            return 1
        
        # Try running the server briefly
        print("\n=== Starting server (will run for 3 seconds) ===")
        import threading
        import time
        import os
        
        def stop_server():
            time.sleep(3)
            print("Stopping server...")
            os._exit(0)
        
        # Start a thread to stop the server after 3 seconds
        threading.Thread(target=stop_server, daemon=True).start()
        
        try:
            # Inspect the app's callbacks before starting the server
            print("\n=== Inspecting registered callbacks ===")
            if hasattr(app, '_callback_list'):
                print(f"Number of callbacks: {len(app._callback_list)}")
                for i, callback in enumerate(app._callback_list):
                    print(f"Callback {i+1}: {callback}")
            else:
                print("No _callback_list attribute found on app")
                
            print("\nStarting server on port 8052...")
            app.run_server(debug=False, port=8052)
        except Exception as e:
            print(f"\n❌ Error running server: {type(e).__name__}: {str(e)}")
            print("Detailed error:")
            error_details = traceback.format_exc()
            print(error_details)
            
            # Write error to file for better analysis
            with open(os.path.join(os.path.dirname(__file__), 'error_details.txt'), 'w') as f:
                f.write(f"Error type: {type(e).__name__}\n")
                f.write(f"Error message: {str(e)}\n\n")
                f.write("Traceback:\n")
                f.write(error_details)
            
            print("\nError details written to error_details.txt")
            return 1
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        print("-"*80)
        print("TRACEBACK:")
        error_details = traceback.format_exc()
        print(error_details)
        print("="*80 + "\n")
        
        # Write error to file for better analysis
        with open(os.path.join(os.path.dirname(__file__), 'error_details.txt'), 'w') as f:
            f.write(f"Error type: {type(e).__name__}\n")
            f.write(f"Error message: {str(e)}\n\n")
            f.write("Traceback:\n")
            f.write(error_details)
        
        print("\nError details written to error_details.txt")
        return 1

if __name__ == "__main__":
    print("Starting test with new refresh_controls implementation...")
    sys.exit(main())
