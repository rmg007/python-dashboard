"""
Layout Overrides component for the Admin Dashboard.

Allows administrators to customize the dashboard layout for users.
"""
from dash import html, dcc, Input, Output, State, callback, no_update, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json
import uuid

from db.user_queries import get_user, update_user, log_admin_event

def build_layout_overrides():
    """Build the layout overrides interface."""
    return html.Div([
        html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
            html.H3("Layout Overrides", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-question-circle me-2"), "Help"],
                id="layout-help-btn",
                color="link",
                className="text-muted"
            )
        ]),
        
        # Help alert
        dbc.Alert(
            [
                html.H4("About Layout Overrides", className="alert-heading"),
                html.P("""
                    Use this tool to customize the dashboard layout for specific users. 
                    You can modify the position, visibility, and configuration of dashboard 
                    components for individual users.
                """),
                html.Hr(),
                html.P("""
                    Changes made here will override the default layout for the selected user. 
                    To restore the default layout, simply delete the override.
                """, className="mb-0")
            ],
            id="layout-help-alert",
            color="info",
            is_open=False,
            dismissable=True,
            className="mb-4"
        ),
        
        # User selection
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.H5("Select User", className="card-title mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText("User"),
                            dcc.Dropdown(
                                id="layout-user-select",
                                placeholder="Search for a user...",
                                className="flex-grow-1"
                            )
                        ])
                    ], md=8),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-user-plus me-2"), "Create New Preset"],
                            id="create-preset-btn",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=4)
                ]),
                html.Div(id="user-layout-info", className="mt-3")
            ])
        ]),
        
        # Layout editor
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
                    html.H5("Layout Editor", className="mb-0"),
                    dbc.ButtonGroup([
                        dbc.Button(
                            [html.I(className="fas fa-eye me-2"), "Preview Layout"],
                            id="preview-layout-btn",
                            color="outline-primary",
                            size="sm"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-save me-2"), "Save Changes"],
                            id="save-layout-btn",
                            color="primary",
                            size="sm",
                            disabled=True
                        )
                    ])
                ]),
                
                # Layout grid
                html.Div(className="layout-grid", children=[
                    # Header
                    html.Div(className="layout-header", children=[
                        html.Div(className="layout-item", children=[
                            html.Div(className="layout-item-header", children=[
                                "Header",
                                html.Span(className="badge bg-primary ms-2", children=[
                                    html.I(className="fas fa-grip-vertical me-1"),
                                    "Drag"
                                ])
                            ]),
                            html.Div(className="layout-item-content", children=[
                                "Header content (logo, navigation, etc.)"
                            ])
                        ])
                    ]),
                    
                    # Main content
                    html.Div(className="layout-main-content", children=[
                        # Sidebar
                        html.Div(className="layout-sidebar", children=[
                            html.Div(className="layout-item", children=[
                                html.Div(className="layout-item-header", children=[
                                    "Sidebar",
                                    html.Span(className="badge bg-primary ms-2", children=[
                                        html.I(className="fas fa-grip-vertical me-1"),
                                        "Drag"
                                    ])
                                ]),
                                html.Div(className="layout-item-content", children=[
                                    "Sidebar content (navigation, filters, etc.)"
                                ])
                            ])
                        ]),
                        
                        # Main area
                        html.Div(className="layout-main", children=[
                            # Dashboard widgets will go here
                            html.Div(className="layout-item", children=[
                                html.Div(className="layout-item-header", children=[
                                    "Dashboard Content",
                                    html.Span(className="badge bg-primary ms-2", children=[
                                        html.I(className="fas fa-grip-vertical me-1"),
                                        "Drag"
                                    ])
                                ]),
                                html.Div(className="layout-item-content", children=[
                                    "Main dashboard content (charts, tables, etc.)"
                                ])
                            ])
                        ])
                    ]),
                    
                    # Footer
                    html.Div(className="layout-footer", children=[
                        html.Div(className="layout-item", children=[
                            html.Div(className="layout-item-header", children=[
                                "Footer",
                                html.Span(className="badge bg-primary ms-2", children=[
                                    html.I(className="fas fa-grip-vertical me-1"),
                                    "Drag"
                                ])
                            ]),
                            html.Div(className="layout-item-content", children=[
                                "Footer content (copyright, links, etc.)"
                            ])
                        ])
                    ])
                ]),
                
                # Layout configuration
                html.Div(className="mt-4", id="layout-configuration")
            ])
        ]),
        
        # Preset management
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
                    html.H5("Layout Presets", className="mb-0"),
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "Create New Preset"],
                        id="create-preset-btn-2",
                        color="primary",
                        size="sm"
                    )
                ]),
                
                dbc.Row([
                    dbc.Col(md=4, children=[
                        dbc.Card(className="mb-3", children=[
                            dbc.CardHeader("Default Layout"),
                            dbc.CardBody(children=[
                                html.P("The standard layout for all users", className="text-muted"),
                                html.Div(className="d-grid gap-2", children=[
                                    dbc.Button(
                                        [html.I(className="fas fa-eye me-2"), "Preview"],
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-edit me-2"), "Edit"],
                                        color="outline-secondary",
                                        size="sm"
                                    )
                                ])
                            ])
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        dbc.Card(className="mb-3 border-primary", children=[
                            dbc.CardHeader("Executive Dashboard", className="bg-primary text-white"),
                            dbc.CardBody(children=[
                                html.P("Layout for executives with high-level metrics", className="text-muted"),
                                html.Div(className="d-grid gap-2", children=[
                                    dbc.Button(
                                        [html.I(className="fas fa-eye me-2"), "Preview"],
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-edit me-2"), "Edit"],
                                        color="outline-secondary",
                                        size="sm"
                                    )
                                ])
                            ]),
                            dbc.CardFooter(children=[
                                html.Small("Assigned to: ", className="text-muted"),
                                html.Span("5 users", className="ms-1 fw-bold")
                            ])
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        dbc.Card(className="mb-3", children=[
                            dbc.CardHeader("Analyst View"),
                            dbc.CardBody(children=[
                                html.P("Detailed view for data analysts", className="text-muted"),
                                html.Div(className="d-grid gap-2", children=[
                                    dbc.Button(
                                        [html.I(className="fas fa-eye me-2"), "Preview"],
                                        color="outline-primary",
                                        size="sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-edit me-2"), "Edit"],
                                        color="outline-secondary",
                                        size="sm"
                                    )
                                ])
                            ]),
                            dbc.CardFooter(children=[
                                html.Small("Assigned to: ", className="text-muted"),
                                html.Span("12 users", className="ms-1 fw-bold")
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        
        # Modals
        dbc.Modal(
            [
                dbc.ModalHeader("Preview Layout"),
                dbc.ModalBody(
                    html.Iframe(
                        src="/dashboard-preview",
                        style={"width": "100%", "height": "500px", "border": "none"}
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-preview-modal", className="ms-auto")
                ),
            ],
            id="preview-modal",
            size="xl",
            is_open=False,
        ),
        
        # Hidden stores
        dcc.Store(id='layout-store'),
        
        # Toast for notifications
        dbc.Toast(
            id="layout-notification",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])

def register_callbacks(app):
    """Register callbacks for the layout overrides component."""
    @app.callback(
        [Output("layout-help-alert", "is_open")],
        [Input("layout-help-btn", "n_clicks")],
        [State("layout-help-alert", "is_open")],
    )
    def toggle_help(n_clicks, is_open):
        """Toggle the help alert."""
        if n_clicks:
            return [not is_open]
        return [is_open]
    
    @app.callback(
        [Output("user-layout-info", "children"),
         Output("save-layout-btn", "disabled"),
         Output("layout-store", "data")],
        [Input("layout-user-select", "value")]
    )
    def load_user_layout(user_id):
        """Load layout for the selected user."""
        if not user_id:
            return ["Select a user to edit their layout", True, None]
        
        # In a real app, you would fetch the user's layout from the database
        # For now, we'll use a default layout
        default_layout = {
            'version': '1.0',
            'regions': {
                'header': {'visible': True, 'order': 1},
                'sidebar': {'visible': True, 'order': 2, 'width': 250},
                'main': {'visible': True, 'order': 3},
                'footer': {'visible': True, 'order': 4}
            },
            'widgets': {}
        }
        
        # Get user info
        user = get_user(user_id) or {}
        
        # Build user info card
        user_card = dbc.Card(children=[
            dbc.CardBody(children=[
                html.Div(className="d-flex align-items-center", children=[
                    html.Img(
                        src=user.get('avatar_url', '/static/images/default-avatar.png'),
                        className="rounded-circle me-3",
                        style={"width": "48px", "height": "48px", "objectFit": "cover"}
                    ),
                    html.Div(children=[
                        html.H5(user.get('full_name', 'User'), className="mb-0"),
                        html.Small(user.get('email', 'No email'), className="text-muted")
                    ])
                ]),
                html.Hr(),
                html.Div(className="row g-2", children=[
                    html.Div(className="col-6", children=[
                        html.Div(className="d-flex align-items-center", children=[
                            html.Div(className="me-2", children=[
                                html.I(className="fas fa-user-tag")
                            ]),
                            html.Div(children=[
                                html.Div("Role", className="text-muted small"),
                                html.Div(user.get('role', 'user').title(), className="fw-bold")
                            ])
                        ])
                    ]),
                    html.Div(className="col-6", children=[
                        html.Div(className="d-flex align-items-center", children=[
                            html.Div(className="me-2", children=[
                                html.I(className="fas fa-calendar-alt")
                            ]),
                            html.Div(children=[
                                html.Div("Last Login", className="text-muted small"),
                                html.Div("2 hours ago", className="fw-bold")  # Would be dynamic in a real app
                            ])
                        ])
                    ])
                ])
            ])
        ])
        
        return [user_card, False, default_layout]
    
    @app.callback(
        [Output("preview-modal", "is_open")],
        [Input("preview-layout-btn", "n_clicks"),
         Input("close-preview-modal", "n_clicks")],
        [State("preview-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_preview(open_click, close_click, is_open):
        """Toggle the preview modal."""
        if open_click or close_click:
            return [not is_open]
        return [is_open]
    
    @app.callback(
        [Output("layout-notification", "is_open"),
         Output("layout-notification", "children"),
         Output("layout-notification", "header"),
         Output("layout-notification", "icon")],
        [Input("save-layout-btn", "n_clicks")],
        [State("layout-user-select", "value"),
         State("layout-store", "data")],
        prevent_initial_call=True
    )
    def save_layout(save_click, user_id, layout_data):
        """Save the layout for the selected user."""
        if not save_click or not user_id or not layout_data:
            raise PreventUpdate
        
        try:
            # In a real app, you would save the layout to the database
            # For now, we'll just log the action
            log_admin_event(
                user_id=user_id,
                event_type="layout_updated",
                target_type="user",
                target_id=user_id,
                metadata={
                    'layout': layout_data
                }
            )
            
            return [
                True,  # Show notification
                f"Layout for user {user_id} has been saved successfully.",
                "Success",
                "success"
            ]
        except Exception as e:
            return [
                True,  # Show notification
                f"Error saving layout: {str(e)}",
                "Error",
                "danger"
            ]
    
    # Add more callbacks for the layout editor functionality
    # (drag and drop, widget configuration, etc.)
