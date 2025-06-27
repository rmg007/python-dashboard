"""
UI components for export functionality.
"""
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# Export button IDs (matching those in export_callbacks.py)
EXPORT_BUTTON_IDS = {
    'csv': 'export-csv-btn',
    'excel': 'excel-export-btn',
    'pdf': 'pdf-export-btn',
    'zip': 'zip-export-btn'
}

def create_export_buttons():
    """Create the export button group."""
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
                dbc.Button(
                    [html.I(className="fas fa-clock me-2"), "Schedule Export"],
                    id="schedule-export-btn",
                    color="outline-info",
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
    ])

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
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Preset", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Select(
                                id="export-preset",
                                options=[],
                                placeholder="Select a saved preset (optional)",
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3", id="export-preset-row"),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="export-cancel-btn", color="secondary", className="me-2"),
                dbc.Button("Save as Preset", id="export-save-preset-btn", outline=True, color="info", className="me-2"),
                dbc.Button("Export", id="export-confirm-btn", color="primary"),
            ]),
        ],
        id="export-modal",
        size="md",
        centered=True,
    )

def create_schedule_export_modal():
    """Create the schedule export modal dialog."""
    now = datetime.now()
    default_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    return dbc.Modal(
        [
            dbc.ModalHeader("Schedule Export"),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Name", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Input(
                                id="schedule-name",
                                type="text",
                                placeholder="e.g., Weekly Permit Report",
                                required=True,
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Format", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Select(
                                id="schedule-format",
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
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Frequency", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Select(
                                id="schedule-frequency",
                                options=[
                                    {"label": "Hourly", "value": "hourly"},
                                    {"label": "Daily", "value": "daily"},
                                    {"label": "Weekly", "value": "weekly"},
                                    {"label": "Monthly", "value": "monthly"},
                                ],
                                value="daily",
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Start Time", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Input(
                                id="schedule-start-time",
                                type="time",
                                value=default_time.strftime("%H:%M"),
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Email Notification", width=3, className="text-end"),
                        dbc.Col(
                            dbc.Input(
                                id="schedule-email",
                                type="email",
                                placeholder="email@example.com (optional)",
                                className="mb-2"
                            ),
                            width=9
                        )
                    ], className="mb-3"),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="schedule-cancel-btn", color="secondary", className="me-2"),
                dbc.Button("Schedule", id="schedule-save-btn", color="primary"),
            ]),
        ],
        id="schedule-export-modal",
        size="lg",
        centered=True,
    )

def create_export_history_table():
    """Create a table to display export history."""
    return html.Div([
        html.H4("Export History", className="mt-4 mb-3"),
        dash_table.DataTable(
            id="export-history-table",
            columns=[
                {"name": "Date", "id": "created_at", "type": "datetime"},
                {"name": "Format", "id": "format"},
                {"name": "File", "id": "file_path", "presentation": "markdown"},
                {"name": "Records", "id": "records_exported"},
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={
                "backgroundColor": "#f8f9fa",
                "fontWeight": "bold",
                "border": "1px solid #dee2e6",
            },
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "rgba(0, 116, 217, 0.1)",
                    "border": "1px solid #0074d9",
                }
            ],
            page_size=10,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            row_selectable="single",
            page_action="native",
        ),
    ])

def create_scheduled_exports_table():
    """Create a table to display and manage scheduled exports."""
    return html.Div([
        html.Div([
            html.H4("Scheduled Exports", className="mt-4 mb-3"),
            dbc.Button(
                [html.I(className="fas fa-plus me-2"), "New Scheduled Export"],
                id="new-schedule-btn",
                color="primary",
                className="mb-3"
            ),
        ], className="d-flex justify-content-between align-items-center"),
        dash_table.DataTable(
            id="scheduled-exports-table",
            columns=[
                {"name": "Name", "id": "name"},
                {"name": "Format", "id": "format"},
                {"name": "Frequency", "id": "frequency"},
                {"name": "Next Run", "id": "next_run", "type": "datetime"},
                {"name": "Last Run", "id": "last_run", "type": "datetime"},
                {"name": "Status", "id": "active", "presentation": "dropdown"},
                {"name": "Actions", "id": "id", "presentation": "dropdown"},
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={
                "backgroundColor": "#f8f9fa",
                "fontWeight": "bold",
                "border": "1px solid #dee2e6",
            },
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "rgba(0, 116, 217, 0.1)",
                    "border": "1px solid #0074d9",
                }
            ],
            page_size=10,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            row_selectable="single",
            page_action="native",
            dropdown={
                'active': {
                    'options': [
                        {'label': 'Active', 'value': True},
                        {'label': 'Inactive', 'value': False}
                    ]
                },
                'id': {
                    'options': [
                        {
                            'label': html.Span([
                                html.I(className="fas fa-edit me-2"),
                                'Edit'
                            ]),
                            'value': 'edit'
                        },
                        {
                            'label': html.Span([
                                html.I(className="fas fa-trash-alt me-2"),
                                'Delete'
                            ], className='text-danger'),
                            'value': 'delete'
                        },
                        {
                            'label': html.Span([
                                html.I(className="fas fa-download me-2"),
                                'Download Latest'
                            ]),
                            'value': 'download'
                        }
                    ]
                }
            },
        ),
    ])
