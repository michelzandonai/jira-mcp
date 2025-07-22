"""
Project-related tools for Jira Agent.

These tools handle project operations like searching and getting details.
"""

from .search_projects import search_projects
from .get_project_details import get_project_details

__all__ = [
    "search_projects",
    "get_project_details"
]