print("🔍 Running Core Functionality Tests")
print("=" * 50)

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🧪 Testing module imports...")
    try:
        import dash
        import dash_bootstrap_components as dbc
        import pandas as pd
        import plotly.graph_objects as go
        from sqlalchemy import create_engine
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection and schema."""
    print("\n🧪 Testing database connection...")
    try:
        from db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if permits table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permits';")
        if not cursor.fetchone():
            print("❌ 'permits' table not found in database")
            return False
            
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM permits;")
        count = cursor.fetchone()[0]
        print(f"✅ Database connection successful. Found {count} records in 'permits' table")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_queries():
    """Test database queries."""
    print("\n🧪 Testing database queries...")
    try:
        from db.queries import get_filter_options, get_kpi_totals
        
        # Test get_filter_options
        years = get_filter_options("year")
        months = get_filter_options("month")
        depts = get_filter_options("action_by_dept")
        
        print(f"✅ Query tests passed. Found {len(years)} years, {len(months)} months, {len(depts)} departments")
        
        # Test KPI totals
        kpis = get_kpi_totals()
        print(f"✅ KPI query returned: {kpis}")
        
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_components():
    """Test that components can be created."""
    print("\n🧪 Testing component creation...")
    try:
        from components.charts import build_trend_chart, build_status_chart
        from components.datatable import build_permit_table
        
        # Test with empty data
        empty_fig = build_trend_chart([])
        status_fig = build_status_chart([])
        table = build_permit_table([])
        
        print("✅ Component creation tests passed")
        return True
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def run_tests():
    """Run all tests and report results."""
    test_results = [
        ("Module Imports", test_imports()),
        ("Database Connection", test_database()),
        ("Database Queries", test_queries()),
        ("Components", test_components()),
    ]
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        all_passed = all_passed and result
    
    if all_passed:
        print("\n🎉 All tests passed! The core functionality appears to be working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    run_tests()
    input("\nPress Enter to exit...")
