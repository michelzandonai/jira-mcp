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

# --- Definição do Agente Mestre Central ---
# O ADK irá procurar por uma variável no escopo global que seja uma instância de 'Agent'.
root_agent = Agent(
    # Nome que aparecerá no Cursor
    name="JiraAgent", 
    
    # Descrição que aparecerá no Cursor
    description="Agente para interagir com o Jira. Permite explorar projetos, criar issues e registrar horas.",
    
    model=config.GOOGLE_MODEL,
    tools=[
        search_jira_projects,
        get_project_details,
        search_issues_by_summary,
        create_issue,
        get_issue_types,
        log_work_on_issue,
        update_issue_estimates,
    ],
    instruction=(
        "Sua função é ser um assistente Jira. Analise o pedido do usuário e use a ferramenta apropriada.\n"
        "- Para criar, use `create_issue`.\n"
        "- Para modificar (registrar horas, atualizar estimativas), use `log_work_on_issue` ou `update_issue_estimates`. Forneça o nome do projeto e o nome ou chave da tarefa.\n"
        "- Para buscar informações, use as ferramentas de busca (`search_jira_projects`, `get_project_details`, `search_issues_by_summary`). Forneça o nome do projeto ou da tarefa que deseja buscar."
    )
) 