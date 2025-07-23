"""
Create issue tool for Jira Agent.

This tool allows the agent to create a new issue in Jira with validation and optional worklog.
"""

from datetime import datetime
from google.adk.tools import FunctionTool, ToolContext

from ...infrastructure.jira_client import get_jira_client
from ...domain.services.project_service import ProjectService
from ...domain.models.issue import IssueCreateInput
from ...core.exceptions import ProjectNotFoundError, JiraConnectionError
from ...core.validation_service import ValidationService
from ...core.error_handler import ErrorHandler
from ...core.logging_config import get_logger

logger = get_logger(__name__)


def create_issue_function(tool_input: IssueCreateInput, tool_context: ToolContext = None) -> str:
    """
    Cria uma nova issue no Jira com validação abrangente e worklog opcional.
    
    Esta ferramenta cria uma única issue com os detalhes especificados. Pode opcionalmente
    registrar tempo de trabalho imediatamente após a criação se time_spent for fornecido.
    
    Funcionalidades:
    - Validação e resolução de projeto por chave ou nome
    - Validação de tipo de issue
    - Validação de estimativas de tempo (original e restante)
    - Atribuição automática para o usuário atual
    - Criação opcional de worklog imediato
    - Tratamento abrangente de erros
    
    Args:
        tool_input: Parâmetros de criação de issue com validação
        tool_context: Contexto da ferramenta ADK
        
    Returns:
        str: Resultado formatado da operação
    """
    try:
        # Handle both dict and IssueCreateInput objects
        def get_field(field_name, default=None):
            if isinstance(tool_input, dict):
                return tool_input.get(field_name, default)
            else:
                return getattr(tool_input, field_name, default)
        
        # Get Jira client and services
        jira_client = get_jira_client()
        project_service = ProjectService(jira_client)
        
        # Validate and resolve project
        try:
            project_key = project_service.validate_project_access(get_field('project_identifier'))
        except Exception as e:
            error_msg = ErrorHandler.handle_tool_error(
                e, 
                "create_issue",
                {"project_identifier": get_field('project_identifier')}
            )
            return error_msg
        
        # Validar dados de worklog se fornecidos
        time_spent = get_field('time_spent')
        if time_spent:
            worklog_result = ValidationService.validate_worklog_data(
                time_spent,
                get_field('work_start_date') or "",
                get_field('work_description') or ""
            )
            if not worklog_result.is_valid:
                validation_error = ErrorHandler.create_validation_error(
                    "worklog_data", 
                    time_spent, 
                    worklog_result.errors[0]
                )
                error_msg = ErrorHandler.handle_tool_error(validation_error, "create_issue")
                return error_msg
        
        # Prepare issue fields
        issue_fields = {
            "project": {"key": project_key},
            "summary": get_field('summary', '').strip(),
            "description": get_field('description', '').strip(),
            "issuetype": {"name": get_field('issue_type')},
        }
        
        # Add time tracking if estimates provided
        original_estimate = get_field('original_estimate')
        remaining_estimate = get_field('remaining_estimate')
        if original_estimate or remaining_estimate:
            issue_fields["timetracking"] = {}
            if original_estimate:
                issue_fields["timetracking"]["originalEstimate"] = original_estimate
            if remaining_estimate:
                issue_fields["timetracking"]["remainingEstimate"] = remaining_estimate
        
        # Try to assign to current user
        try:
            current_user = jira_client.get_current_user()
            if current_user:
                issue_fields["assignee"] = {"accountId": current_user}
        except Exception as e:
            ErrorHandler.log_warning(
                f"Could not assign issue to current user: {str(e)}", 
                "create_issue",
                {"project_key": project_key}
            )
        
        # Create the issue
        try:
            new_issue = jira_client.create_issue(issue_fields)
            ErrorHandler.log_info(f"Created issue: {new_issue.key}", "create_issue")
            
            success_message = f"✅ Issue {new_issue.key} created successfully!"
            
            # Add worklog if requested
            if time_spent:
                try:
                    work_start_date = get_field('work_start_date')
                    work_datetime = datetime.strptime(work_start_date, '%Y-%m-%d')
                    jira_client.add_worklog(
                        new_issue.key,
                        time_spent,
                        work_datetime,
                        get_field('work_description') or get_field('description') or "Work logged during issue creation"
                    )
                    success_message += f" Work logged: {time_spent} on {work_start_date}."
                    
                except Exception as e:
                    ErrorHandler.log_warning(
                        f"Issue created but worklog failed: {str(e)}", 
                        "create_issue",
                        {"issue_key": new_issue.key}
                    )
                    success_message += f" ⚠️ Issue created but failed to log work: {str(e)}"
            
            # Add issue URL if available
            if hasattr(new_issue, 'permalink'):
                success_message += f"\nURL: {new_issue.permalink()}"
            
            return success_message
            
        except Exception as e:
            error_msg = ErrorHandler.handle_tool_error(
                e, 
                "create_issue",
                {"project_key": project_key, "issue_fields": issue_fields}
            )
            return error_msg
        
    except Exception as e:
        error_msg = ErrorHandler.handle_tool_error(e, "create_issue")
        return error_msg


# Create the FunctionTool instance
create_issue = FunctionTool(func=create_issue_function)