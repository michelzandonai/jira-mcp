"""
Main entry point for Jira Agent application.

This module provides the main entry point for running the Jira Agent
with the new ADK-based architecture.
"""

import sys
import os
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    try:
        from src.api.main import app
        import uvicorn
        from src.core.config import get_settings
        
        settings = get_settings()
        
        print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
        print(f"📍 Environment: {settings.environment}")
        print(f"🤖 Model: {settings.google_model}")
        print(f"🌐 Server: http://{settings.api_host}:{settings.api_port}")
        print(f"📚 Docs: http://{settings.api_host}:{settings.api_port}/docs")
        print("")
        
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.auto_reload and settings.environment == "development",
            log_level=settings.log_level.lower()
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("Check your .env configuration and ensure all required variables are set.")
        sys.exit(1)