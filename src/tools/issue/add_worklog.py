"""
Add worklog tool for Jira Agent.

This tool allows the agent to add time tracking entries to existing issues.
"""

from typing import Optional
from google.adk.tools import FunctionTool, ToolContext

from ...infrastructure.jira_client import get_jira_client
from ...domain.services.worklog_service import WorklogService
from ...domain.models.worklog import WorklogCreateInput
from ...core.exceptions import IssueNotFoundError, JiraConnectionError
from ...core.logging_config import get_logger

logger = get_logger(__name__)


def add_worklog_function(
    issue_key: str, 
    time_spent: str, 
    work_date: str = "", 
    description: str = "", 
    tool_context: ToolContext = None
) -> str:
    """
    Adiciona registro de tempo de trabalho a uma issue existente do Jira.
    
    Use esta ferramenta para:
    - Registrar tempo trabalhado em issues já criadas
    - Documentar trabalho realizado com descrição
    - Manter controle de horas gastas em projetos
    
    Args:
        issue_key: Chave da issue (ex: 'PROJ-123', 'KAN-45')
        time_spent: Tempo gasto (ex: '2h 30m', '1d', '4h', '30m')
        work_date: Data do trabalho no formato YYYY-MM-DD (padrão: hoje)
        description: Descrição do trabalho realizado
        tool_context: Contexto da ferramenta ADK
        
    Returns:
        str: Resultado da operação de adição de worklog
    """
    try:
        logger.info(f"Adding worklog to issue: '{issue_key}', time: '{time_spent}', date: '{work_date}'")
        
        # Create worklog input
        try:
            worklog_input = WorklogCreateInput(
                issue_key=issue_key.strip(),
                time_spent=time_spent.strip(),
                work_date=work_date.strip() if work_date else None,
                description=description.strip() if description else ""
            )
        except Exception as e:
            return f"❌ Invalid input: {str(e)}"
        
        # Get Jira client and worklog service
        jira_client = get_jira_client()
        worklog_service = WorklogService(jira_client)
        
        # Add worklog
        result = worklog_service.add_worklog_to_issue(worklog_input)
        
        logger.info(f"Worklog added successfully to {issue_key}")
        
        return result
        
    except IssueNotFoundError as e:
        error_msg = f"❌ Issue not found: {e.issue_identifier}. Please verify the issue key is correct."
        logger.warning(error_msg, exc_info=True)
        return error_msg
        
    except JiraConnectionError as e:
        error_msg = f"❌ Failed to add worklog: {e.message}"
        logger.error(error_msg, exc_info=True)
        return error_msg
        
    except Exception as e:
        error_msg = f"❌ Unexpected error while adding worklog: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


# Create the FunctionTool instance
add_worklog = FunctionTool(func=add_worklog_function)