"""
Custom exceptions for Jira Agent application.

This module defines application-specific exceptions to provide
better error handling and user feedback.
"""


class JiraAgentError(Exception):
    """Base exception for Jira Agent application."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class JiraConnectionError(JiraAgentError):
    """Exception raised when Jira connection fails."""
    
    def __init__(self, message: str = "Failed to connect to Jira"):
        super().__init__(message, "JIRA_CONNECTION_ERROR")


class JiraAuthenticationError(JiraAgentError):
    """Exception raised when Jira authentication fails."""
    
    def __init__(self, message: str = "Jira authentication failed"):
        super().__init__(message, "JIRA_AUTH_ERROR")


class ProjectNotFoundError(JiraAgentError):
    """Exception raised when a Jira project is not found."""
    
    def __init__(self, project_identifier: str):
        message = f"Project '{project_identifier}' not found"
        super().__init__(message, "PROJECT_NOT_FOUND")
        self.project_identifier = project_identifier


class IssueNotFoundError(JiraAgentError):
    """Exception raised when a Jira issue is not found."""
    
    def __init__(self, issue_identifier: str):
        message = f"Issue '{issue_identifier}' not found"
        super().__init__(message, "ISSUE_NOT_FOUND")
        self.issue_identifier = issue_identifier


class ValidationError(JiraAgentError):
    """Exception raised when input validation fails."""
    
    def __init__(self, field: str, value: str, reason: str):
        message = f"Validation failed for '{field}' with value '{value}': {reason}"
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.reason = reason


class PermissionError(JiraAgentError):
    """Exception raised when user lacks required permissions."""
    
    def __init__(self, operation: str, resource: str = None):
        if resource:
            message = f"Permission denied for operation '{operation}' on resource '{resource}'"
        else:
            message = f"Permission denied for operation '{operation}'"
        super().__init__(message, "PERMISSION_ERROR")
        self.operation = operation
        self.resource = resource


class ToolExecutionError(JiraAgentError):
    """Exception raised when a tool execution fails."""
    
    def __init__(self, tool_name: str, message: str):
        full_message = f"Tool '{tool_name}' execution failed: {message}"
        super().__init__(full_message, "TOOL_EXECUTION_ERROR")
        self.tool_name = tool_name