"""
Main Jira Agent using Google ADK.

This module defines the primary agent that handles all Jira interactions
using the proper ADK patterns and tools.
"""

from google.adk.agents import LlmAgent

from ..core.config import get_settings
from ..core.logging_config import get_logger
from ..tools.project.search_projects import search_projects
from ..tools.project.get_project_details import get_project_details
from ..tools.issue.create_issue import create_issue
from ..tools.issue.list_issues import list_issues  
from ..tools.issue.add_worklog import add_worklog

logger = get_logger(__name__)


def create_jira_agent() -> LlmAgent:
    """
    Create and configure the main Jira agent.
    
    Returns:
        LlmAgent: Configured Jira agent with all tools
    """
    settings = get_settings()
    
    # Instrução do agente em português
    instruction = """
    Você é um assistente especializado em Jira que ajuda usuários a gerenciar seus projetos e issues.
    
    Suas principais capacidades:
    - Buscar e explorar projetos do Jira
    - Obter informações detalhadas sobre projetos
    - Listar issues de projetos específicos
    - Criar novas issues com validação adequada
    - Adicionar registros de tempo de trabalho a issues existentes
    - Lidar com operações individuais e em lote
    
    Sempre priorize a segurança do usuário e integridade dos dados:
    - Valide identificadores de projetos e issues antes de operações
    - Forneça feedback claro sobre as ações realizadas
    - Se algo falhar, explique o motivo e sugira alternativas
    - Use operações em lote quando o usuário precisar realizar múltiplas ações similares
    
    Quando usuários perguntarem sobre informações de projetos, ajude-os a encontrar o projeto correto primeiro.
    Ao criar issues, certifique-se de que todas as informações necessárias sejam fornecidas e validadas.
    
    Seja conciso mas completo em suas respostas, e sempre confirme operações bem-sucedidas
    com detalhes relevantes como chaves de issues ou URLs.
    
    Responda sempre em português brasileiro, de forma clara e profissional.
    """
    
    # Create the agent with proper ADK configuration
    agent = LlmAgent(
        name="JiraAgent",
        description=(
            "Um agente de integração com Jira que ajuda usuários a gerenciar projetos e issues. "
            "Pode buscar projetos, criar issues e lidar com várias operações do Jira "
            "com validação adequada e tratamento de erros."
        ),
        model=settings.google_model,
        instruction=instruction,
        tools=[
            # Project tools
            search_projects,
            get_project_details,
            
            # Issue tools  
            create_issue,
            list_issues,
            add_worklog,
            
            # Additional tools will be added here as they are implemented
        ]
    )
    
    logger.info(
        "Agente Jira criado com sucesso",
        extra={
            "model": settings.google_model,
            "tools_count": len(agent.tools),
            "environment": settings.environment
        }
    )
    
    return agent


# Create the global agent instance
jira_agent = create_jira_agent()