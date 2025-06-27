print("🚀 Launching Dashboard...")
print("=" * 50)

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Import the app with error handling
try:
    print("\n🔍 Importing application...")
    from app import app
    print("✅ Application imported successfully")
except Exception as e:
    print(f"❌ Error importing application: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    exit(1)

# Configure and run the server
if __name__ == "__main__":
    print("\n🚀 Starting Dash server...")
    print("   - Host: 0.0.0.0")
    print("   - Port: 8050")
    print("   - Debug: True")
    print("\n🖥️  Open your browser and navigate to: http://127.0.0.1:8050/")
    print("=" * 50)
    
    try:
        app.run_server(
            host='0.0.0.0',
            port=8050,
            debug=True,
            dev_tools_hot_reload=True,
            use_reloader=False  # Disable reloader to avoid duplicate output
        )
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
