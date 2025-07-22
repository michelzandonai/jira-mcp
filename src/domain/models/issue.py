"""
Issue domain model for Jira Agent.

This module defines the issue entity and its validation rules.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from .base import (
    BaseJiraModel, 
    ProjectIdentifierMixin, 
    TimeEstimateMixin, 
    WorklogMixin, 
    IssueBaseMixin
)
from ...core.validators import validate_time_format, sanitize_summary, sanitize_description


class IssueModel(BaseModel):
    """
    Domain model for a Jira issue.
    
    Represents the essential information about a Jira issue
    with business validation rules.
    """
    
    key: Optional[str] = Field(None, description="Issue key (e.g., 'PROJ-123')")
    project_key: str = Field(..., description="Project key where issue belongs")
    summary: str = Field(..., description="Issue summary/title")
    description: Optional[str] = Field("", description="Issue description")
    issue_type: str = Field(default="Task", description="Issue type (e.g., 'Task', 'Bug')")
    status: Optional[str] = Field(None, description="Current issue status")
    priority: Optional[str] = Field(None, description="Issue priority")
    assignee: Optional[str] = Field(None, description="Assignee account ID")
    reporter: Optional[str] = Field(None, description="Reporter account ID")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    original_estimate: Optional[str] = Field(None, description="Original time estimate")
    remaining_estimate: Optional[str] = Field(None, description="Remaining time estimate")
    time_spent: Optional[str] = Field(None, description="Time already spent")
    url: Optional[str] = Field(None, description="Issue URL in Jira")
    
    @validator("summary")
    def validate_summary(cls, v):
        """Validate and sanitize issue summary."""
        if not v or not v.strip():
            raise ValueError("Issue summary cannot be empty")
        
        sanitized = sanitize_summary(v)
        
        if len(sanitized) < 3:
            raise ValueError("Issue summary must be at least 3 characters long")
        
        return sanitized
    
    @validator("description")
    def validate_description(cls, v):
        """Validate and sanitize issue description."""
        if v is None:
            return ""
        return sanitize_description(v)
    
    @validator("issue_type")
    def validate_issue_type(cls, v):
        """Validate issue type."""
        if not v or not v.strip():
            return "Task"  # Default to Task
        
        return v.strip().title()  # Capitalize first letter
    
    @validator("original_estimate", "remaining_estimate", "time_spent")
    def validate_time_estimates(cls, v):
        """Validate time estimate formats."""
        if v and not validate_time_format(v):
            raise ValueError(f"Invalid time format: '{v}'. Use format like '2h 30m', '1d', '4h'")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


class IssueCreateInput(
    BaseJiraModel,
    ProjectIdentifierMixin,
    IssueBaseMixin,
    TimeEstimateMixin,
    WorklogMixin
):
    """
    Modelo de entrada para criar uma nova issue.
    
    Combina múltiplos mixins para fornecer funcionalidade completa
    de criação de issues com validação robusta.
    """
    
    assignee_email: Optional[str] = Field(None, description="Email do responsável pela issue")


