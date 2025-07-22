"""
Get project details tool for Jira Agent.

This tool allows the agent to retrieve detailed information about a specific Jira project.
"""

import logging
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool, ToolContext

from ...infrastructure.jira_client import get_jira_client
from ...domain.services.project_service import ProjectService
from ...core.exceptions import ProjectNotFoundError, JiraConnectionError

logger = logging.getLogger(__name__)


class GetProjectDetailsInput(BaseModel):
    """Esquema de entrada para obter detalhes do projeto."""
    
    project_identifier: str = Field(
        ...,
        description=(
            "Identificador do projeto - pode ser a chave do projeto (ex: 'PROJ') ou nome do projeto (ex: 'Meu Projeto'). "
            "A busca não diferencia maiúsculas de minúsculas e buscará em chaves, nomes ou descrições de projetos."
        )
    )


def get_project_details_function(tool_input: GetProjectDetailsInput, tool_context: ToolContext = None) -> dict:
    """
    Obtém informações detalhadas sobre um projeto específico do Jira.
    
    Use esta ferramenta para:
    - Obter informações abrangentes sobre um projeto
    - Verificar a existência do projeto antes de criar issues
    - Entender a estrutura e configuração do projeto
    
    Args:
        tool_input: Parâmetros de identificação do projeto
        tool_context: Contexto da ferramenta ADK
        
    Returns:
        dict: Resposta com status e resultado da operação
    """
    try:
        # Get Jira client and project service
        jira_client = get_jira_client()
        project_service = ProjectService(jira_client)
        
        # Get project details
        project = project_service.get_project_by_identifier(tool_input.project_identifier)
        
        # Format the project details for display
        formatted_details = project_service.format_project_details(project)
        
        logger.info(f"Retrieved project details for: {project.key}")
        
        success_msg = f"✅ Project details retrieved successfully:\n\n{formatted_details}"
        return {"status": "success", "result": success_msg}
        
    except ProjectNotFoundError as e:
        error_msg = f"❌ Project not found: {e.message}"
        logger.warning(error_msg)
        return {"status": "error", "error_message": error_msg}
        
    except JiraConnectionError as e:
        error_msg = f"❌ Failed to get project details: {e.message}"
        logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}
        
    except Exception as e:
        error_msg = f"❌ Unexpected error while getting project details: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}


# Create the FunctionTool instance
get_project_details = FunctionTool(func=get_project_details_function)