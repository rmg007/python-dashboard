"""
Layout manager for loading and saving dashboard layouts.
"""
from typing import List, Dict, Any, Optional
from db.queries import get_user_layout, save_user_layout, get_default_layout
from components.draggable import create_draggable_grid, create_dashboard_component
from components.kpis import get_kpi_placeholders
from components.charts import build_trend_chart, build_status_chart
from components.datatable import build_permit_table


def get_layout_components() -> Dict[str, Dict[str, Any]]:
    """
    Define all available dashboard components with their metadata.
    
    Returns:
        dict: Dictionary of component metadata keyed by component ID
    """
    return {
        "kpi-1": {
            "title": "Key Performance Indicators",
            "component": get_kpi_placeholders(),
            "width": 12,
            "height": 2,
            "className": "bg-light"
        },
        "chart-trend": {
            "title": "Permit Trends Over Time",
            "component": build_trend_chart([]),
            "width": 6,
            "height": 3
        },
        "chart-status": {
            "title": "Status Distribution",
            "component": build_status_chart([]),
            "width": 6,
            "height": 3
        },
        "table-permits": {
            "title": "Permit Details",
            "component": build_permit_table([]),
            "width": 12,
            "height": 4
        }
    }


def build_dashboard_layout(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Build the dashboard layout for a specific user.
    
    Args:
        user_id: Optional user ID to load saved layout for
        
    Returns:
        dict: Dictionary containing the layout and components
    """
    # Get saved layout or default layout
    saved_layout = get_user_layout(user_id) if user_id else []
    default_layout = get_default_layout()
    
    # If no saved layout, use default
    layout = saved_layout if saved_layout else default_layout
    
    # Get all available components
    components = get_layout_components()
    
    # Create component instances with layout
    component_instances = []
    layout_items = []
    
    for item in layout:
        component_id = item.get("i")
        if component_id in components:
            component_data = components[component_id]
            
            # Create component instance with saved layout
            component = create_dashboard_component(
                component_id=component_id,
                title=component_data["title"],
                content=component_data["component"],
                width=item.get("w", component_data.get("width", 6)),
                height=item.get("h", component_data.get("height", 4)),
                className=component_data.get("className", "")
            )
            
            component_instances.append(component["component"])
            layout_items.append({
                "i": component_id,
                "x": item.get("x", 0),
                "y": item.get("y", 0),
                "w": component["w"],
                "h": component["h"],
                "minW": 2,
                "minH": 2,
                "maxW": 12,
                "maxH": 12,
                "static": False
            })
    
    return {
        "layout": layout_items,
        "components": component_instances,
        "is_default": not bool(saved_layout)
    }

def save_dashboard_layout(user_id: str, layout: List[Dict[str, Any]]) -> bool:
    """
    Save the dashboard layout for a user.
    
    Args:
        user_id: User ID to save layout for
        layout: Layout configuration to save
        
    Returns:
        bool: True if save was successful
    """
    if not user_id or not layout:
        return False
    
    try:
        save_user_layout(user_id, layout)
        return True
    except Exception as e:
        print(f"Error saving layout: {e}")
        return False

def reset_dashboard_layout(user_id: str) -> bool:
    """
    Reset the dashboard layout to default for a user.
    
    Args:
        user_id: User ID to reset layout for
        
    Returns:
        bool: True if reset was successful
    """
    if not user_id:
        return False
    
    try:
        # Delete the user's layout to fall back to default
        from db.connection import get_connection
        with get_connection() as conn:
            conn.execute("DELETE FROM user_layouts WHERE user_id = ?", (user_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error resetting layout: {e}")
        return False
