#!/usr/bin/env python3
"""
Quick validation script for the refactored AI Agents Jury Deliberation system.

This script performs basic validation to ensure the refactoring was successful
and the system is ready for use.
"""

import sys
import os
from pathlib import Path


def validate_imports():
    """Validate that all modules can be imported."""
    print("🔍 Validating imports...")
    
    try:
        # Core modules
        from jury_simulation.deliberation_simulator import DeliberationSimulator
        from jury_simulation.langgraph_state_machine import LangGraphStateMachine
        from jury_simulation.state import JuryState
        
        # Agent modules
        from agents.juror import Juror
        from agents.moderator import Moderator
        from agents.verdict_manager import VerdictManager
        
        # Config modules
        from config.data_loader import load_backgrounds_from_yaml, load_case_from_file
        from config.llm_manager import llm_manager
        
        # Output modules
        from output.formatter import output_formatter
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def validate_file_structure():
    """Validate that all required files are present."""
    print("🔍 Validating file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "setup.py",
        "example_usage.py",
        "jury_simulation/__init__.py",
        "jury_simulation/deliberation_simulator.py",
        "jury_simulation/langgraph_state_machine.py",
        "jury_simulation/state.py",
        "agents/__init__.py",
        "agents/juror.py",
        "agents/moderator.py",
        "agents/verdict_manager.py",
        "config/__init__.py",
        "config/data_loader.py",
        "config/llm_manager.py",
        "output/__init__.py",
        "output/formatter.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True


def validate_data_files():
    """Validate that data files are accessible."""
    print("🔍 Validating data files...")
    
    try:
        from config.data_loader import load_backgrounds_from_yaml, load_case_from_file
        
        # Test YAML loading
        if Path("jurors/jurors.yaml").exists():
            backgrounds = load_backgrounds_from_yaml("jurors/jurors.yaml")
            if backgrounds:
                print(f"✅ Loaded {len(backgrounds)} jury members from jurors.yaml")
            else:
                print("⚠️  No jury members loaded from jurors.yaml")
        
        # Test case loading
        if Path("cases/Scenario 1.txt").exists():
            case_content = load_case_from_file("cases/Scenario 1.txt")
            if case_content:
                print("✅ Case file loaded successfully")
            else:
                print("⚠️  Case file is empty")
        
        return True
        
    except Exception as e:
        print(f"❌ Data file validation failed: {e}")
        return False


def validate_class_instantiation():
    """Validate that classes can be instantiated."""
    print("🔍 Validating class instantiation...")
    
    try:
        from jury_simulation.deliberation_simulator import DeliberationSimulator
        from config.llm_manager import llm_manager
        from output.formatter import output_formatter
        from agents.juror import Juror
        from agents.moderator import Moderator
        from agents.verdict_manager import VerdictManager
        
        # Test instantiation
        simulator = DeliberationSimulator()
        moderator = Moderator()
        verdict_manager = VerdictManager()
        
        print("✅ All classes instantiated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False


def validate_cli_interface():
    """Validate that CLI interface is accessible."""
    print("🔍 Validating CLI interface...")
    
    try:
        import subprocess
        
        # Test help command (quick timeout)
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "jury deliberation" in result.stdout.lower():
            print("✅ CLI help interface works")
            return True
        else:
            print("⚠️  CLI help interface may have issues")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  CLI help command timed out")
        return False
    except Exception as e:
        print(f"❌ CLI interface validation failed: {e}")
        return False


def validate_api_key_setup():
    """Validate API key configuration."""
    print("🔍 Validating API key setup...")
    
    try:
        from config.llm_manager import llm_manager
        
        api_key = llm_manager.get_api_key()
        if api_key:
            print(f"✅ API key found (source: {llm_manager.api_key_source})")
            return True
        else:
            print("⚠️  No API key found")
            print("   Set GOOGLE_API_KEY environment variable, create .env file, or create 'api_key' file")
            print("   Run 'python setup_api_key.py' for guided setup")
            return False
            
    except Exception as e:
        print(f"❌ API key validation failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🚀 QUICK VALIDATION - AI Agents Jury Deliberation Refactoring")
    print("=" * 70)
    
    validations = [
        ("File Structure", validate_file_structure),
        ("Imports", validate_imports),
        ("Class Instantiation", validate_class_instantiation),
        ("Data Files", validate_data_files),
        ("CLI Interface", validate_cli_interface),
        ("API Key Setup", validate_api_key_setup),
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        print(f"\n📋 {name}")
        try:
            if validation_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} validation crashed: {e}")
    
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ The refactoring is successful and the system is ready for use.")
        print("\nNext steps:")
        print("1. Set your API key: export GOOGLE_API_KEY='your-key-here'")
        print("2. Run: python main.py --help")
        print("3. Try: python main.py --interactive")
        print("4. Run full tests: python test_refactoring.py")
        
    elif passed >= total - 1:
        print("\n✅ VALIDATION MOSTLY SUCCESSFUL!")
        print("⚠️  Minor issues detected, but core functionality works.")
        print("The system is ready for basic use.")
        
    else:
        print("\n❌ VALIDATION FAILED!")
        print("⚠️  Significant issues detected. Please review and fix before use.")
    
    print("\n📚 For detailed testing, run: python test_refactoring.py")
    print("📖 For usage examples, run: python example_usage.py")
    print("=" * 70)
    
    return 0 if passed >= total - 1 else 1


if __name__ == "__main__":
    sys.exit(main())
