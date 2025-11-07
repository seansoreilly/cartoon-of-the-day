#!/usr/bin/env python3
"""Setup verification script for Cartoon of the Day."""

import sys
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_required_packages():
    """Verify all required packages are installed."""
    required = {
        'streamlit': '1.32.0',
        'streamlit_js_eval': '0.1.5',
        'google.generativeai': '0.5.0',
        'geopy': '2.4.1',
        'geocoder': '1.38.1',
        'dotenv': '1.0.0',
        'pytz': '2024.1',
        'PIL': '10.3.0',
        'timezonefinder': '6.2.0',
        'requests': '2.31.0',
    }

    missing = []
    outdated = []

    for package, min_version in required.items():
        try:
            if package == 'dotenv':
                import dotenv
                pkg = dotenv
            elif package == 'PIL':
                import PIL
                pkg = PIL
            elif package == 'google.generativeai':
                import google.generativeai
                pkg = google.generativeai
            else:
                pkg = __import__(package)

            version = getattr(pkg, '__version__', 'unknown')
            print(f"✅ {package} ({version})")

        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)

    return len(missing) == 0


def check_api_keys():
    """Verify API keys are configured."""
    try:
        from dotenv import load_dotenv
        import os

        load_dotenv()

        google_key = os.getenv('GOOGLE_API_KEY')
        news_key = os.getenv('NEWSAPI_KEY')

        if google_key:
            print("✅ GOOGLE_API_KEY configured")
        else:
            print("⚠️  GOOGLE_API_KEY not found (required for cartoon generation)")

        if news_key:
            print("✅ NEWSAPI_KEY configured")
        else:
            print("ℹ️  NEWSAPI_KEY not found (optional - will use fictional news)")

        return bool(google_key)

    except Exception as e:
        print(f"❌ Error checking API keys: {e}")
        return False


def check_directories():
    """Verify required directories exist."""
    dirs = [
        'src',
        'tests',
        'data',
        'data/cartoons',
        '.streamlit',
    ]

    all_exist = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"⚠️  {dir_path}/ missing (will be created)")
            path.mkdir(parents=True, exist_ok=True)
            all_exist = False

    return True  # Always return True since we auto-create


def check_https_warning():
    """Warn about HTTPS requirement for browser geolocation."""
    print("\n⚠️  IMPORTANT: Browser geolocation requires HTTPS")
    print("   • Local development (localhost): May work on some browsers")
    print("   • Production: Deploy to Streamlit Cloud or use HTTPS")
    print("   • Fallback: IP-based location or manual entry always available")


def main():
    """Run all verification checks."""
    print("🔍 Verifying Cartoon of the Day Setup\n")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("API Keys", check_api_keys),
        ("Directories", check_directories),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("\n📊 Summary:")
    print("-" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    check_https_warning()

    print("\n" + "=" * 60)

    if all_passed:
        print("\n🎉 Setup verification complete! Ready to run:")
        print("   streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("   Install missing packages: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
