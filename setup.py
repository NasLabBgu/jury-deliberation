#!/usr/bin/env python3
"""
Setup script for AI Agents Jury Deliberation system.

This script helps users set up the environment and verify the installation.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_api_key():
    """Check if API key is configured."""
    print("\nChecking API key configuration...")
    
    # Check environment variable
    if os.environ.get('GOOGLE_API_KEY'):
        print("✅ GOOGLE_API_KEY found in environment variables")
        return True
    
    # Check for api_key file
    api_key_file = Path("api_key")
    if api_key_file.exists():
        print("✅ api_key file found")
        return True
    
    print("⚠️  No API key found")
    print("   Please either:")
    print("   1. Set environment variable: export GOOGLE_API_KEY='your-key-here'")
    print("   2. Create an 'api_key' file with your Google API key")
    print("   Get your API key from: https://aistudio.google.com/app/apikey")
    return False


def check_file_structure():
    """Check if required files and directories exist."""
    print("\nChecking file structure...")
    
    required_dirs = ["jurors", "cases"]
    required_files = ["main.py", "requirements.txt"]
    
    missing_dirs = []
    missing_files = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    for file_name in required_files:
        if not Path(file_name).exists():
            missing_files.append(file_name)
    
    if missing_dirs or missing_files:
        print("❌ Missing required files/directories:")
        for item in missing_dirs + missing_files:
            print(f"   - {item}")
        return False
    
    print("✅ All required files and directories present")
    return True


def test_imports():
    """Test if all modules can be imported."""
    print("\nTesting imports...")
    
    try:
        # Test core imports
        from jury_simulation.deliberation_simulator import DeliberationSimulator
        from config.llm_manager import llm_manager
        from output.formatter import output_formatter
        
        print("✅ Core modules imported successfully")
        
        # Test basic functionality
        simulator = DeliberationSimulator()
        print("✅ DeliberationSimulator created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 60)
    print("SETUP COMPLETED SUCCESSFULLY! 🎉")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Get your Google API key from: https://aistudio.google.com/app/apikey")
    print("2. Set your API key:")
    print("   export GOOGLE_API_KEY='your-api-key-here'")
    print("   # OR create an 'api_key' file with your key")
    print("\n3. Run the system:")
    print("   # Interactive mode:")
    print("   python main.py --interactive")
    print("\n   # Command-line mode:")
    print("   python main.py --jury jurors/jurors.yaml --case cases/Scenario\\ 1.txt --scenario 1")
    print("\n   # Get help:")
    print("   python main.py --help")
    print("\n4. Try the examples:")
    print("   python example_usage.py")
    print("\nFor more information, see README.md")
    print("=" * 60)


def main():
    """Main setup function."""
    print("AI AGENTS JURY DELIBERATION - SETUP")
    print("=" * 40)
    
    # Run checks
    checks = [
        check_python_version(),
        check_file_structure(),
        install_dependencies(),
        test_imports(),
        check_api_key()  # This one is optional, so don't fail on it
    ]
    
    # Count successful checks (excluding the optional API key check)
    required_checks = checks[:-1]
    api_key_check = checks[-1]
    
    if all(required_checks):
        if api_key_check:
            print("\n✅ ALL CHECKS PASSED!")
        else:
            print("\n✅ CORE SETUP COMPLETED (API key needed)")
        
        show_next_steps()
        return 0
    else:
        print("\n❌ SETUP FAILED")
        print("Please fix the issues above and run setup again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
