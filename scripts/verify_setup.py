#!/usr/bin/env python3
"""
Verify that the benchmark setup is correct.
Run this before running the benchmark.
"""

import sys
import os

def check_python_version():
    """Check Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. You have:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import google.genai
        print("✅ google-genai package installed")
        return True
    except ImportError:
        print("❌ google-genai package NOT installed")
        print("   Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if GOOGLE_API_KEY is set"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable NOT set")
        print("   Get your FREE API key at: https://makersuite.google.com/app/apikey")
        print("   Then set it:")
        print("   - Windows PowerShell: $env:GOOGLE_API_KEY='your-key-here'")
        print("   - Windows CMD: set GOOGLE_API_KEY=your-key-here")
        print("   - Linux/Mac: export GOOGLE_API_KEY='your-key-here'")
        return False
    print(f"✅ GOOGLE_API_KEY is set ({api_key[:10]}...)")
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "dialogues/dialogue_templates.jsonl",
        "patient_profiles_1500.csv",
        "scripts/run_benchmark.py",
        "scripts/auto_score.py",
        "scripts/create_scoring_sheet.py",
    ]

    all_exist = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✅ Found: {filepath}")
        else:
            print(f"❌ Missing: {filepath}")
            all_exist = False

    return all_exist

def check_syntax():
    """Check if scripts have valid syntax"""
    scripts_to_check = [
        "scripts/run_benchmark.py",
        "scripts/auto_score.py",
        "scripts/create_scoring_sheet.py"
    ]

    all_valid = True
    for script_path in scripts_to_check:
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                compile(f.read(), script_path, "exec")
            print(f"✅ {script_path} syntax is valid")
        except SyntaxError as e:
            print(f"❌ Syntax error in {script_path}: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            all_valid = False
        except UnicodeDecodeError as e:
            print(f"❌ Unicode error in {script_path}: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"❌ File not found: {script_path}")
            all_valid = False

    return all_valid

def main():
    print("=" * 70)
    print("🔍 VERIFYING BENCHMARK SETUP")
    print("=" * 70)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_files),
        ("Syntax Check", check_syntax),
        ("Dependencies", check_dependencies),
        ("API Key", check_api_key),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking: {name}")
        print("-" * 70)
        results.append(check_func())
        print()

    print("=" * 70)
    if all(results):
        print("✅ ALL CHECKS PASSED! You're ready to run the benchmark!")
        print("=" * 70)
        print("\nNext step:")
        print("  python run_benchmark.py --quick")
        return 0
    else:
        print("❌ SOME CHECKS FAILED. Please fix the issues above.")
        print("=" * 70)
        print("\nFor help, see: SETUP.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
