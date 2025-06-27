"""
Callbacks for handling dashboard layout changes and persistence.
"""
from typing import Dict, Any, Tuple, List
from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from layout.layout_manager import build_dashboard_layout, save_dashboard_layout, reset_dashboard_layout


def register_layout_callbacks(app):
    """
    Register all layout-related callbacks.
    
    Args:
        app: Dash application instance
    """
    @app.callback(
        [
            Output("dashboard-grid", "layout"),
            Output("dashboard-grid", "children"),
            Output("save-status", "children"),
            Output("save-status", "className")
        ],
        [
            Input("save-layout-btn", "n_clicks"),
            Input("reset-layout-btn", "n_clicks"),
            Input("dashboard-grid", "layout"),
            Input("current-user", "modified_timestamp")
        ],
        [
            State("current-user", "data"),
            State("dashboard-grid", "layout"),
            State("save-status", "className")
        ],
        prevent_initial_call=True
    )
    def handle_layout_actions(
        save_clicks: int,
        reset_clicks: int,
        current_layout: List[Dict[str, Any]],
        user_ts: int,
        user_data: Dict[str, Any],
        previous_layout: List[Dict[str, Any]],
        status_class: str
    ) -> Tuple[List[Dict[str, Any]], List[Any], str, str]:
        """
        Handle layout saving, resetting, and loading.
        
        Args:
            save_clicks: Number of times save button was clicked
            reset_clicks: Number of times reset button was clicked
            current_layout: Current grid layout
            user_ts: Timestamp of last user data modification
            user_data: Current user data
            previous_layout: Previous grid layout
            status_class: Current status message CSS class
            
        Returns:
            Tuple containing:
                - Updated layout
                - Grid children components
                - Status message
                - Status message CSS class
        """
        if not user_data or "user_id" not in user_data:
            raise PreventUpdate
            
        user_id = user_data["user_id"]
        
        # Handle save button click
        if ctx.triggered_id == "save-layout-btn":
            if save_dashboard_layout(user_id, current_layout):
                return (
                    current_layout,
                    no_update,
                    "Layout saved successfully!",
                    "text-success"
                )
            return (
                no_update,
                no_update,
                "Failed to save layout. Please try again.",
                "text-danger"
            )
            
        # Handle reset button click
        elif ctx.triggered_id == "reset-layout-btn":
            if reset_dashboard_layout(user_id):
                # Rebuild the layout with defaults
                layout_data = build_dashboard_layout(user_id)
                return (
                    layout_data["layout"],
                    layout_data["components"],
                    "Layout reset to default.",
                    "text-info"
                )
            return (
                no_update,
                no_update,
                "Failed to reset layout. Please try again.",
                "text-danger"
            )
            
        # Handle initial load or user change
        elif ctx.triggered_id == "current-user.modified_timestamp":
            layout_data = build_dashboard_layout(user_id)
            return (
                layout_data["layout"],
                layout_data["components"],
                "Welcome! Drag and drop to customize your dashboard." if layout_data["is_default"] 
                else "Your saved layout has been loaded.",
                "text-muted"
            )
            
        # Handle layout changes (auto-save could be implemented here)
        elif ctx.triggered_id == "dashboard-grid.layout":
            # Optional: Auto-save on layout change
            # save_dashboard_layout(user_id, current_layout)
            return (
                current_layout,
                no_update,
                "Drag and drop to rearrange. Don't forget to save your changes!",
                "text-warning"
            )
            
        raise PreventUpdate
    
    @app.callback(
        [
            Output("main-panel-wrapper", "children"),
            Output("current-user", "data", allow_duplicate=True)
        ],
        [Input("url", "pathname")],
        [State("current-user", "data")],
        prevent_initial_call=True
    )
    def initialize_dashboard(pathname: str, user_data: Dict[str, Any]) -> Tuple[dbc.Container, Dict[str, str]]:
        """
        Initialize the dashboard with the user's layout.
        
        Args:
            pathname: Current URL path
            user_data: Current user data
            
        Returns:
            Tuple containing:
                - Main panel container with draggable grid
                - Updated user data
        """
        # In a real app, you'd get the user ID from the session
        # For now, we'll use a default user
        if not user_data:
            user_data = {"user_id": "demo@example.com"}
            
        # Build the layout for this user
        layout_data = build_dashboard_layout(user_data["user_id"])
        
        # Create the draggable grid
        grid = create_draggable_grid(
            layout=layout_data["layout"],
            children=layout_data["components"],
            grid_id="dashboard-grid",
            save_btn_id="save-layout-btn",
            reset_btn_id="reset-layout-btn"
        )
        
        return grid, user_data
