import os
import sys
from dash.testing.application_runners import import_app
import pytest

def test_app_import():
    """Test that the app can be imported and has required attributes."""
    try:
        from app import app
        assert hasattr(app, 'layout'), "App is missing 'layout' attribute"
        assert hasattr(app, 'server'), "App is missing 'server' attribute"
        print("✅ App imports successfully and has required attributes")
        return True
    except Exception as e:
        print(f"❌ Error importing app: {e}")
        return False

def test_database_connection():
    """Test that the database connection works and has expected tables."""
    try:
        from db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        assert 'permits' in tables, "'permits' table not found in database"
        print(f"✅ Database connection successful. Tables found: {tables}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_components():
    """Test that key components can be imported and initialized."""
    try:
        from components.charts import build_trend_chart, build_status_chart
        from components.datatable import build_permit_table
        print("✅ Component imports successful")
        return True
    except Exception as e:
        print(f"❌ Component import error: {e}")
        return False

def test_queries():
    """Test that database queries work as expected."""
    try:
        from db.queries import get_filter_options, get_kpi_totals
        
        # Test get_filter_options
        years = get_filter_options("year")
        months = get_filter_options("month")
        depts = get_filter_options("action_by_dept")
        
        print(f"✅ Query tests passed. Found {len(years)} years, {len(months)} months, {len(depts)} departments")
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def run_tests():
    """Run all tests and report results."""
    print("\n🔍 Running Dashboard Tests")
    print("=" * 50)
    
    tests = [
        ("App Import", test_app_import),
        ("Database Connection", test_database_connection),
        ("Component Imports", test_components),
        ("Database Queries", test_queries),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Testing: {name}" + "-" * (45 - len(name)))
        result = test_func()
        results.append((name, result))
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    # Return overall status
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    run_tests()
    input("\nPress Enter to exit...")
