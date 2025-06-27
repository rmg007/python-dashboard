"""
UI components for manual data refresh and job status.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import time
from datetime import datetime
import json

# Import job runner and logger
from etl.refresh_pipeline import run_etl_pipeline
from db.job_logger import get_job_history, log_job

# Set to track registered callbacks
_registered_refresh_callbacks = set()

def create_refresh_controls():
    """
    Create the refresh controls component.
    
    Returns:
        dbc.Card: A card containing refresh controls and status
    """
    return dbc.Card(
        [
            dbc.CardHeader("Data Refresh"),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            dbc.Button(
                                ["Refresh Data ", 
                                 dbc.Spinner(size="sm", color="light", className="ms-2")],
                                id="refresh-btn",
                                color="primary",
                                className="me-2",
                                n_clicks=0,
                                disabled=False
                            ),
                            dbc.Button(
                                ["View History"],
                                id="history-btn",
                                color="secondary",
                                outline=True,
                                className="me-2"
                            ),
                            html.Div(id="last-refresh-time", className="text-muted mt-2"),
                            html.Div(id="refresh-status", className="mt-2"),
                            
                            # Hidden div to store the last refresh time
                            dcc.Store(id='last-refresh-store', data={"last_refresh": None}),
                            
                            # Modal for job history
                            dbc.Modal(
                                [
                                    dbc.ModalHeader("Job History"),
                                    dbc.ModalBody(
                                        [
                                            dbc.Spinner(
                                                html.Div(id="job-history-content"),
                                                color="primary"
                                            )
                                        ]
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", 
                                            id="close-history", 
                                            className="ms-auto"
                                        )
                                    ),
                                ],
                                id="job-history-modal",
                                size="lg",
                                scrollable=True,
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="mb-4",
    )

def load_job_history(is_open):
    """Load job history when the modal is opened."""
    import dash_bootstrap_components as dbc
    from dash import html
    
    if not is_open:
        return None
    
    # Get job history from database
    job_history = get_job_history(limit=50)
    
    if not job_history:
        return html.Div("No job history found.")
    
    # Create a table to display job history
    header = html.Thead(html.Tr([
        html.Th("Job Name"),
        html.Th("Status"),
        html.Th("Start Time"),
        html.Th("End Time"),
        html.Th("Duration"),
        html.Th("Message")
    ]))
    
    rows = []
    for job in job_history:
        # Calculate duration
        if job["start_time"] and job["end_time"]:
            start = job["start_time"]
            end = job["end_time"]
            duration = end - start
            duration_str = f"{duration.total_seconds():.1f}s"
        else:
            duration_str = "N/A"
        
        # Format times
        start_str = job["start_time"].strftime("%Y-%m-%d %H:%M:%S") if job["start_time"] else "N/A"
        end_str = job["end_time"].strftime("%Y-%m-%d %H:%M:%S") if job["end_time"] else "N/A"
        
        # Create row
        row = html.Tr([
            html.Td(job["job_name"]),
            html.Td(html.Span("✅ " + job["status"]) if job["status"] == "success" else html.Span("❌ " + job["status"])),
            html.Td(start_str),
            html.Td(end_str),
            html.Td(duration_str),
            html.Td(job["message"] or "")
        ])
        rows.append(row)
    
    body = html.Tbody(rows)
    table = dbc.Table([header, body], striped=True, bordered=True, hover=True)
    
    return html.Div([
        html.H4("Job History"),
        table
    ])

def toggle_job_history_modal(open_clicks, close_clicks, is_open):
    """Toggle the job history modal."""
    from dash import callback_context
    import dash
    
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Toggle based on which button was clicked
    if button_id == "history-btn":
        return True
    elif button_id == "close-history":
        return False
    
    return is_open

def handle_refresh(n_clicks, last_refresh_data):
    """Handle manual refresh button click."""
    import time
    import json
    from datetime import datetime
    from etl.refresh_pipeline import run_refresh_pipeline
    from db.job_logger import log_job_run
    
    if n_clicks is None:
        return "Ready", False, last_refresh_data, "Last refresh: Never"
    
    # Initialize last_refresh_data if None
    if last_refresh_data is None:
        last_refresh_data = {"last_refresh": None, "refresh_count": 0}
    else:
        try:
            last_refresh_data = json.loads(last_refresh_data) if isinstance(last_refresh_data, str) else last_refresh_data
        except:
            last_refresh_data = {"last_refresh": None, "refresh_count": 0}
    
    # Run the refresh pipeline
    start_time = time.time()
    result = run_etl_pipeline()
    end_time = time.time()
    duration = end_time - start_time
    
    # Extract success/failure from result
    success = result.get("status") == "success"
    message = result.get("message") if success else result.get("error", "Unknown error")
    
    # Log the job run
    log_job(
        job_name="manual_refresh",
        status="SUCCESS" if success else "FAILED",
        error_message=None if success else message,
        duration=duration,
        details={"triggered_by": "user"}
    )
    
    # Update last refresh data
    refresh_count = last_refresh_data.get("refresh_count", 0) + 1
    last_refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_refresh_data = {
        "last_refresh": last_refresh_time,
        "refresh_count": refresh_count
    }
    
    # Format status message
    status = f"✅ Refresh complete ({duration:.1f}s)" if success else f"❌ Refresh failed ({duration:.1f}s): {message}"
    
    # Format last refresh text
    last_refresh_text = f"Last refresh: {last_refresh_time}"
    
    return (
        status,
        False,  # Enable the button
        json.dumps(last_refresh_data),
        last_refresh_text
    )

def register_refresh_callbacks(app):
    """Register callbacks for the refresh controls.
    
    Args:
        app: The Dash application instance
    """
    import logging
    from dash import Input, Output, State
    
    # Configure logging for this module
    logger = logging.getLogger(__name__)
    
    # Skip if already registered
    if 'refresh_controls_main' in _registered_refresh_callbacks:
        logger.warning("Skipping duplicate registration of refresh callbacks")
        return
    
    # Mark as registered
    _registered_refresh_callbacks.add('refresh_controls_main')
    logger.info("Registering refresh callbacks")
    
    # Register the refresh button callback
    app.callback(
        [
            Output("refresh-status", "children"),
            Output("refresh-btn", "disabled"),
            Output("last-refresh-store", "data"),
            Output("last-refresh-time", "children"),
        ],
        [Input("refresh-btn", "n_clicks")],
        [State("last-refresh-store", "data")],
        prevent_initial_call=True
    )(handle_refresh)
    
    # Register the job history modal toggle callback
    app.callback(
        Output("job-history-modal", "is_open"),
        [Input("history-btn", "n_clicks"), 
         Input("close-history", "n_clicks")],
        [State("job-history-modal", "is_open")],
        prevent_initial_call=True
    )(toggle_job_history_modal)
    
    # Register the job history content callback
    app.callback(
        Output("job-history-content", "children"),
        [Input("job-history-modal", "is_open")],
        prevent_initial_call=True
    )(load_job_history)
    
    logger.info("Refresh control callbacks registered successfully")
