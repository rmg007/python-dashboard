"""
Callbacks for the Admin Dashboard user management.
"""
from dash import Input, Output, State, html, ctx, no_update
import dash_bootstrap_components as dbc
from datetime import datetime
import json

from db.user_queries import get_user, update_user, delete_user, log_admin_event

def register_callbacks(app):
    """Register all user management callbacks."""
    @app.callback(
        [Output("edit-user-modal", "is_open"),
         Output("edit-user-modal-body", "children"),
         Output("user-notification", "is_open"),
         Output("user-notification", "children"),
         Output("user-notification", "header"),
         Output("user-notification", "icon")],
        [Input("edit-selected-users-btn", "n_clicks"),
         Input("edit-user-cancel", "n_clicks"),
         Input("edit-user-save", "n_clicks"),
         Input("delete-user-confirm", "n_clicks")],
        [State("users-table", "selected_row_ids"),
         State("edit-user-modal", "is_open"),
         State("users-table", "data")],
        prevent_initial_call=True
    )
    def toggle_edit_modal(edit_click, cancel_click, save_click, delete_click, selected_ids, is_open, table_data):
        """Handle the edit user modal and user actions."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Handle delete action
        if ctx_callback == "delete-user-confirm" and delete_click and selected_ids:
            try:
                # In a real app, you would delete the users from the database
                # For now, we'll just log the action
                for user_id in selected_ids:
                    log_admin_event(
                        user_id="admin",  # Current admin user ID
                        event_type="user_deleted",
                        target_type="user",
                        target_id=user_id,
                        metadata={"action": "user_deleted"}
                    )
                
                return [
                    False,  # Close modal
                    no_update,  # Keep existing modal body
                    True,  # Show notification
                    f"Successfully deleted {len(selected_ids)} user(s)",
                    "Success",
                    "success"
                ]
            except Exception as e:
                return [
                    no_update,
                    no_update,
                    True,
                    f"Error deleting users: {str(e)}",
                    "Error",
                    "danger"
                ]
        
        # Handle save action
        if ctx_callback == "edit-user-save" and save_click and selected_ids:
            try:
                # In a real app, you would update the users in the database
                # For now, we'll just log the action
                for user_id in selected_ids:
                    log_admin_event(
                        user_id="admin",  # Current admin user ID
                        event_type="user_updated",
                        target_type="user",
                        target_id=user_id,
                        metadata={"action": "user_updated"}
                    )
                
                return [
                    False,  # Close modal
                    no_update,  # Keep existing modal body
                    True,  # Show notification
                    f"Successfully updated {len(selected_ids)} user(s)",
                    "Success",
                    "success"
                ]
            except Exception as e:
                return [
                    no_update,
                    no_update,
                    True,
                    f"Error updating users: {str(e)}",
                    "Error",
                    "danger"
                ]
        
        # Handle edit action
        if ctx_callback == "edit-selected-users-btn" and edit_click and selected_ids:
            # Get the first selected user's data
            user_data = next((user for user in table_data if user["user_id"] in selected_ids), None)
            
            if not user_data:
                return [
                    no_update,
                    no_update,
                    True,
                    "User not found",
                    "Error",
                    "danger"
                ]
            
            # Create the edit form
            form = dbc.Form([
                dbc.Row([
                    dbc.Label("User ID", width=3, className="text-muted"),
                    dbc.Col([
                        dbc.Input(type="text", value=user_data.get("user_id", ""), disabled=True)
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Email", width=3),
                    dbc.Col([
                        dbc.Input(
                            id="edit-user-email",
                            type="email",
                            value=user_data.get("email", ""),
                            required=True
                        )
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Full Name", width=3),
                    dbc.Col([
                        dbc.Input(
                            id="edit-user-name",
                            type="text",
                            value=user_data.get("full_name", "")
                        )
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Role", width=3),
                    dbc.Col([
                        dbc.Select(
                            id="edit-user-role",
                            value=user_data.get("role", "user"),
                            options=[
                                {"label": "User", "value": "user"},
                                {"label": "Auditor", "value": "auditor"},
                                {"label": "Admin", "value": "admin"}
                            ]
                        )
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Status", width=3),
                    dbc.Col([
                        dbc.Select(
                            id="edit-user-status",
                            value="active" if user_data.get("is_active", True) else "inactive",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ]
                        )
                    ], width=9)
                ])
            ])
            
            return [
                True,  # Open modal
                form,
                no_update,
                no_update,
                no_update,
                no_update
            ]
        
        # Handle cancel or close
        if ctx_callback in ["edit-user-cancel", "delete-user-cancel"] or not selected_ids:
            return [
                False,  # Close modal
                no_update,  # Keep existing modal body
                no_update,
                no_update,
                no_update,
                no_update
            ]
        
        return [
            not is_open,  # Toggle modal
            no_update,  # Keep existing modal body
            no_update,
            no_update,
            no_update,
            no_update
        ]
    
    @app.callback(
        [Output("delete-user-modal", "is_open")],
        [Input("deactivate-users-btn", "n_clicks"),
         Input("delete-user-cancel", "n_clicks")],
        [State("delete-user-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_delete_modal(delete_click, cancel_click, is_open):
        """Toggle the delete confirmation modal."""
        if delete_click or cancel_click:
            return [not is_open]
        return [is_open]
    
    @app.callback(
        [Output("users-table", "data"),
         Output("users-table", "selected_rows")],
        [Input("edit-user-save", "n_clicks"),
         Input("delete-user-confirm", "n_clicks")],
        [State("users-table", "data"),
         State("users-table", "selected_row_ids")],
        prevent_initial_call=True
    )
    def update_users_table(save_click, delete_click, current_data, selected_ids):
        """Update the users table after edits or deletions."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if ctx_callback == "edit-user-save" and save_click and selected_ids:
            # In a real app, you would update the data from the database
            # For now, we'll just return the current data
            return [current_data, []]
        
        if ctx_callback == "delete-user-confirm" and delete_click and selected_ids:
            # In a real app, you would remove the deleted users
            # For now, we'll just return the current data
            return [current_data, []]
        
        return [current_data, []]
