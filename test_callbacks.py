"""
Minimal test script to identify duplicate callback registrations.
"""
import os
import logging
from pathlib import Path
from dash import Dash, html

# Configure logging
log_file = 'test_callbacks.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to {os.path.abspath(log_file)}")

def test_callback_registration(callback_func, name):
    """Test registration of a single callback function."""
    try:
        logger.info(f"Testing callback: {name}")
        app = Dash(__name__)
        
        # Create a minimal layout
        app.layout = html.Div([
            html.Div(id='test-output'),
            html.Button('Test', id='test-button')
        ])
        
        # Register the callback
        callback_func(app)
        
        logger.info(f"Successfully registered callback: {name}")
        return True
    except Exception as e:
        logger.error(f"Error registering callback {name}: {e}", exc_info=True)
        return False

def main():
    """Test registration of all callbacks one by one."""
    # Import callback functions
    from callbacks.kpi_callbacks import register_kpi_callbacks
    from callbacks.visual_callbacks import register_visual_callbacks
    from callbacks.layout_callbacks import register_layout_callbacks
    from callbacks.export_callbacks import register_export_callbacks
    from components.refresh_controls import register_refresh_callbacks
    
    # List of callbacks to test
    callbacks = [
        (lambda app: register_kpi_callbacks(app), "KPI Callbacks"),
        (lambda app: register_visual_callbacks(app), "Visual Callbacks"),
        (lambda app: register_layout_callbacks(app), "Layout Callbacks"),
        (lambda app: register_export_callbacks(app, None), "Export Callbacks"),
        (lambda app: register_refresh_callbacks(app), "Refresh Callbacks"),
    ]
    
    # Test each callback
    for callback_func, name in callbacks:
        if not test_callback_registration(callback_func, name):
            logger.error(f"Failed to register callback: {name}")
            return
    
    logger.info("All callbacks registered successfully")

if __name__ == "__main__":
    main()
