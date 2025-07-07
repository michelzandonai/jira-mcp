from google.adk.agents import Agent

# Importa as configurações centralizadas
import config

# Importa as FERRAMENTAS dos nossos módulos de especialistas
from .project_explorer_agent import search_jira_projects, get_project_details, search_issues_by_summary
from .issue_creator_agent import create_issue, get_issue_types
from .time_management_agent import log_work_on_issue, update_issue_estimates

# --- Definição do Agente Mestre Central ---
# O ADK irá procurar por uma variável no escopo global que seja uma instância de 'Agent'.
root_agent = Agent(
    # Nome que aparecerá no Cursor
    name="JiraAgent", 
    
    # Descrição que aparecerá no Cursor
    description="Agente para interagir com o Jira. Permite explorar projetos, criar issues e registrar horas.",
    
    model=config.GOOGLE_MODEL,
    tools=[
        # Ferramentas de criação e consulta de issues
        create_issue,
        get_issue_types,
        
        # Ferramentas de exploração de projetos
        search_jira_projects,
        get_project_details,
        search_issues_by_summary,
        
        # Ferramentas de gerenciamento de tempo
        log_work_on_issue,
        update_issue_estimates
    ],
    instruction=(
        "Sua função é ser um assistente Jira completo. Analise o pedido do usuário e escolha a ferramenta MAIS específica para a tarefa.\n"
        "1. PARA CRIAR: Use `create_issue`. Ela lida com todos os casos de criação.\n"
        "2. PARA MODIFICAR UMA ISSUE EXISTENTE: Seja preciso. Se o usuário quer 'registrar horas' ou 'tempo gasto', use `log_work_on_issue`. Se quer 'mudar a estimativa' ou 'tempo restante/previsto', use `update_issue_estimates`.\n"
        "3. PARA BUSCAR INFORMAÇÕES DE PROJETOS: Use `search_jira_projects` para encontrar projetos e `get_project_details` para detalhes de um projeto.\n"
        "4. PARA BUSCAR ISSUES: Use `search_issues_by_summary` para encontrar tarefas existentes em um projeto pelo nome.\n"
        "5. PARA OUTRAS CONSULTAS: `get_issue_types` pode ser útil para listar os tipos de issue de um projeto antes de criar uma."
    )
) 