"""
Tools module for Jira Agent.

This module contains all the ADK tools that the agent can use
to interact with Jira, organized by functional area.
"""

# Import all tools to make them available for the agent
from .project.search_projects import search_projects
from .project.get_project_details import get_project_details

from .issue.create_issue import create_issue
from .issue.list_issues import list_issues
from .issue.add_worklog import add_worklog

# List of all available tools for easy import by the agent
ALL_TOOLS = [
    # Project tools
    search_projects,
    get_project_details,
    
    # Issue tools
    create_issue,
    list_issues,
    add_worklog,
]

__all__ = [
    "ALL_TOOLS",
    # Project tools
    "search_projects",
    "get_project_details", 
    # Issue tools
    "create_issue",
    "list_issues",
    "add_worklog",
]