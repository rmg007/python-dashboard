print("Testing app startup...")

try:
    print("1. Importing app...")
    from app import app
    print("✅ App imported successfully")
    
    print("2. Accessing app.server...")
    server = app.server
    print("✅ App server accessed successfully")
    
    print("3. Running app...")
    if __name__ == "__main__":
        app.run_server(debug=True, port=8050)
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
print("Test completed.")
