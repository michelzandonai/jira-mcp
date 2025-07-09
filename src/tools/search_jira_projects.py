from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class SearchProjectsInput(BaseModel):
    """Define os argumentos para a ferramenta de busca de projetos."""
    search_term: str = Field(default="", description="Termo para filtrar projetos por nome ou chave. Se vazio, lista todos os projetos visíveis.")

def search_jira_projects_func(tool_input: SearchProjectsInput) -> str:
    """
    Busca e lista projetos do Jira. Pode filtrar por um termo de busca ou listar todos os projetos disponíveis.
    Use esta ferramenta para descobrir projetos ou encontrar a chave de um projeto específico.
    """
    try:
        jira_client = utils.get_jira_client()
        
        projects = jira_client.projects()
        
        if not projects:
            return "Nenhum projeto encontrado no Jira."
        
        search_term = tool_input.search_term
        if search_term:
            search_term_lower = search_term.lower()
            filtered_projects = [
                p for p in projects 
                if search_term_lower in p.name.lower() or search_term_lower in p.key.lower()
            ]
            projects = filtered_projects
            
            if not projects:
                return f"Nenhum projeto encontrado com o termo '{search_term}'."
        
        result = [
            f"Projetos encontrados com o termo '{search_term}':" if search_term 
            else f"Todos os projetos disponíveis ({len(projects)} encontrados):",
            ""
        ]
        
        for project in projects:
            project_type = getattr(project, 'projectTypeKey', 'N/A')
            result.append(f"• {project.key} - {project.name} (Tipo: {project_type})")
        
        return "\n".join(result)

    except Exception as e:
        return f"Erro ao buscar projetos no Jira: {e}"

search_jira_projects = FunctionTool(search_jira_projects_func)
search_jira_projects.name = "search_jira_projects" 