"""
Startup and diagnostic script
"""
import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'telegram',
        'PIL',
        'pytesseract',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'telegram':
                import telegram
            elif package == 'PIL':
                from PIL import Image
            elif package == 'pytesseract':
                import pytesseract
            elif package == 'dotenv':
                import dotenv
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n📸 Checking Tesseract OCR...")
    
    try:
        import pytesseract
        
        # First try to get version (PATH method)
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract is properly installed")
            return True
        except:
            # Fallback: check if file exists at expected location
            if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
                print("✅ Tesseract found at C:\\Program Files\\Tesseract-OCR")
                return True
            else:
                print("⚠️ Tesseract is installed but not found in PATH")
                print("Please add Tesseract to your system PATH or install it from:")
                print("https://github.com/UB-Mannheim/tesseract/wiki")
                return False
    except:
        print("⚠️ Tesseract not installed (OCR features won't work)")
        return False

def check_database():
    """Check if database exists and is initialized"""
    print("\n💾 Checking database...")
    
    from database import ExpenseDatabase
    try:
        db = ExpenseDatabase()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def check_config():
    """Check if bot token is configured"""
    print("\n⚙️ Checking configuration...")
    
    from config import BOT_TOKEN
    if BOT_TOKEN and len(BOT_TOKEN) > 10:
        print("✅ Bot token is configured")
        return True
    else:
        print("❌ Bot token is missing or invalid")
        return False

def run_diagnostics():
    """Run all diagnostic checks"""
    print("=" * 50)
    print("🤖 Expense Tracker Bot - Diagnostic Check")
    print("=" * 50)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Tesseract OCR", check_tesseract),
        ("Database", check_database),
        ("Configuration", check_config),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed: {str(e)}")
            results[name] = False
        print()
    
    print("=" * 50)
    print("📋 Summary:")
    print("=" * 50)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All checks passed! Bot is ready to run.")
        print("\nStart the bot with: python main.py")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
