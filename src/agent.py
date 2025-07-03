from google.adk.agents import Agent

# Importa as configurações centralizadas
from . import config

# Importa as FERRAMENTAS dos nossos módulos de especialistas
from .agents.project_explorer_agent import search_jira_projects, get_project_details
from .agents.issue_creator_agent import create_issue, get_issue_types
from .agents.time_management_agent import log_work_on_issue, update_issue_estimates

# --- Definição do Agente Mestre Central ---
# O ADK irá procurar por uma variável no escopo global que seja uma instância de 'Agent'.
root_agent = Agent(
    name="jira_master_agent",
    model=config.GOOGLE_MODEL,
    tools=[
        # Ferramentas de criação e consulta de issues
        create_issue,
        get_issue_types,
        
        # Ferramentas de exploração de projetos
        search_jira_projects,
        get_project_details,
        
        # Ferramentas de gerenciamento de tempo
        log_work_on_issue,
        update_issue_estimates
    ],
    description="Agente mestre para gerenciar o Jira. Capaz de criar issues, consultar projetos, registrar horas e atualizar estimativas.",
    instruction=(
        "Sua função é ser um assistente Jira completo. Analise o pedido do usuário e escolha a ferramenta MAIS específica para a tarefa.\n"
        "1. PARA CRIAR: Use `create_issue`. Ela lida com todos os casos de criação.\n"
        "2. PARA MODIFICAR UMA ISSUE EXISTENTE: Seja preciso. Se o usuário quer 'registrar horas' ou 'tempo gasto', use `log_work_on_issue`. Se quer 'mudar a estimativa' ou 'tempo restante/previsto', use `update_issue_estimates`.\n"
        "3. PARA BUSCAR INFORMAÇÕES: Use `search_jira_projects` para encontrar projetos, `get_project_details` para detalhes de um projeto, e `get_issue_types` para listar os tipos de issue de um projeto."
    )
) 