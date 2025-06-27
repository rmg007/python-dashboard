"""
Test script to isolate which callback registration is causing the DuplicateCallback error.
"""

import sys
import traceback
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_callback_registration():
    """Test each callback registration function separately."""
    try:
        print("\n=== Creating Dash app ===")
        from dash import Dash
        app = Dash(__name__, suppress_callback_exceptions=True)
        
        # Set up a minimal layout
        from dash import html
        app.layout = html.Div([
            html.Div(id="refresh-status"),
            html.Button("Refresh", id="refresh-btn"),
            html.Div(id="last-refresh-time"),
            html.Div(id="job-history-modal"),
            html.Button("History", id="history-btn"),
            html.Button("Close", id="close-history"),
            html.Div(id="job-history-content"),
            html.Div(id="last-refresh-store", style={"display": "none"})
        ])
        
        # Test each callback registration function separately
        print("\n=== Testing KPI callbacks ===")
        from callbacks.kpi_callbacks import register_kpi_callbacks
        register_kpi_callbacks(app)
        print("✅ KPI callbacks registered successfully")
        
        print("\n=== Testing visual callbacks ===")
        from callbacks.visual_callbacks import register_visual_callbacks
        register_visual_callbacks(app)
        print("✅ Visual callbacks registered successfully")
        
        print("\n=== Testing layout callbacks ===")
        from callbacks.layout_callbacks import register_layout_callbacks
        register_layout_callbacks(app)
        print("✅ Layout callbacks registered successfully")
        
        print("\n=== Testing export callbacks ===")
        from callbacks.export_callbacks import register_export_callbacks
        register_export_callbacks(app, None)
        print("✅ Export callbacks registered successfully")
        
        print("\n=== Testing refresh callbacks ===")
        from components.refresh_controls import register_refresh_callbacks
        register_refresh_callbacks(app)
        print("✅ Refresh callbacks registered successfully")
        
        # Try registering refresh callbacks again (this should be skipped due to our prevention logic)
        print("\n=== Testing refresh callbacks (second registration) ===")
        register_refresh_callbacks(app)
        print("✅ Second refresh callbacks registration handled correctly")
        
        print("\n=== All callbacks registered successfully! ===")
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"ERROR: {str(e)}")
        print("-"*80)
        print("TRACEBACK:")
        traceback.print_exc()
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    print("Starting callback registration test...")
    success = test_callback_registration()
    
    if success:
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Test failed with errors.")
    
    print("Test complete.")
