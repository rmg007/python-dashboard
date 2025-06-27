import pdb

try:
    print("Starting application with debugger...")
    pdb.set_trace()
    
    from app import app
    
    print("\nApplication imported successfully!")
    print("Starting server...")
    
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        use_reloader=False
    )
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
    # Print additional debug info
    print("\n=== DEBUG INFO ===")
    import sys
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("\nPress Enter to exit...")
    input()
