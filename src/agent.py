"""
Agent module for Google ADK web interface.

This module exposes the root_agent that ADK looks for.
"""

from .agents.jira_agent import jira_agent

# The ADK looks for 'root_agent' in this module
root_agent = jira_agent