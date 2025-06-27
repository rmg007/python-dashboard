"""
Draggable dashboard layout components using dash-draggable.
"""
from typing import Dict, List, Any, Optional
import dash_draggable as dd
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_draggable_grid(
    layout: List[Dict[str, Any]],
    children: List,
    grid_id: str = "dashboard-grid",
    save_btn_id: str = "save-layout-btn",
    reset_btn_id: str = "reset-layout-btn"
) -> html.Div:
    """
    Create a draggable grid layout for the dashboard.
    
    Args:
        layout: List of layout items with i, x, y, w, h properties
        children: List of components to be placed in the grid
        grid_id: ID for the grid container
        save_btn_id: ID for the save layout button
        reset_btn_id: ID for the reset layout button
        
    Returns:
        html.Div: A draggable grid layout with controls
    """
    return html.Div([
        # Control buttons
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    html.I(className="fas fa-save me-2") + "Save Layout",
                    id=save_btn_id,
                    color="primary",
                    className="me-2"
                ),
                dbc.Button(
                    html.I(className="fas fa-undo me-2") + "Reset Layout",
                    id=reset_btn_id,
                    color="secondary",
                    outline=True
                ),
                html.Div(id="save-status", className="ms-3 d-inline-block")
            ], width=12, className="mb-3")
        ]),
        
        # The draggable grid
        dd.DraggableGridLayout(
            id=grid_id,
            layout=layout,
            children=children,
            clearSavedLayout=True,
            cols=12,
            rowHeight=30,
            containerPadding=[0, 0],
            margin=[10, 10],
            isDraggable=True,
            isResizable=True,
            isBounded=True,
            useCSSTransforms=True,
            compactType=None,
            preventCollision=False,
            className="dashboard-grid"
        )
    ])


def create_dashboard_card(
    component_id: str,
    title: str,
    content: Any,
    loading: bool = False,
    className: str = "",
    **kwargs
) -> dbc.Card:
    """
    Create a card component for dashboard items.
    
    Args:
        component_id: Unique ID for the component
        title: Card title
        content: Content to display in the card body
        loading: Whether to show loading state
        className: Additional CSS classes
        **kwargs: Additional props to pass to the card
        
    Returns:
        dbc.Card: A styled card component
    """
    return dbc.Card(
        [
            dbc.CardHeader(title, className="fw-bold bg-light"),
            dbc.CardBody([
                dcc.Loading(
                    id=f"loading-{component_id}",
                    children=content,
                    type="circle",
                    className="p-5" if loading else ""
                )
            ], className="p-0"),
        ],
        className=f"h-100 {className}",
        id=f"card-{component_id}",
        **kwargs
    )


def create_dashboard_component(
    component_id: str,
    title: str,
    content: Any,
    width: int = 12,
    height: int = 4,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a dashboard component with layout metadata.
    
    Args:
        component_id: Unique ID for the component
        title: Component title
        content: Component content
        width: Default width in grid units (1-12)
        height: Default height in grid units
        **kwargs: Additional props for the component
        
    Returns:
        dict: Component with layout metadata
    """
    return {
        "i": component_id,
        "component": create_dashboard_card(
            component_id=component_id,
            title=title,
            content=content,
            **kwargs
        ),
        "w": width,
        "h": height,
        "minW": 2,
        "minH": 3,
        "maxW": 12,
        "maxH": 12,
        "static": False
    }
