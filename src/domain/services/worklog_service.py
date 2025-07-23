"""
Worklog business service for Jira Agent.

This service handles all worklog-related business logic
and coordinates with the infrastructure layer.
"""

from typing import Optional
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
                success_message = (
                    f"✅ Worklog added successfully to {worklog_input.issue_key}!\n"
                    f"Time: {worklog_input.time_spent}\n"
                    f"Date: {work_datetime.strftime('%Y-%m-%d')}"
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