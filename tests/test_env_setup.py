#!/usr/bin/env python3
"""
Test script to verify .env file support is working correctly.
"""

import os
import sys
from pathlib import Path

def test_dotenv_loading():
    """Test if dotenv loading works."""
    print("🧪 Testing .env file support...")
    
    # Test 1: Check if python-dotenv is available
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv is available")
        
        # Test 2: Check if .env file exists
        env_file = Path(".env")
        if env_file.exists():
            print("✅ .env file exists")
            
            # Load .env file
            load_dotenv()
            
            # Test 3: Check if environment variables are loaded
            google_key = os.environ.get('GOOGLE_API_KEY')
            openai_key = os.environ.get('OPENAI_API_KEY')
            
            if google_key:
                print(f"✅ GOOGLE_API_KEY loaded from .env: {google_key[:10]}...")
            else:
                print("⚠️  GOOGLE_API_KEY not found in .env")
                
            if openai_key:
                print(f"✅ OPENAI_API_KEY loaded from .env: {openai_key[:10]}...")
            else:
                print("⚠️  OPENAI_API_KEY not found in .env")
                
        else:
            print("⚠️  .env file does not exist")
            print("   Create one using: python setup_api_key.py")
            
    except ImportError:
        print("❌ python-dotenv not available")
        return False
    
    return True

def test_llm_manager():
    """Test the LLM manager with .env support."""
    print("\n🧪 Testing LLM Manager...")
    
    try:
        # Import the updated LLM manager
        sys.path.insert(0, str(Path.cwd()))
        from config.llm_manager import llm_manager
        
        # Test API key detection
        api_key = llm_manager.get_api_key()
        
        if api_key:
            print(f"✅ API key found: {api_key[:10]}...")
            print(f"   Source: {llm_manager.api_key_source}")
            return True
        else:
            print("❌ No API key found")
            print("   Try running: python setup_api_key.py")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM manager: {e}")
        return False

def create_sample_env():
    """Create a sample .env file for testing."""
    print("\n📝 Creating sample .env file...")
    
    sample_content = """# Sample .env file for testing
# Replace with your actual API keys

GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.0-flash-001
DEFAULT_TEMPERATURE=0.3
"""
    
    try:
        with open(".env", "w") as f:
            f.write(sample_content)
        print("✅ Sample .env file created")
        print("   Edit .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing .env File Support")
    print("=" * 40)
    
    # Test 1: Check dotenv support
    dotenv_ok = test_dotenv_loading()
    
    # Test 2: Check LLM manager
    llm_ok = test_llm_manager()
    
    # If no .env file exists, offer to create one
    if not Path(".env").exists():
        print("\n📁 No .env file found. Would you like to create a sample one?")
        response = input("Create sample .env file? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            create_sample_env()
    
    print("\n📊 Test Results:")
    print(f"   .env support: {'✅' if dotenv_ok else '❌'}")
    print(f"   LLM manager: {'✅' if llm_ok else '❌'}")
    
    if dotenv_ok and llm_ok:
        print("\n🎉 .env file support is working correctly!")
    else:
        print("\n⚠️  Some issues detected. Check the messages above.")
    
    print("\n💡 Next steps:")
    print("   1. Edit .env file with your actual API keys")
    print("   2. Run: python quick_validation.py")
    print("   3. Run: python main.py --help")

if __name__ == "__main__":
    main()
