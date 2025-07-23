"""
Project business service for Jira Agent.

This service handles all project-related business logic
and coordinates with the infrastructure layer.
"""

from typing import List, Optional

from ...infrastructure.jira_client import JiraClientService
from ..models.project import ProjectModel, ProjectSummary, ProjectSearchResult
from ...core.exceptions import ProjectNotFoundError, JiraConnectionError
from ...core.error_handler import ErrorHandler
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class ProjectService:
    """
    Business service for project operations.
    
    Handles project-related business logic including search,
    validation, and information retrieval.
    """
    
    def __init__(self, jira_client: JiraClientService):
        """
        Initialize the project service.
        
        Args:
            jira_client: Jira client service instance
        """
        self.jira_client = jira_client
    
    def search_projects(self, search_term: Optional[str] = None) -> ProjectSearchResult:
        """
        Search for projects by term or get all projects.
        
        Args:
            search_term: Optional term to filter projects
            
        Returns:
            ProjectSearchResult: Search results with projects
            
        Raises:
            JiraConnectionError: If search fails
        """
        try:
            all_projects = self.jira_client.get_projects()
            
            project_summaries = []
            
            if search_term:
                # Filter projects by search term
                search_lower = search_term.lower()
                filtered_projects = [
                    p for p in all_projects
                    if (search_lower in p.key.lower() or 
                        search_lower in p.name.lower() or
                        (hasattr(p, 'description') and p.description and 
                         search_lower in p.description.lower()))
                ]
            else:
                filtered_projects = all_projects
            
            # Convert to domain models
            for project in filtered_projects:
                project_type = getattr(project, 'projectTypeKey', None)
                project_summaries.append(
                    ProjectSummary(
                        key=project.key,
                        name=project.name,
                        project_type=project_type
                    )
                )
            
            result = ProjectSearchResult(
                projects=project_summaries,
                total_count=len(project_summaries),
                search_term=search_term
            )
            
            ErrorHandler.log_info(f"Found {len(project_summaries)} projects for search term: {search_term}", "ProjectService")
            
            return result
            
        except Exception as e:
            ErrorHandler.handle_service_error(e, "ProjectService", "search_projects", {"search_term": search_term})
            raise JiraConnectionError(f"Failed to search projects: {str(e)}")
    
    def get_project_by_identifier(self, identifier: str) -> ProjectModel:
        """
        Get a project by its identifier (key or name).
        
        Args:
            identifier: Project key, name, or search term
            
        Returns:
            ProjectModel: The project information
            
        Raises:
            ProjectNotFoundError: If project is not found
            JiraConnectionError: If operation fails
        """
        try:
            # First try to find the project
            project_key, error = self.jira_client.find_project(identifier)
            
            if error:
                raise ProjectNotFoundError(identifier)
            
            # Get detailed project information
            project_details = self.jira_client.get_project_details(project_key)
            
            # Convert to domain model
            lead_id = None
            if hasattr(project_details, 'lead') and project_details.lead:
                lead = project_details.lead
                if hasattr(lead, 'accountId'):
                    lead_id = lead.accountId
                elif hasattr(lead, 'name'):
                    lead_id = lead.name
            
            project_model = ProjectModel(
                key=project_details.key,
                name=project_details.name,
                description=getattr(project_details, 'description', None),
                project_type=getattr(project_details, 'projectTypeKey', None),
                lead=lead_id,
                url=getattr(project_details, 'self', None)
            )
            
            ErrorHandler.log_info(f"Retrieved project: {project_model.key}", "ProjectService")
            
            return project_model
            
        except ProjectNotFoundError:
            raise
        except Exception as e:
            ErrorHandler.handle_service_error(e, "ProjectService", "get_project_by_identifier", {"identifier": identifier})
            raise JiraConnectionError(f"Failed to get project details: {str(e)}")
    
    def validate_project_access(self, identifier: str) -> str:
        """
        Validate that a project exists and is accessible.
        
        Args:
            identifier: Project identifier to validate
            
        Returns:
            str: Validated project key
            
        Raises:
            ProjectNotFoundError: If project is not found or not accessible
        """
        try:
            project_key, error = self.jira_client.find_project(identifier)
            
            if error:
                raise ProjectNotFoundError(identifier)
            
            ErrorHandler.log_info(f"Validated project access: {project_key}", "ProjectService")
            
            return project_key
            
        except Exception as e:
            ErrorHandler.handle_service_error(e, "ProjectService", "validate_project_access", {"identifier": identifier})
            raise JiraConnectionError(f"Failed to validate project access: {str(e)}")
    
    def get_project_issue_types(self, project_key: str) -> List[dict]:
        """
        Get available issue types for a specific project.
        
        Args:
            project_key: The project key
            
        Returns:
            List[dict]: Available issue types with id and name
            
        Raises:
            ProjectNotFoundError: If project is not found
            JiraConnectionError: If operation fails
        """
        try:
            issue_types = self.jira_client.get_issue_types(project_key)
            
            ErrorHandler.log_info(f"Retrieved {len(issue_types)} issue types for project {project_key}", "ProjectService")
            
            return issue_types
            
        except ProjectNotFoundError:
            raise
        except Exception as e:
            ErrorHandler.handle_service_error(e, "ProjectService", "get_project_issue_types", {"project_key": project_key})
            raise JiraConnectionError(f"Failed to get project issue types: {str(e)}")
    
    def format_project_list(self, projects: List[ProjectSummary], search_term: Optional[str] = None) -> str:
        """
        Format a list of projects for display.
        
        Args:
            projects: List of project summaries
            search_term: Optional search term used
            
        Returns:
            str: Formatted project list
        """
        if not projects:
            if search_term:
                return f"No projects found matching '{search_term}'"
            else:
                return "No projects found"
        
        lines = []
        
        if search_term:
            lines.append(f"Projects matching '{search_term}' ({len(projects)} found):")
        else:
            lines.append(f"All available projects ({len(projects)} found):")
        
        lines.append("")
        
        for project in projects:
            project_type = f" (Type: {project.project_type})" if project.project_type else ""
            lines.append(f"• {project.key} - {project.name}{project_type}")
        
        return "\n".join(lines)
    
    def format_project_details(self, project: ProjectModel) -> str:
        """
        Format project details for display.
        
        Args:
            project: Project model to format
            
        Returns:
            str: Formatted project details
        """
        lines = [
            f"Project: {project.name} ({project.key})",
            ""
        ]
        
        if project.description:
            lines.append(f"Description: {project.description}")
        
        if project.project_type:
            lines.append(f"Type: {project.project_type}")
        
        if project.url:
            lines.append(f"URL: {project.url}")
        
        return "\n".join(lines)