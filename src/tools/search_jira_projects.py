import os
from jira import JIRA
import config

def search_jira_projects(search_term: str = "") -> str:
    """
    Busca e lista projetos do Jira. Pode filtrar por um termo ou listar todos.

    Args:
        search_term: (Opcional) Termo para filtrar projetos por nome ou chave. Se vazio, lista todos.

    Returns:
        Lista formatada dos projetos encontrados.
    """
    try:
        jira_client = JIRA(
            server=config.JIRA_SERVER, 
            basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN)
        )
        
        projects = jira_client.projects()
        
        if not projects:
            return "Nenhum projeto encontrado no Jira."
        
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