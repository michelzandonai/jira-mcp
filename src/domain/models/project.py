"""
Project domain model for Jira Agent.

This module defines the project entity and its validation rules.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator

from .base import BaseJiraModel


class ProjectModel(BaseJiraModel):
    """
    Domain model for a Jira project.
    
    Represents the essential information about a Jira project
    with business validation rules.
    """
    
    key: str = Field(..., description="Project key (e.g., 'PROJ')")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_type: Optional[str] = Field(None, description="Project type (e.g., 'software')")
    lead: Optional[str] = Field(None, description="Project lead account ID")
    url: Optional[str] = Field(None, description="Project URL in Jira")
    
    @validator("key")
    def validate_key(cls, v):
        """Validate project key format."""
        if not v or not v.strip():
            raise ValueError("Project key cannot be empty")
        
        # Project keys should be uppercase alphanumeric
        if not v.isupper():
            v = v.upper()
        
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Project key must contain only letters, numbers, hyphens, and underscores")
        
        return v
    
    @validator("name")
    def validate_name(cls, v):
        """Validate project name."""
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        
        if len(v.strip()) < 2:
            raise ValueError("Project name must be at least 2 characters long")
        
        return v.strip()
    
class ProjectSummary(BaseJiraModel):
    """
    Simplified project information for listings.
    """
    
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    project_type: Optional[str] = Field(None, description="Project type")
    
class ProjectSearchResult(BaseJiraModel):
    """
    Result of a project search operation.
    """
    
    projects: List[ProjectSummary] = Field(default_factory=list, description="Found projects")
    total_count: int = Field(0, description="Número total de resultados encontrados")
    search_term: Optional[str] = Field(None, description="Termo de busca utilizado")