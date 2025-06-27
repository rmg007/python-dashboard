from db.connection import get_connection
from typing import List, Dict, Any, Optional

def get_filter_options(column):
    allowed = {"year", "month", "action_by_dept"}
    if column not in allowed:
        return []

    query = f"SELECT DISTINCT {column} FROM vw_filters ORDER BY {column}"
    with get_connection() as conn:
        results = conn.execute(query).fetchall()
    return [row[0] for row in results if row[0]]

def get_kpi_totals(year=None, month=None, dept=None):
    """
    Get KPI totals based on the provided filters.
    
    Args:
        year (str, optional): Filter by year
        month (str, optional): Filter by month (1-12)
        dept (str, optional): Filter by department
        
    Returns:
        dict: Dictionary containing total_permits, total_valuation, and department_count
    """
    query = """
    SELECT 
        COUNT(*) as total_permits,
        COALESCE(SUM(CAST(REPLACE(valuation, '$', '') AS REAL)), 0) as total_valuation,
        COUNT(DISTINCT action_by_dept) as department_count
    FROM permits
    WHERE 1=1
    """

    filters = []
    params = []

    if year:
        filters.append("AND strftime('%Y', date_status) = ?")
        params.append(str(year))


    if month:
        filters.append("AND strftime('%m', date_status) = ?")
        params.append(month.zfill(2))  # Ensure two-digit month

    if dept:
        filters.append("AND action_by_dept = ?")
        params.append(dept)


    query += " ".join(filters)

    with get_connection() as conn:
        result = conn.execute(query, params).fetchone()

    return {
        "total_permits": result[0] or 0,
        "total_valuation": result[1] or 0.0,
        "department_count": result[2] or 0
    }


def get_permit_trends(year=None, month=None, dept=None):
    """
    Get permit trends over time based on filters.
    
    Args:
        year (str, optional): Filter by year
        month (str, optional): Filter by month (1-12)
        dept (str, optional): Filter by department
        
    Returns:
        list: List of tuples containing (period, count)
    """
    query = """
    SELECT strftime('%Y-%m', date_status) as period, COUNT(*) as count
    FROM permits
    WHERE 1=1
    """
    filters, params = [], []

    if year:
        filters.append("AND strftime('%Y', date_status) = ?")
        params.append(str(year))

    if month:
        filters.append("AND strftime('%m', date_status) = ?")
        params.append(month.zfill(2))

    if dept:
        filters.append("AND action_by_dept = ?")
        params.append(dept)


    query += " ".join(filters) + " GROUP BY period ORDER BY period"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_status_distribution(year=None, month=None, dept=None):
    """
    Get status distribution of permits based on filters.
    
    Args:
        year (str, optional): Filter by year
        month (str, optional): Filter by month (1-12)
        dept (str, optional): Filter by department
        
    Returns:
        list: List of tuples containing (status, count)
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM permits
    WHERE 1=1
    """
    filters, params = [], []

    if year:
        filters.append("AND strftime('%Y', date_status) = ?")
        params.append(str(year))


    if month:
        filters.append("AND strftime('%m', date_status) = ?")
        params.append(month.zfill(2))

    if dept:
        filters.append("AND action_by_dept = ?")
        params.append(dept)


    query += " ".join(filters) + " GROUP BY status ORDER BY count DESC"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_filtered_permits(year=None, month=None, dept=None):
    """
    Get filtered permit records based on criteria.
    
    Args:
        year (str, optional): Filter by year
        month (str, optional): Filter by month (1-12)
        dept (str, optional): Filter by department
        
    Returns:
        list: List of tuples containing permit records
    """
    query = """
    SELECT 
        permit_number,
        permit_type,
        permit_subtype,
        status,
        description,
        CAST(REPLACE(valuation, '$', '') AS REAL) as valuation,
        date_filed,
        date_issued,
        date_completed,
        action_by_dept,
        address,
        contractor
    FROM permits
    WHERE 1=1
    """
    
    params = []
    
    if year:
        query += " AND strftime('%Y', date_filed) = ?"
        params.append(str(year))
        
    if month:
        query += " AND strftime('%m', date_filed) = ?"
        params.append(month.zfill(2))
        
    if dept:
        query += " AND action_by_dept = ?"
        params.append(dept)
        
    query += " ORDER BY date_filed DESC"
    
    with get_connection() as conn:
        results = conn.execute(query, params).fetchall()
    
    return results


def get_user_layout(user_id: str) -> List[Dict[str, Any]]:
    """
    Get the saved layout for a specific user.
    
    Args:
        user_id (str): The ID of the user
        
    Returns:
        list: List of layout items with x, y, w, h properties
    """
    query = """
    SELECT component_id, x, y, w, h
    FROM user_layouts
    WHERE user_id = ?
    ORDER BY component_id
    """
    
    with get_connection() as conn:
        rows = conn.execute(query, (user_id,)).fetchall()
    
    return [
        {"i": row[0], "x": row[1], "y": row[2], "w": row[3], "h": row[4]}
        for row in rows
    ]


def save_user_layout(user_id: str, layout: List[Dict[str, Any]]) -> None:
    """
    Save the layout for a specific user.
    
    Args:
        user_id (str): The ID of the user
        layout (list): List of layout items with i, x, y, w, h properties
    """
    if not user_id or not layout:
        return
    
    with get_connection() as conn:
        # Delete existing layout for this user
        conn.execute("DELETE FROM user_layouts WHERE user_id = ?", (user_id,))
        
        # Insert new layout items
        if layout:
            values = [
                (user_id, item["i"], item["x"], item["y"], item["w"], item["h"])
                for item in layout
                if all(k in item for k in ["i", "x", "y", "w", "h"])
            ]
            if values:
                conn.executemany(
                    """
                    INSERT INTO user_layouts (user_id, component_id, x, y, w, h)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    values
                )
        conn.commit()


def get_default_layout() -> List[Dict[str, Any]]:
    """
    Get the default dashboard layout.
    
    Returns:
        list: Default layout configuration
    """
    return [
        {"i": "kpi-1", "x": 0, "y": 0, "w": 12, "h": 2},
        {"i": "chart-trend", "x": 0, "y": 2, "w": 6, "h": 3},
        {"i": "chart-status", "x": 6, "y": 2, "w": 6, "h": 3},
        {"i": "table-permits", "x": 0, "y": 5, "w": 12, "h": 4}
    ]
