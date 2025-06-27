"""
Test script to isolate and diagnose DuplicateCallback errors.
"""

import logging
import sys
import traceback
from pathlib import Path

# Set up logging to capture all output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('duplicate_callback_test.log', mode='w')
    ]
)

logger = logging.getLogger(__name__)

def test_refresh_callbacks():
    """Test refresh callbacks in isolation."""
    try:
        logger.info("Testing refresh callbacks...")
        
        # Import only what we need
        from dash import Dash
        from components.refresh_controls import register_refresh_callbacks
        
        # Create a minimal app
        logger.info("Creating minimal Dash app...")
        app = Dash(__name__, suppress_callback_exceptions=True)
        
        # Register callbacks
        logger.info("Registering refresh callbacks...")
        register_refresh_callbacks(app)
        
        logger.info("Refresh callbacks registered successfully!")
        return True
        
    except Exception as e:
        error_msg = f"Error in test_refresh_callbacks: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False

if __name__ == "__main__":
    logger.info("Starting duplicate callback test...")
    
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Run the test
    success = test_refresh_callbacks()
    
    if success:
        logger.info("✅ Test completed successfully! No duplicate callback errors detected.")
    else:
        logger.error("❌ Test failed with errors. Check the log file for details.")
    
    logger.info("Test complete.")
