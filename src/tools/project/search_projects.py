"""
Search projects tool for Jira Agent.

This tool allows the agent to search for Jira projects by name or key,
or list all available projects.
"""

from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool, ToolContext

from ...infrastructure.jira_client import get_jira_client
from ...domain.services.project_service import ProjectService
from ...core.exceptions import JiraConnectionError
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class SearchProjectsInput(BaseModel):
    """Esquema de entrada para buscar projetos do Jira."""
    
    search_term: str = Field(
        default="",
        description=(
            "Termo de busca opcional para filtrar projetos por nome ou chave. "
            "Se vazio, todos os projetos disponíveis serão listados. "
            "Exemplos: 'Mobile', 'PROJ', 'website'"
        )
    )


def search_projects_function(tool_input: SearchProjectsInput, tool_context: ToolContext = None) -> dict:
    """
    Busca projetos do Jira ou lista todos os projetos disponíveis.
    
    Use esta ferramenta para:
    - Encontrar projetos por nome ou chave
    - Descobrir projetos disponíveis na instância do Jira
    - Obter chaves de projetos necessárias para outras operações
    
    A busca não diferencia maiúsculas de minúsculas e busca em chaves, nomes e descrições de projetos.
    Se nenhum termo de busca for fornecido, todos os projetos acessíveis são retornados.
    
    Args:
        tool_input: Parâmetros de busca incluindo termo de busca opcional
        tool_context: Contexto da ferramenta ADK
        
    Returns:
        dict: Resposta com status e resultado da operação
    """
    try:
        # Get Jira client and project service
        jira_client = get_jira_client()
        project_service = ProjectService(jira_client)
        
        # Perform the search
        search_term = tool_input.search_term.strip() if tool_input.search_term else None
        result = project_service.search_projects(search_term)
        
        # Format the results for display
        formatted_result = project_service.format_project_list(
            result.projects, 
            result.search_term
        )
        
        logger.info(f"Search projects completed: {result.total_count} projects found")
        
        return {"status": "success", "result": formatted_result}
        
    except JiraConnectionError as e:
        error_msg = f"❌ Failed to search projects: {e.message}"
        logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}
        
    except Exception as e:
        error_msg = f"❌ Unexpected error while searching projects: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}


# Create the FunctionTool instance
search_projects = FunctionTool(func=search_projects_function)