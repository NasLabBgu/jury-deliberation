#!/usr/bin/env python3
"""
API Key Setup Script for AI Agents Jury Deliberation

This script helps users set up their API keys for the jury deliberation system.
It supports multiple methods of configuration including .env files.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create a .env file with user input."""
    print("🔑 Setting up API keys for AI Agents Jury Deliberation")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Setup cancelled.")
            return False
    
    print("\n📋 You'll need API keys for the LLM providers you want to use.")
    print("   At minimum, you need either Google Gemini OR OpenAI API key.")
    print("   You can get both and configure them for flexibility.")
    
    # Collect API keys
    env_content = []
    
    print("\n🤖 Google Gemini API Key")
    print("   Get your key from: https://aistudio.google.com/app/apikey")
    google_key = input("   Enter your Google Gemini API key (or press Enter to skip): ").strip()
    
    if google_key:
        env_content.append(f"GOOGLE_API_KEY={google_key}")
        print("✅ Google Gemini API key configured")
    else:
        print("⏭️  Skipping Google Gemini API key")
    
    print("\n🧠 OpenAI API Key")
    print("   Get your key from: https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if openai_key:
        env_content.append(f"OPENAI_API_KEY={openai_key}")
        print("✅ OpenAI API key configured")
    else:
        print("⏭️  Skipping OpenAI API key")
    
    # Add optional configurations
    env_content.append("")
    env_content.append("# Optional: Default model configuration")
    env_content.append("DEFAULT_LLM_PROVIDER=gemini")
    env_content.append("DEFAULT_MODEL=gemini-2.0-flash-001")
    env_content.append("DEFAULT_TEMPERATURE=0.3")
    env_content.append("")
    env_content.append("# Optional: Deliberation configuration")
    env_content.append("DEFAULT_ROUNDS=3")
    env_content.append("DEFAULT_OUTPUT_DIR=./output")
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write("\n".join(env_content))
        print(f"\n✅ .env file created successfully!")
        print(f"   Location: {Path('.env').absolute()}")
        
        if not google_key and not openai_key:
            print("\n⚠️  Warning: No API keys were configured.")
            print("   You'll need to add them manually to the .env file.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def create_api_key_file():
    """Create a simple api_key file (legacy method)."""
    print("\n🔑 Alternative: Create api_key file")
    print("   This is a simpler method but less secure.")
    
    api_key = input("Enter your Google Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided.")
        return False
    
    try:
        with open("api_key", "w") as f:
            f.write(api_key)
        print(f"✅ api_key file created successfully!")
        print(f"   Location: {Path('api_key').absolute()}")
        print("⚠️  Note: This file should be added to .gitignore")
        return True
        
    except Exception as e:
        print(f"❌ Error creating api_key file: {e}")
        return False


def test_api_key():
    """Test if the API key is working."""
    print("\n🧪 Testing API key configuration...")
    
    try:
        from config.llm_manager import llm_manager
        
        # Try to get API key
        api_key = llm_manager.get_api_key()
        if api_key:
            print("✅ API key found and loaded successfully!")
            
            # Try to initialize LLM
            llm = llm_manager.initialize_gemini("gemini-2.0-flash-001")
            if llm:
                print("✅ LLM initialization successful!")
                
                # Test connection (optional, uses API credits)
                test_connection = input("\n🔍 Test API connection? This will use API credits. (y/N): ").strip().lower()
                if test_connection in ['y', 'yes']:
                    if llm_manager.test_connection():
                        print("🎉 API connection test successful!")
                    else:
                        print("❌ API connection test failed.")
                        print("   Check your internet connection and API key validity.")
                else:
                    print("⏭️  Skipping connection test.")
                
                return True
            else:
                print("❌ LLM initialization failed.")
                return False
        else:
            print("❌ No API key found.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False


def show_setup_instructions():
    """Show manual setup instructions."""
    print("\n📖 Manual Setup Instructions")
    print("=" * 40)
    print("1. Create a .env file in the project root")
    print("2. Add your API keys to the .env file:")
    print("   GOOGLE_API_KEY=your_google_api_key_here")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print("3. Save the file")
    print("4. Run the system again")
    print("\n📁 Example .env file content:")
    print("   GOOGLE_API_KEY=AIzaSy...")
    print("   OPENAI_API_KEY=sk-...")
    print("\n🔗 Get API keys from:")
    print("   Google Gemini: https://aistudio.google.com/app/apikey")
    print("   OpenAI: https://platform.openai.com/api-keys")


def main():
    """Main setup function."""
    print("🚀 AI Agents Jury Deliberation - API Key Setup")
    print("=" * 50)
    
    # Check current status
    print("🔍 Checking current API key configuration...")
    
    try:
        from config.llm_manager import llm_manager
        api_key = llm_manager.get_api_key()
        
        if api_key:
            print("✅ API key already configured!")
            print(f"   Source: {llm_manager.api_key_source}")
            
            test_current = input("\n🧪 Test current configuration? (y/N): ").strip().lower()
            if test_current in ['y', 'yes']:
                test_api_key()
            
            return 0
        else:
            print("❌ No API key found.")
            
    except Exception as e:
        print(f"⚠️  Error checking configuration: {e}")
    
    # Offer setup options
    print("\n🔧 Setup Options:")
    print("1. Create .env file (Recommended)")
    print("2. Create api_key file (Simple)")
    print("3. Show manual instructions")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            if create_env_file():
                test_api_key()
            break
            
        elif choice == "2":
            if create_api_key_file():
                test_api_key()
            break
            
        elif choice == "3":
            show_setup_instructions()
            break
            
        elif choice == "4":
            print("👋 Setup cancelled.")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-4.")
    
    print("\n🎉 Setup complete!")
    print("You can now run the jury deliberation system.")
    print("Try: python main.py --help")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
