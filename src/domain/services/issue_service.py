"""
Issue business service for Jira Agent.

This service handles all issue-related business logic
and coordinates with the infrastructure layer.
"""

from typing import List, Optional
from datetime import datetime

from ...infrastructure.jira_client import JiraClientService
from ..models.issue import IssueSearchResult, IssueSummary
from ...core.exceptions import JiraConnectionError
from ...core.error_handler import ErrorHandler
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class IssueService:
    """
    Business service for issue operations.
    
    Handles issue-related business logic including search,
    retrieval, and information processing.
    """
    
    def __init__(self, jira_client: JiraClientService):
        """
        Initialize the issue service.
        
        Args:
            jira_client: Jira client service instance
        """
        self.jira_client = jira_client
    
    def get_project_issues(self, project_key: str, status_filter: Optional[str] = None, max_results: int = 50) -> IssueSearchResult:
        """
        Get issues from a specific project.
        
        Args:
            project_key: The project key to get issues from
            status_filter: Optional status to filter by
            max_results: Maximum number of issues to return
            
        Returns:
            IssueSearchResult: Search results with issues
            
        Raises:
            JiraConnectionError: If search fails
        """
        try:
            # Get issues from infrastructure layer
            jira_issues = self.jira_client.get_project_issues(project_key, status_filter, max_results)
            
            # Convert to domain models
            issue_summaries = []
            for jira_issue in jira_issues:
                # Extract assignee display name
                assignee_name = None
                if hasattr(jira_issue.fields, 'assignee') and jira_issue.fields.assignee:
                    assignee = jira_issue.fields.assignee
                    if hasattr(assignee, 'displayName'):
                        assignee_name = assignee.displayName
                    elif hasattr(assignee, 'name'):
                        assignee_name = assignee.name
                
                # Parse datetime fields
                created = None
                updated = None
                try:
                    if hasattr(jira_issue.fields, 'created') and jira_issue.fields.created:
                        created = datetime.fromisoformat(jira_issue.fields.created.replace('Z', '+00:00'))
                    if hasattr(jira_issue.fields, 'updated') and jira_issue.fields.updated:
                        updated = datetime.fromisoformat(jira_issue.fields.updated.replace('Z', '+00:00'))
                except ValueError:
                    # If datetime parsing fails, leave as None
                    pass
                
                issue_summary = IssueSummary(
                    key=jira_issue.key,
                    summary=getattr(jira_issue.fields, 'summary', ''),
                    status=getattr(jira_issue.fields.status, 'name', None) if hasattr(jira_issue.fields, 'status') else None,
                    assignee=assignee_name,
                    priority=getattr(jira_issue.fields.priority, 'name', None) if hasattr(jira_issue.fields, 'priority') else None,
                    issue_type=getattr(jira_issue.fields.issuetype, 'name', None) if hasattr(jira_issue.fields, 'issuetype') else None,
                    created=created,
                    updated=updated
                )
                issue_summaries.append(issue_summary)
            
            # Create result object
            result = IssueSearchResult(
                issues=issue_summaries,
                total_count=len(issue_summaries),
                project_key=project_key,
                status_filter=status_filter
            )
            
            ErrorHandler.log_info(
                f"Found {len(issue_summaries)} issues for project {project_key}", 
                "IssueService"
            )
            
            return result
            
        except Exception as e:
            ErrorHandler.handle_service_error(e, "IssueService", "get_project_issues", 
                                            {"project_key": project_key, "status_filter": status_filter})
            raise JiraConnectionError(f"Failed to get project issues: {str(e)}")
    
    def format_issue_list(self, issues: List[IssueSummary], project_key: str, status_filter: Optional[str] = None) -> str:
        """
        Format a list of issues for display.
        
        Args:
            issues: List of issue summaries
            project_key: Project key the issues belong to
            status_filter: Status filter applied (if any)
            
        Returns:
            str: Formatted issue list
        """
        if not issues:
            if status_filter:
                return f"No issues found in project '{project_key}' with status '{status_filter}'"
            else:
                return f"No issues found in project '{project_key}'"
        
        lines = []
        
        # Header
        if status_filter:
            lines.append(f"Issues in project '{project_key}' with status '{status_filter}' ({len(issues)} found):")
        else:
            lines.append(f"Issues in project '{project_key}' ({len(issues)} found):")
        
        lines.append("")
        
        # Issue list
        for issue in issues:
            status_text = f" [{issue.status}]" if issue.status else ""
            assignee_text = f" - {issue.assignee}" if issue.assignee else " - Unassigned"
            type_text = f" ({issue.issue_type})" if issue.issue_type else ""
            
            # Get issue URL
            issue_url = self.jira_client.get_issue_url(issue.key)
            
            lines.append(f"• {issue.key}{status_text}: {issue.summary}{assignee_text}{type_text}")
            lines.append(f"  🔗 {issue_url}")
        
        return "\n".join(lines)