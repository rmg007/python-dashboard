print("Testing application startup...\n")

# Test basic imports
try:
    print("1. Testing Dash import...", end=" ")
    import dash
    print("✅ Success")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test app creation
try:
    print("\n2. Testing app creation...", end=" ")
    from dash import Dash
    app = Dash(__name__)
    print("✅ Success")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test database connection
try:
    print("\n3. Testing database connection...", end=" ")
    from db.connection import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"✅ Success. Found tables: {tables}")
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}")

# Test app imports
try:
    print("\n4. Testing app imports...")
    from app import app
    print("   - Main app import: ✅ Success")
    
    # Test if app has required attributes
    print("   - Checking app attributes...")
    required_attrs = ['layout', 'server']
    for attr in required_attrs:
        if hasattr(app, attr):
            print(f"     - {attr}: ✅ Found")
        else:
            print(f"     - {attr}: ❌ Missing")
    
except Exception as e:
    print(f"❌ Failed: {e}")

print("\nTest completed.")
input("Press Enter to exit...")
