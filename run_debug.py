import sys
import traceback

try:
    print("=== Starting application in debug mode ===")
    from app import app
    
    print("\n=== Application imported successfully ===")
    print("Starting server...")
    
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        use_reloader=False  # Disable reloader to avoid duplicate output
    )
    
except Exception as e:
    print("\n=== ERROR OCCURRED ===")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print("\nTraceback:")
    traceback.print_exc()
    
    # Print additional debug information
    print("\n=== System Path ===")
    import sys
    for path in sys.path:
        print(path)
    
    print("\n=== Installed Packages ===")
    import pkg_resources
    for dist in pkg_resources.working_set:
        print(f"{dist.key}=={dist.version}")
    
    input("\nPress Enter to exit...")
