from google.adk.agents import Agent

# Importa as configurações centralizadas
import config

# Importa as FERRAMENTAS dos novos módulos individuais
from tools.search_jira_projects import search_jira_projects
from tools.get_project_details import get_project_details
from tools.search_issues_by_summary import search_issues_by_summary
from tools.create_issue import create_issue
from tools.get_issue_types import get_issue_types
from tools.log_work_on_issue import log_work_on_issue
from tools.update_issue_estimates import update_issue_estimates
from tools.batch_log_work import batch_log_work
from tools.batch_create_issues import batch_create_issues

# Importa o handler do guardrail
from agents.guardrails import before_tool_callback_handler

# --- Definição do Agente Mestre Central ---
# O ADK irá procurar por uma variável no escopo global que seja uma instância de 'Agent'.
root_agent = Agent(
    # Nome que aparecerá no Cursor
    name="JiraAgent", 
    
    # Descrição que aparecerá no Cursor
    description="Agente para interagir com o Jira. Permite explorar projetos, criar issues e registrar horas.",
    
    model=config.GOOGLE_MODEL,
    tools=[
        # Ferramentas em Lote
        batch_log_work,
        batch_create_issues,
        # Ferramentas Individuais
        log_work_on_issue,
        create_issue,
        update_issue_estimates,
        search_jira_projects,
        get_project_details,
        search_issues_by_summary,
        get_issue_types,
    ],
    # Adiciona o guardrail para interceptar chamadas de ferramentas
    before_tool_callback=before_tool_callback_handler,
    instruction=(
        "Sua função é ser um assistente Jira. Analise o pedido do usuário e priorize o uso de ferramentas em LOTE sempre que possível.\n"
        "- Para registrar horas em MÚLTIPLAS tarefas de um projeto, use `batch_log_work`.\n"
        "- Para CRIAR MÚLTIPLAS issues de uma vez (com ou sem registro de horas), use `batch_create_issues`.\n"
        "- Para ações em UMA ÚNICA tarefa, use as ferramentas individuais (`log_work_on_issue`, `create_issue`, etc.).\n"
        "- Para buscar informações, use as ferramentas de busca."
    )
) 