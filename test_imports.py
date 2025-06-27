print("Testing application imports...\n")

# Test basic imports
try:
    import dash
    print("✅ dash imported successfully")
except ImportError as e:
    print(f"❌ Error importing dash: {e}")

try:
    import dash_bootstrap_components as dbc
    print("✅ dash_bootstrap_components imported successfully")
except ImportError as e:
    print(f"❌ Error importing dash_bootstrap_components: {e}")

try:
    import pandas as pd
    print(f"✅ pandas {pd.__version__} imported successfully")
except ImportError as e:
    print(f"❌ Error importing pandas: {e}")

# Test application imports
try:
    from db.connection import get_connection
    print("✅ db.connection imported successfully")
    
    # Test database connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Database connection successful. Found tables: {[t[0] for t in tables]}")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
except Exception as e:
    print(f"❌ Error importing db.connection: {e}")

print("\nImport test completed.")
