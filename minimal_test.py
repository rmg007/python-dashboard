import sys
import traceback
import logging

# Configure logging to show all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def run_test():
    print("Starting minimal test...")
    
    try:
        print("1. Importing app...")
        from app import app
        print("✅ App imported successfully")
        
        print("2. Accessing app.server...")
        server = app.server
        print("✅ App server accessed successfully")
        
        print("3. Running app...")
        app.run_server(debug=True, port=8050)
        
    except Exception as e:
        print("\n❌ Error during test:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
