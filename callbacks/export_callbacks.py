"""
Callbacks for handling export functionality in the dashboard.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from dash import Input, Output, State, html, dcc, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from components.export_utils import (
    export_to_csv, export_to_excel, export_to_pdf, create_zip_archive,
    mask_sensitive_columns, cleanup_old_exports
)

# Configure logging
logger = logging.getLogger(__name__)

# Export button IDs
EXPORT_BUTTON_IDS = {
    'csv': 'export-csv-btn',
    'excel': 'export-excel-btn',
    'pdf': 'export-pdf-btn',
    'zip': 'export-zip-btn'
}

# Track registered callbacks to prevent duplicates
_registered_callbacks = set()

def register_export_callbacks(app, db):
    """Register all export-related callbacks."""
    callback_id = 'export_callbacks_main'
    
    # Skip if already registered
    if callback_id in _registered_callbacks:
        return
        
    _registered_callbacks.add(callback_id)
    
    @app.callback(
        [
            Output("export-status", "children"),
            Output("export-download-link", "href"),
            Output("export-download-link", "style"),
            Output("export-modal", "is_open"),
        ],
        [
            Input(EXPORT_BUTTON_IDS['csv'], "n_clicks"),
            Input(EXPORT_BUTTON_IDS['excel'], "n_clicks"),
            Input(EXPORT_BUTTON_IDS['pdf'], "n_clicks"),
            Input(EXPORT_BUTTON_IDS['zip'], "n_clicks"),
            Input("export-confirm-btn", "n_clicks"),
        ],
        [
            State("filtered-table", "data"),
            State("filtered-table", "columns"),
            State("current-user", "data"),
            State("export-filename", "value"),
            State("export-format", "value"),
        ],
        prevent_initial_call=True,
    )
    def handle_export(
        csv_clicks, excel_clicks, pdf_clicks, zip_clicks, confirm_clicks,
        table_data, table_columns, current_user, filename, export_format
    ):
        """Handle export button clicks and generate export files."""
        if not current_user or 'id' not in current_user or 'role' not in current_user:
            return "Error: User not authenticated", "", {"display": "none"}, False
        
        # Get the button that triggered the callback
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Handle export preview (when any export button is clicked)
        if button_id in EXPORT_BUTTON_IDS.values():
            if not table_data:
                return "No data to export", "", {"display": "none"}, False
                
            # Show export options modal
            return (
                "",  # status
                "",  # download link
                {"display": "none"},  # download link style
                True,  # show modal
            )
        
        # Handle export confirmation
        elif button_id == "export-confirm-btn" and confirm_clicks:
            if not table_data or not filename:
                return "Error: Missing data or filename", "", {"display": "none"}, False
            
            try:
                # Convert table data to DataFrame
                df = pd.DataFrame(table_data)
                
                # Apply role-based column masking
                df = mask_sensitive_columns(df, current_user.get('role', 'viewer'))
                
                # Generate export
                user_id = str(current_user['id'])
                base_name = filename or "export"
                
                if export_format == 'csv':
                    file_path = export_to_csv(df, user_id, base_name)
                elif export_format == 'excel':
                    file_path = export_to_excel(df, user_id, base_name)
                elif export_format == 'pdf':
                    file_path = export_to_pdf(df, user_id, base_name, f"{base_name.title()} Report")
                elif export_format == 'zip':
                    # Create multiple formats and zip them
                    csv_path = export_to_csv(df, user_id, base_name)
                    pdf_path = export_to_pdf(df, user_id, base_name, f"{base_name.title()} Report")
                    file_path = create_zip_archive([csv_path, pdf_path], user_id, base_name)
                else:
                    return f"Unsupported format: {export_format}", "", {"display": "none"}, False
                
                # Log the export
                log_export(db, {
                    'user_id': user_id,
                    'format': export_format,
                    'file_path': file_path,
                    'rows_exported': len(df),
                    'exported_at': datetime.now().isoformat(),
                    'metadata': {
                        'filename': filename,
                        'columns': list(df.columns),
                        'role': current_user.get('role')
                    }
                })
                
                # Return download link
                download_path = f"/exports/{user_id}/{os.path.basename(file_path)}"
                return (
                    "Export completed successfully!",
                    download_path,
                    {"display": "inline-block"},
                    False
                )
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}", exc_info=True)
                return f"Export failed: {str(e)}", "", {"display": "none"}, False
        
        # Default return if no conditions met
        raise PreventUpdate
    
    # Function to initialize the export system
    def init_export_system():
        # Ensure export directory exists
        export_dir = os.path.join(os.getcwd(), 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Clean up old exports on startup
        try:
            cleanup_old_exports(days=30)
        except Exception as e:
            logger.error(f"Error cleaning up old exports: {e}")
    
    # Call the initialization function immediately
    init_export_system()


def log_export(db, export_data):
    """
    Log export operation to the database.
    
    Args:
        db: Database connection object (not used, kept for backward compatibility)
        export_data: Dictionary containing export data to log
    """
    try:
        # If db is None, use the get_connection function from db.connection
        if db is None:
            from db.connection import get_connection
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO export_logs 
                    (user_id, format, file_path, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        export_data.get('user_id', 'anonymous'),
                        export_data.get('format', 'unknown'),
                        export_data.get('file_path', ''),
                        export_data.get('exported_at', datetime.now().isoformat()),
                        json.dumps(export_data.get('metadata', {}))
                    )
                )
                conn.commit()
        else:
            # For backward compatibility with SQLAlchemy-style connection
            with db.engine.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO export_logs 
                    (user_id, format, file_path, created_at, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        export_data.get('user_id', 'anonymous'),
                        export_data.get('format', 'unknown'),
                        export_data.get('file_path', ''),
                        export_data.get('exported_at', datetime.now().isoformat()),
                        json.dumps(export_data.get('metadata', {}))
                    )
                )
                conn.commit()
    except Exception as e:
        logger.error(f"Failed to log export: {e}", exc_info=True)
        # Re-raise the exception to be handled by the caller
        raise


def create_export_modal():
    """Create the export options modal dialog."""
    return dbc.Modal(
        [
            dbc.ModalHeader("Export Options"),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Filename", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Input(
                                id="export-filename",
                                type="text",
                                placeholder="e.g., permits_export",
                                value="permits_export",
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Format", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Select(
                                id="export-format",
                                options=[
                                    {"label": "CSV", "value": "csv"},
                                    {"label": "Excel", "value": "excel"},
                                    {"label": "PDF", "value": "pdf"},
                                    {"label": "ZIP (CSV + PDF)", "value": "zip"},
                                ],
                                value="csv",
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3")
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="export-cancel-btn", color="secondary", className="me-2"),
                dbc.Button("Export", id="export-confirm-btn", color="primary"),
            ]),
        ],
        id="export-modal",
        size="md",
        centered=True,
    )


def create_export_buttons():
    """Create export button group."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-file-csv me-2"), "CSV"],
                    id=EXPORT_BUTTON_IDS['csv'],
                    color="outline-primary",
                    className="me-2 mb-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-file-excel me-2"), "Excel"],
                    id=EXPORT_BUTTON_IDS['excel'],
                    color="outline-success",
                    className="me-2 mb-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-file-pdf me-2"), "PDF"],
                    id=EXPORT_BUTTON_IDS['pdf'],
                    color="outline-danger",
                    className="me-2 mb-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-file-archive me-2"), "ZIP"],
                    id=EXPORT_BUTTON_IDS['zip'],
                    color="outline-secondary",
                    className="me-2 mb-2"
                ),
            ], width=12, className="mb-3"),
        ]),
        # Status message and download link
        html.Div(id="export-status", className="mt-2"),
        html.A(
            id="export-download-link",
            children="Download File",
            download="",
            target="_blank",
            className="btn btn-success mt-2",
            style={"display": "none"}
        ),
        # Export modal
        create_export_modal()
    ])
