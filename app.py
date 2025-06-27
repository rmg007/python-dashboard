import os
import logging
from pathlib import Path
from flask import send_from_directory, abort
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import layout and callbacks
from layout.base import serve_layout, custom_css
from callbacks.kpi_callbacks import register_kpi_callbacks
from callbacks.visual_callbacks import register_visual_callbacks
from callbacks.layout_callbacks import register_layout_callbacks
from callbacks.export_callbacks import register_export_callbacks, create_export_buttons
from components.export_utils import set_export_dir

# Initialize the Dash app
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/gridstack.js/7.2.3/gridstack-all.js",
        "https://cdnjs.cloudflare.com/ajax/libs/gridstack.js/7.2.3/gridstack.min.css"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5"}
    ]
)
app.title = "Permit Dashboard"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='w', encoding='utf-8')
    ]
)

# Set log level for specific noisy loggers
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('dash').setLevel(logging.INFO)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("Starting application")

# Add custom CSS
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{app.title}</title>
        {{%favicon%}}
        {{%css%}}
        <style>{custom_css}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# Set up export directory
export_dir = os.path.join(os.getcwd(), 'static', 'exports')
os.makedirs(export_dir, exist_ok=True)
set_export_dir(export_dir)

# Add route to serve exported files
@app.server.route('/exports/<user_id>/<path:filename>')
def serve_export(user_id, filename):
    """Serve exported files with security checks."""
    try:
        # Security: Prevent directory traversal
        safe_filename = os.path.basename(filename)
        user_dir = os.path.join(export_dir, user_id)
        
        # Verify the file exists and is within the export directory
        if not os.path.exists(os.path.join(user_dir, safe_filename)):
            abort(404)
            
        return send_from_directory(user_dir, safe_filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error serving export file: {e}")
        abort(404)

# Import and initialize scheduler
from scheduler.schedule_jobs import start_scheduler

# Start the scheduler if enabled
if os.getenv('ENABLE_SCHEDULED_JOBS', 'False').lower() == 'true':
    logger.info("Starting scheduler with scheduled jobs enabled")
    if start_scheduler():
        logger.info("Scheduler started successfully")
    else:
        logger.warning("Failed to start scheduler")
else:
    logger.info("Scheduled jobs are disabled (ENABLE_SCHEDULED_JOBS=False)")

# Set the layout
app.layout = serve_layout()

# Initialize database
from db.connection import init_db
init_db()

# Register all callbacks with error handling
try:
    logger.info("Registering KPI callbacks...")
    register_kpi_callbacks(app)
    logger.info("Successfully registered KPI callbacks")
    
    logger.info("Registering visual callbacks...")
    register_visual_callbacks(app)
    logger.info("Successfully registered visual callbacks")
    
    logger.info("Registering layout callbacks...")
    register_layout_callbacks(app)
    logger.info("Successfully registered layout callbacks")
    
    logger.info("Registering export callbacks...")
    # Temporarily pass None for db parameter to export callbacks
    register_export_callbacks(app, None)
    logger.info("Successfully registered export callbacks")
    
    # Register refresh controls callbacks
    from components.refresh_controls import register_refresh_callbacks
    logger.info("Registering refresh callbacks...")
    register_refresh_callbacks(app)
    logger.info("Successfully registered refresh callbacks")
    
except Exception as e:
    logger.error(f"Error registering callbacks: {e}", exc_info=True)
    raise

# Add external scripts for draggable functionality
app.scripts.append_script({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/react-grid-layout/1.3.4/react-grid-layout.min.js'
})

if __name__ == "__main__":
    # Configure logging to console
    import sys
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    
    # Set log level for specific loggers
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('dash').setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")
    
    try:
        # Initialize database and run migrations
        from db.connection import init_db
        from db.migrations import run_migrations
        
        logger.info("Initializing database...")
        init_db()
        run_migrations()
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 8050))
        debug = os.environ.get('FLASK_ENV', 'development').lower() == 'development'
        
        logger.info(f"Starting Dash server on port {port} (debug={debug})...")
        
        # Start the app with appropriate settings
        try:
            app.run_server(
                host='0.0.0.0',
                port=port,
                debug=debug,
                use_reloader=False,  # Disable reloader to simplify debugging
                dev_tools_hot_reload=debug,
                dev_tools_ui=debug,
                dev_tools_props_check=debug
            )
        except Exception as e:
            # Log the full error message and traceback
            import traceback
            error_msg = f"Error starting Dash server: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logger.error(error_msg)
            print("\n" + "="*80)
            print("FULL ERROR MESSAGE:")
            print("="*80)
            print(error_msg)
            print("="*80 + "\n")
            raise
            
    except Exception as e:
        # Log the full error message and traceback
        import traceback
        error_msg = f"Failed to start application: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        logger.error(error_msg)
        print("\n" + "="*80)
        print("FULL ERROR MESSAGE:")
        print("="*80)
        print(error_msg)
        print("="*80 + "\n")
        raise

# Make the server available for deployment
server = app.server

# Add custom CSS
app.css.append_css({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
})
