"""
Root agent for Google ADK web interface.

This is the main entry point that ADK looks for when running 'adk web'.
It exposes the Jira agent for the web interface.
"""

from .agents.jira_agent import jira_agent

# The ADK looks for a variable named 'root_agent'
root_agent = jira_agent