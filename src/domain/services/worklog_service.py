"""
Worklog business service for Jira Agent.

This service handles all worklog-related business logic
and coordinates with the infrastructure layer.
"""

from typing import Optional, List, Tuple
from datetime import datetime, date
from dateutil import parser

from ...infrastructure.jira_client import JiraClientService
from ..models.worklog import WorklogCreateInput
from ...core.exceptions import JiraConnectionError, IssueNotFoundError
from ...core.error_handler import ErrorHandler
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class WorklogService:
    """
    Business service for worklog operations.
    
    Handles worklog-related business logic including creation,
    validation, and processing.
    """
    
    def __init__(self, jira_client: JiraClientService):
        """
        Initialize the worklog service.
        
        Args:
            jira_client: Jira client service instance
        """
        self.jira_client = jira_client
    
    def add_worklog_to_issue(self, worklog_input: WorklogCreateInput) -> str:
        """
        Add a worklog entry to an existing issue.
        
        Args:
            worklog_input: Worklog creation input data
            
        Returns:
            str: Success message with worklog details
            
        Raises:
            IssueNotFoundError: If issue is not found
            JiraConnectionError: If worklog creation fails
        """
        try:
            # Parse work date
            work_datetime = self._parse_work_date(worklog_input.work_date)
            
            # Validate issue exists (this will raise IssueNotFoundError if not found)
            try:
                issue = self.jira_client.get_issue(worklog_input.issue_key)
                logger.info(f"Issue {worklog_input.issue_key} found: {issue.fields.summary}")
            except Exception as e:
                raise IssueNotFoundError(worklog_input.issue_key)
            
            # Add worklog
            success = self.jira_client.add_worklog(
                issue_key=worklog_input.issue_key,
                time_spent=worklog_input.time_spent,
                started=work_datetime,
                comment=worklog_input.description or ""
            )
            
            if success:
                # Get issue URL
                issue_url = self.jira_client.get_issue_url(worklog_input.issue_key)
                
                success_message = (
                    f"✅ Worklog added successfully to {worklog_input.issue_key}!\n"
                    f"Time: {worklog_input.time_spent}\n"
                    f"Date: {work_datetime.strftime('%Y-%m-%d')}\n"
                    f"🔗 Link: {issue_url}"
                )
                
                if worklog_input.description:
                    success_message += f"\nDescription: {worklog_input.description}"
                
                ErrorHandler.log_info(
                    f"Worklog added to {worklog_input.issue_key}: {worklog_input.time_spent}", 
                    "WorklogService"
                )
                
                return success_message
            else:
                raise JiraConnectionError("Failed to add worklog - unknown error")
                
        except IssueNotFoundError:
            raise
        except Exception as e:
            ErrorHandler.handle_service_error(
                e, "WorklogService", "add_worklog_to_issue", 
                {"issue_key": worklog_input.issue_key}
            )
            raise JiraConnectionError(f"Failed to add worklog: {str(e)}")
    
    def _parse_work_date(self, work_date: Optional[str]) -> datetime:
        """
        Parse work date string to datetime.
        
        Args:
            work_date: Date string in YYYY-MM-DD format, or None for today
            
        Returns:
            datetime: Parsed datetime object
        """
        if not work_date:
            # Default to today
            return datetime.combine(date.today(), datetime.min.time())
        
        try:
            # Parse date string
            parsed_date = parser.parse(work_date).date()
            # Combine with midnight time
            return datetime.combine(parsed_date, datetime.min.time())
        except (ValueError, parser.ParserError) as e:
            logger.warning(f"Invalid date format '{work_date}', using today: {e}")
            return datetime.combine(date.today(), datetime.min.time())
    
    def validate_issue_key(self, issue_key: str) -> bool:
        """
        Validate that an issue key exists and is accessible.
        
        Args:
            issue_key: Issue key to validate
            
        Returns:
            bool: True if issue exists and is accessible
        """
        try:
            self.jira_client.get_issue(issue_key)
            return True
        except Exception:
            return False
    
    def resolve_issue_identifier(self, issue_identifier: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve an issue identifier (key or summary) to an exact issue key.
        
        Args:
            issue_identifier: Issue key (e.g., "PROJ-123") or summary/name
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (issue_key, error_or_choice_message)
        """
        try:
            # First, check if it looks like an issue key (contains dash and uppercase)
            if '-' in issue_identifier and any(c.isupper() for c in issue_identifier):
                # Try to get the issue directly
                try:
                    issue = self.jira_client.get_issue(issue_identifier)
                    return issue_identifier, None
                except:
                    # If not found, continue to search by summary
                    pass
            
            # Search by summary across all projects
            issues, error = self.jira_client.search_issues_by_summary(issue_identifier)
            
            if error:
                return None, f"❌ Error searching for issue: {error}"
            
            if len(issues) == 0:
                return None, f"❌ No issues found matching '{issue_identifier}'"
            
            if len(issues) == 1:
                return issues[0].key, None
            
            # Multiple issues found - format options for user to choose
            options = []
            for issue in issues[:5]:  # Show max 5 options
                status = getattr(issue.fields.status, 'name', 'Unknown') if hasattr(issue.fields, 'status') else 'Unknown'
                assignee = "Unassigned"
                if hasattr(issue.fields, 'assignee') and issue.fields.assignee:
                    assignee = getattr(issue.fields.assignee, 'displayName', 'Unknown')
                
                issue_type = getattr(issue.fields.issuetype, 'name', 'Unknown') if hasattr(issue.fields, 'issuetype') else 'Unknown'
                issue_url = self.jira_client.get_issue_url(issue.key)
                
                options.append(f"• {issue.key} [{status}]: {issue.fields.summary} - {assignee} ({issue_type})\n  🔗 {issue_url}")
            
            choice_message = (
                f"❓ Multiple issues found matching '{issue_identifier}' ({len(issues)} found):\n\n" +
                "\n".join(options) +
                f"\n\nPlease specify the exact issue key (e.g., {issues[0].key}) to add the worklog."
            )
            
            if len(issues) > 5:
                choice_message += f"\n\n... and {len(issues) - 5} more issues found."
            
            return None, choice_message
                
        except Exception as e:
            ErrorHandler.handle_service_error(
                e, "WorklogService", "resolve_issue_identifier", 
                {"issue_identifier": issue_identifier}
            )
            return None, f"❌ Error resolving issue identifier: {str(e)}"