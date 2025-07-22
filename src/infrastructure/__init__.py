"""
Infrastructure module for Jira Agent application.

This module contains the infrastructure layer components:
- External service clients (Jira)
- Data repositories
- External API integrations
"""

from .jira_client import JiraClientService, get_jira_client

__all__ = [
    "JiraClientService",
    "get_jira_client"
]