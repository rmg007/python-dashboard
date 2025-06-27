print("Checking app.py syntax...")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Try to compile the code
    compile(code, 'app.py', 'exec')
    print("✅ app.py has valid syntax")
    
except SyntaxError as e:
    print(f"❌ Syntax error in app.py")
    print(f"Line {e.lineno}, Column {e.offset}")
    print(f"{e.text}" if e.text else "")
    print(f"{' ' * (e.offset-1)}^")
    print(f"Error: {e.msg}")
    
except Exception as e:
    print(f"❌ Error checking app.py: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
