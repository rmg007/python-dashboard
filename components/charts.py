from dash import dcc
import plotly.express as px
import pandas as pd
from typing import List, Tuple, Any

def build_trend_chart(rows: List[Tuple[str, int]]) -> dcc.Graph:
    """
    Build a line chart showing permit trends over time.
    
    Args:
        rows: List of tuples containing (period, count) data
        
    Returns:
        dcc.Graph: A Dash Graph component with the trend chart
    """
    if not rows:
        return dcc.Graph(
            figure=px.line(
                title="No Data Available",
                labels={"x": "Period", "y": "Number of Permits"}
            ).update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#7FDBFF')
            )
        )
    
    df = pd.DataFrame(rows, columns=["Period", "Permits"])
    
    fig = px.line(
        df, 
        x="Period", 
        y="Permits", 
        title="Permit Volume Over Time",
        markers=True,
        line_shape="spline",
        labels={"Period": "Time Period", "Permits": "Number of Permits"}
    )
    
    # Update layout for better visualization
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#7FDBFF'),
        xaxis=dict(showgrid=False, title_font=dict(size=14)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#2A3F5F', title_font=dict(size=14)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1E2130", font_size=12),
        margin=dict(l=50, r=30, t=50, b=30)
    )
    
    # Update line style
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
        hovertemplate='<b>%{x}</b><br>%{y} permits<extra></extra>'
    )
    
    return dcc.Graph(figure=fig, id="permit-trend-chart", className="chart-container")


def build_status_chart(rows: List[Tuple[str, int]]) -> dcc.Graph:
    """
    Build a bar chart showing the distribution of permit statuses.
    
    Args:
        rows: List of tuples containing (status, count) data
        
    Returns:
        dcc.Graph: A Dash Graph component with the status distribution chart
    """
    if not rows:
        return dcc.Graph(
            figure=px.bar(
                title="No Data Available",
                labels={"x": "Status", "y": "Count"}
            ).update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#7FDBFF')
            )
        )
    
    df = pd.DataFrame(rows, columns=["Status", "Count"])
    
    # Create a color mapping for different statuses
    status_colors = {
        'Approved': '#2ecc71',
        'Pending': '#f39c12',
        'Rejected': '#e74c3c',
        'In Review': '#3498db',
        'Draft': '#9b59b6'
    }
    
    # Sort by count for better visualization
    df = df.sort_values('Count', ascending=True)
    
    fig = px.bar(
        df, 
        x="Count", 
        y="Status", 
        title="Permit Status Distribution",
        orientation='h',
        color="Status",
        color_discrete_map=status_colors,
        labels={"Count": "Number of Permits", "Status": "Status"}
    )
    
    # Update layout for better visualization
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#7FDBFF'),
        xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#2A3F5F', title_font=dict(size=14)),
        yaxis=dict(showgrid=False, title_font=dict(size=14)),
        showlegend=False,
        hovermode="y",
        hoverlabel=dict(bgcolor="#1E2130", font_size=12),
        margin=dict(l=50, r=30, t=50, b=30)
    )
    
    # Update bar style
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>%{x} permits<extra></extra>',
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=1
    )
    
    return dcc.Graph(figure=fig, id="status-bar-chart", className="chart-container")
