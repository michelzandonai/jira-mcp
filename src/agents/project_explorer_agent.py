import os
from dotenv import load_dotenv
from jira import JIRA
from google.adk.agents import Agent

# Importa as configurações já carregadas
import config

# Configurações
JIRA_SERVER = os.getenv("JIRA_SERVER_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

def _find_project_key_by_name_or_key(jira_client: JIRA, project_identifier: str) -> str | None:
    """
    Busca a chave de um projeto pelo nome (parcial ou completo) ou pela chave exata.

    Args:
        jira_client: O cliente JIRA inicializado.
        project_identifier: O nome (ex: 'Meu Projeto', 'Bolt') ou a chave exata (ex: 'MP').

    Returns:
        A chave do projeto encontrada ou uma mensagem de erro se for ambíguo ou não encontrado.
    """
    try:
        projects = jira_client.projects()
        normalized_identifier = project_identifier.lower()
        
        found_projects = []
        for project in projects:
            # Busca pela chave exata ou pelo nome parcial (contém)
            if project.key.lower() == normalized_identifier:
                return project.key # Retorna imediatamente se encontrar a chave exata
            if normalized_identifier in project.name.lower():
                found_projects.append(project)

        if len(found_projects) == 1:
            return found_projects[0].key
        elif len(found_projects) > 1:
            # Se mais de um projeto for encontrado, retorna uma mensagem de erro para desambiguação
            project_list = ", ".join([f"'{p.name}' ({p.key})" for p in found_projects])
            return f"Ambiguidade encontrada. O termo '{project_identifier}' corresponde a múltiplos projetos: {project_list}. Por favor, seja mais específico ou use a chave do projeto."
        
        return None # Nenhum projeto encontrado
    except Exception:
        return None

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
        
        # Busca todos os projetos disponíveis
        projects = jira_client.projects()
        
        if not projects:
            return "Nenhum projeto encontrado no Jira."
        
        # Filtra projetos se um termo de busca foi fornecido
        if search_term:
            search_term_lower = search_term.lower()
            filtered_projects = []
            for project in projects:
                if (search_term_lower in project.name.lower() or 
                    search_term_lower in project.key.lower()):
                    filtered_projects.append(project)
            projects = filtered_projects
            
            if not projects:
                return f"Nenhum projeto encontrado com o termo '{search_term}'."
        
        # Formata a resposta
        result = []
        if search_term:
            result.append(f"Projetos encontrados com o termo '{search_term}':")
        else:
            result.append(f"Todos os projetos disponíveis ({len(projects)} encontrados):")
        
        result.append("")
        
        for project in projects:
            project_type = getattr(project, 'projectTypeKey', 'N/A')
            result.append(f"• {project.key} - {project.name} (Tipo: {project_type})")
        
        return "\n".join(result)

    except Exception as e:
        return f"Erro ao buscar projetos no Jira: {e}"

def get_project_details(project_name_or_key: str) -> str:
    """
    Obtém detalhes específicos de um projeto do Jira, buscando pelo nome ou chave.

    Args:
        project_name_or_key: A chave ('PROJ') ou o nome ('Meu Projeto') do projeto.

    Returns:
        Detalhes formatados do projeto incluindo descrição, lead, e componentes.
    """
    try:
        jira_client = JIRA(
            server=config.JIRA_SERVER, 
            basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN)
        )
        
        project_key_or_error = _find_project_key_by_name_or_key(jira_client, project_name_or_key)
        if not project_key_or_error or "Ambiguidade encontrada" in project_key_or_error:
            error_message = project_key_or_error or f"Projeto '{project_name_or_key}' não encontrado."
            return f"❌ Erro: {error_message}"
        
        project_key = project_key_or_error
        
        # Busca o projeto específico
        project = jira_client.project(project_key)
        
        result = []
        result.append(f"Detalhes do Projeto: {project.key}")
        result.append("=" * 50)
        result.append(f"Nome: {project.name}")
        result.append(f"Chave: {project.key}")
        result.append(f"Tipo: {getattr(project, 'projectTypeKey', 'N/A')}")
        
        if hasattr(project, 'description') and project.description:
            result.append(f"Descrição: {project.description}")
        
        if hasattr(project, 'lead') and project.lead:
            result.append(f"Líder do Projeto: {project.lead.displayName}")
        
        # Busca componentes do projeto
        components = jira_client.project_components(project_key)
        if components:
            result.append("\nComponentes disponíveis:")
            for component in components:
                result.append(f"• {component.name}")
        
        return "\n".join(result)

    except Exception as e:
        return f"Erro ao buscar detalhes do projeto '{project_name_or_key}': {e}" 