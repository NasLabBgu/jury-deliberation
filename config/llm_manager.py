"""LLM initialization and management utilities."""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseLanguageModel

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class LLMManager:
    """Manager class for LLM initialization and configuration."""
    
    def __init__(self):
        self.llm: Optional[BaseLanguageModel] = None
        self.api_key_source: Optional[str] = None
        self.current_model: Optional[str] = None
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment variable, .env file, or api_key file.
        
        Priority order:
        1. Environment variable (GOOGLE_API_KEY)
        2. .env file (if python-dotenv is available)
        3. api_key file (legacy support)
        
        Returns:
            API key string if found, None otherwise
        """
        # First, try environment variable
        api_key = os.environ.get('GOOGLE_API_KEY')
        
        if api_key:
            self.api_key_source = "environment variable"
            print(f"✅ API key loaded from environment variable")
            return api_key
        
        # Check if .env file was loaded and try again
        if DOTENV_AVAILABLE:
            # dotenv should have already loaded the .env file, but let's check again
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
                self.api_key_source = ".env file"
                print(f"✅ API key loaded from .env file")
                return api_key
        
        # Fallback to file-based approach for local development
        current_dir = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else current_dir

        # Try to find the api_key file in multiple possible locations
        possible_paths = [
            'api_key',  # Current directory
            os.path.join(script_dir, 'api_key'),  # Same directory as script
            os.path.join(current_dir, '..', 'api_key'),  # Parent directory
            os.path.join(script_dir, '..', 'api_key'),  # Parent of script directory
        ]

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        api_key = f.read().strip()
                    if api_key:  # Make sure the file isn't empty
                        self.api_key_source = path
                        print(f"✅ API key loaded from file: {path}")
                        return api_key
            except Exception:
                continue

        print("❌ API key not found in any of the expected locations.")
        print(f"   Current working directory: {current_dir}")
        print("\n🔧 To fix this, use one of these methods:")
        print("   1. Set environment variable: export GOOGLE_API_KEY='your-key-here'")
        print("   2. Create .env file with: GOOGLE_API_KEY=your-key-here")
        print("   3. Create api_key file with just: your-key-here")
        print("\n📁 Searched locations:")
        
        # Show .env file status
        env_path = os.path.join(current_dir, '.env')
        env_exists = "✓" if os.path.exists(env_path) else "✗"
        print(f"   {env_exists} .env -> {os.path.abspath(env_path)}")
        
        # Show api_key file locations
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"   {exists} {path} -> {abs_path}")
        
        print("\n🔑 Get your API key from: https://aistudio.google.com/app/apikey")
        
        return None

    def initialize_openai(self, model_name: str = "gpt-4", temperature: float = 0.7) -> Optional[ChatOpenAI]:
        """Initialize OpenAI LLM.
        
        Args:
            model_name: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            temperature: Model temperature setting
            
        Returns:
            Initialized ChatOpenAI instance or None if failed
        """
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ Cannot initialize OpenAI LLM - OPENAI_API_KEY not set")
            print("   Set OPENAI_API_KEY environment variable or add it to .env file")
            return None
        
        try:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)
            self.current_model = model_name
            print(f"✅ OpenAI LLM {model_name} initialized successfully")
            return self.llm
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI LLM with model {model_name}: {e}")
            self.llm = None
            self.current_model = None
            return None

    def initialize_gemini(self, model_name: str = "gemini-2.0-flash-001", temperature: float = 0.3) -> Optional[ChatGoogleGenerativeAI]:
        """Initialize Google Gemini LLM.
        
        Args:
            model_name: Gemini model name (e.g., "gemini-2.0-flash-001", "gemini-2.5-flash-preview-05-20")
            temperature: Model temperature setting
            
        Returns:
            Initialized ChatGoogleGenerativeAI instance or None if failed
        """
        api_key = self.get_api_key()
        
        if not api_key:
            print("❌ Cannot initialize Gemini LLM - no API key available")
            self.llm = None
            self.current_model = None
            return None
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key
            )
            self.current_model = model_name
            print(f"✅ Gemini LLM {model_name} initialized successfully")
            return self.llm
        except Exception as e:
            print(f"❌ Failed to initialize Gemini LLM with model {model_name}: {e}")
            self.llm = None
            self.current_model = None
            return None

    def test_connection(self) -> bool:
        """Test the API connection with a simple request.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.llm is None:
            print("⚠️ Cannot test API - LLM not initialized")
            return False
        
        try:
            print("🔍 Testing API connection...")
            test_response = self.llm.invoke([{"role": "user", "content": "Hello, can you respond with just 'API connection successful'?"}])
            print(f"✅ API test successful: {test_response.content}")
            return True
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            print("\nPossible solutions:")
            print("1. Check your internet connection")
            print("2. Verify your API key is correct and active")
            print("3. Check if you have sufficient API quota")
            print("4. Try again in a few moments (rate limiting)")
            return False

    def get_llm(self) -> Optional[BaseLanguageModel]:
        """Get the currently initialized LLM instance.
        
        Returns:
            Current LLM instance or None if not initialized
        """
        return self.llm

    def is_initialized(self) -> bool:
        """Check if LLM is initialized.
        
        Returns:
            True if LLM is initialized, False otherwise
        """
        return self.llm is not None

    def get_model_info(self) -> dict:
        """Get information about the current LLM configuration.
        
        Returns:
            Dictionary with model information
        """
        return {
            "initialized": self.is_initialized(),
            "model": self.current_model,
            "api_key_source": self.api_key_source
        }


# Global LLM manager instance
llm_manager = LLMManager()
