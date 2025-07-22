"""
Worklog domain model for Jira Agent.

This module defines the worklog entity and its validation rules.
"""

from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

from ...core.validators import validate_time_format, validate_date_format


class WorklogModel(BaseModel):
    """
    Domain model for a Jira worklog entry.
    
    Represents time tracking information for an issue
    with business validation rules.
    """
    
    id: Optional[str] = Field(None, description="Worklog ID")
    issue_key: str = Field(..., description="Issue key the worklog belongs to")
    author: Optional[str] = Field(None, description="Author account ID")
    time_spent: str = Field(..., description="Time spent (e.g., '2h 30m')")
    started: datetime = Field(..., description="When the work started")
    comment: Optional[str] = Field("", description="Work description/comment")
    created: Optional[datetime] = Field(None, description="When worklog was created")
    updated: Optional[datetime] = Field(None, description="When worklog was last updated")
    
    @validator("time_spent")
    def validate_time_spent(cls, v):
        """Validate time spent format."""
        if not v or not v.strip():
            raise ValueError("Time spent cannot be empty")
        
        if not validate_time_format(v):
            raise ValueError(f"Invalid time format: '{v}'. Use format like '2h 30m', '1d', '4h'")
        
        return v.strip()
    
    @validator("comment")
    def validate_comment(cls, v):
        """Validate worklog comment."""
        if v is None:
            return ""
        
        # Limit comment length
        if len(v) > 1000:
            return v[:997] + "..."
        
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


