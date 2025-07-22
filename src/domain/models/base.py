"""
Base models for Jira Agent domain.

This module contains reusable base models that provide common
functionality and validation patterns.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator

from ...core.validation_service import ValidationService


class BaseJiraModel(BaseModel):
    """
    Base model for all Jira-related entities.
    
    Provides common configuration and validation patterns.
    """
    
    class Config:
        """Common Pydantic configuration for all Jira models."""
        validate_assignment = True
        extra = "forbid"
        use_enum_values = True


class ProjectIdentifierMixin(BaseModel):
    """
    Mixin for models that need to identify a Jira project.
    
    Provides flexible project identification by key or name.
    """
    
    project_identifier: str = Field(
        ...,
        description=(
            "Identificador do projeto. Pode ser a chave do projeto (ex: 'PROJ') "
            "ou nome do projeto (ex: 'Meu Projeto'). A busca não diferencia maiúsculas de minúsculas."
        )
    )




class TimeEstimateMixin(BaseModel):
    """
    Mixin for models that include time estimation fields.
    
    Provides validated time tracking fields with Jira format.
    """
    
    original_estimate: Optional[str] = Field(
        None,
        description=(
            "Estimativa de tempo original (opcional). "
            "Use formato de tempo do Jira: '2w 3d 4h 5m' ou combinações como '1d 4h', '2h 30m'."
        )
    )
    
    remaining_estimate: Optional[str] = Field(
        None,
        description=(
            "Estimativa de tempo restante (opcional). "
            "Use formato de tempo do Jira: '2w 3d 4h 5m' ou combinações como '1d 4h', '2h 30m'."
        )
    )
    
    @validator("original_estimate", "remaining_estimate")
    def validate_time_estimates(cls, v):
        """Validate time estimate formats."""
        if not v:
            return v
        
        result = ValidationService.validate_time_format(v)
        if not result.is_valid:
            raise ValueError(result.errors[0])
        
        return result.sanitized_value


class WorklogMixin(BaseModel):
    """
    Mixin for models that include worklog fields.
    
    Provides validated worklog-related fields.
    """
    
    time_spent: Optional[str] = Field(
        None,
        description=(
            "Tempo gasto (opcional). "
            "Use formato de tempo do Jira: '2h 30m', '1d', '4h', etc."
        )
    )
    
    work_start_date: Optional[str] = Field(
        None,
        description=(
            "Data do trabalho (obrigatório se time_spent for fornecido). "
            "Use formato YYYY-MM-DD, ex: '2024-01-15'."
        )
    )
    
    work_description: Optional[str] = Field(
        None,
        description="Descrição do trabalho realizado para o worklog."
    )
    
    @validator("time_spent")
    def validate_time_spent(cls, v):
        """Validate time spent format."""
        if not v:
            return v
        
        result = ValidationService.validate_time_format(v)
        if not result.is_valid:
            raise ValueError(result.errors[0])
        
        return result.sanitized_value


class IssueBaseMixin(BaseModel):
    """
    Mixin for models with basic issue information.
    
    Provides validated basic issue fields.
    """
    
    summary: str = Field(..., description="Título/resumo da issue. Deve ser claro e descritivo.")
    
    description: Optional[str] = Field(
        "",
        description="Descrição detalhada da issue. Pode incluir formatação e requisitos."
    )
    
    issue_type: str = Field(
        default="Task",
        description="Tipo de issue (ex: 'Task', 'Bug', 'Story', 'Epic'). Padrão é 'Task'."
    )
    
    @validator("summary")
    def validate_summary(cls, v):
        """Validate and sanitize issue summary."""
        result = ValidationService.validate_issue_summary(v)
        if not result.is_valid:
            raise ValueError(result.errors[0])
        
        return result.sanitized_value
    
    @validator("description")
    def validate_description(cls, v):
        """Validate and sanitize issue description."""
        result = ValidationService.validate_issue_description(v or "")
        return result.sanitized_value
    
    @validator("issue_type")
    def validate_issue_type(cls, v):
        """Validate issue type."""
        if not v or not v.strip():
            return "Task"  # Default to Task
        
        return v.strip().title()  # Capitalize first letter


