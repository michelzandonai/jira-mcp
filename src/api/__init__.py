"""
API module for Jira Agent application.

This module contains the FastAPI application and routing configuration.
"""

from .main import app

__all__ = [
    "app"
]