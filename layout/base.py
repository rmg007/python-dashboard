from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.sidebar import build_sidebar

# Import for type hints
from typing import Dict, Any, Optional

def serve_layout():
    """
    Main layout container for the dashboard.
    Includes user session management and the main content structure.
    """
    return dbc.Container([
        # Store user session data
        dcc.Store(id="current-user", storage_type='session'),
        
        # URL routing
        dcc.Location(id="url", refresh=False),
        
        # Main content row
        dbc.Row([
            # Sidebar
            dbc.Col(
                build_sidebar(), 
                width=3,
                className="sidebar"
            ),
            
            # Main content area
            dbc.Col(
                id="main-panel-wrapper",
                width=9,
                className="main-content"
            )
        ], className="g-0"),
        
        # Toast for notifications
        dbc.Toast(
            id="layout-toast",
            header="Dashboard",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ], 
    fluid=True, 
    className="dashboard-container",
    style={"minHeight": "100vh", "padding": "0"}
)

# Add custom CSS for the dashboard layout
custom_css = """
.dashboard-container {
    background-color: #f8f9fa;
}

.sidebar {
    background-color: white;
    min-height: 100vh;
    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    z-index: 100;
    padding: 1rem;
}

.main-content {
    padding: 1.5rem;
}

.dashboard-grid {
    min-height: calc(100vh - 2rem);
}

/* Responsive adjustments */
@media (max-width: 992px) {
    .sidebar, .main-content {
        width: 100% !important;
    }
    
    .main-content {
        padding: 1rem;
    }
}
"""

# Add this CSS to the app's index or a dedicated CSS file
# The layout_callbacks will handle adding the CSS to the app
