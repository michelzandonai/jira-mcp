"""
Configuration management for Jira Agent.

This module handles all application configuration using environment variables
and provides validation for required settings.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Jira Configuration
    jira_server_url: str = Field(..., env="JIRA_SERVER_URL")
    jira_username: str = Field(..., env="JIRA_USERNAME") 
    jira_api_token: str = Field(..., env="JIRA_API_TOKEN")
    
    # Google ADK Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-2.0-flash", env="GOOGLE_MODEL")
    google_genai_use_vertexai: bool = Field(default=False, env="GOOGLE_GENAI_USE_VERTEXAI")
    google_cloud_project: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    google_cloud_region: Optional[str] = Field(default="us-central1", env="GOOGLE_CLOUD_REGION")
    
    # Application Configuration
    app_name: str = Field(default="Jira Agent", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # API Configuration
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    
    # Development Settings
    debug: bool = Field(default=True, env="DEBUG")
    auto_reload: bool = Field(default=True, env="AUTO_RELOAD")
    detailed_errors: bool = Field(default=True, env="DETAILED_ERRORS")
    
    @validator("jira_server_url")
    def validate_jira_url(cls, v):
        """Validate Jira server URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("JIRA_SERVER_URL must start with http:// or https://")
        if not v.endswith(".atlassian.net") and not v.startswith("http://localhost"):
            # Allow localhost for development, otherwise expect Atlassian domain
            if "localhost" not in v and "127.0.0.1" not in v:
                if not any(domain in v for domain in [".atlassian.net", ".jira.com"]):
                    raise ValueError("JIRA_SERVER_URL should be a valid Jira instance URL")
        return v.rstrip("/")
    
    @validator("jira_username")
    def validate_jira_username(cls, v):
        """Validate Jira username format (should be email)."""
        if "@" not in v:
            raise ValueError("JIRA_USERNAME should be an email address")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(valid_envs)}")
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    Uses singleton pattern to ensure settings are loaded only once.
    
    Returns:
        Settings: The application settings instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            raise ValueError(
                f"Failed to load application settings: {e}\n"
                "Please check your .env file and ensure all required variables are set. "
                "See .env.example for reference."
            )
    return _settings




# Convenience function for backward compatibility
def get_jira_config() -> dict:
    """
    Get Jira configuration as dictionary.
    
    Returns:
        dict: Jira connection parameters
    """
    settings = get_settings()
    return {
        "server": settings.jira_server_url,
        "username": settings.jira_username,
        "api_token": settings.jira_api_token
    }


def get_google_config() -> dict:
    """
    Get Google ADK configuration as dictionary.
    
    Returns:
        dict: Google/Gemini configuration parameters
    """
    settings = get_settings()
    return {
        "api_key": settings.google_api_key,
        "model": settings.google_model,
        "use_vertexai": settings.google_genai_use_vertexai,
        "project": settings.google_cloud_project,
        "region": settings.google_cloud_region
    }