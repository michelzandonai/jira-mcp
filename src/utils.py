import os
from jira import JIRA, JIRAError
import dateparser
import config
import re


def get_jira_client():
    """Initializes and returns a JIRA client."""
    return JIRA(
        server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN)
    )

def find_project_by_identifier(jira_client: JIRA, identifier: str) -> tuple[str | None, str | None]:
    """
    Busca um projeto de forma inteligente pelo identificador, procurando na chave, nome e descrição.

    Args:
        jira_client: O cliente JIRA inicializado.
        identifier: O termo de busca (chave, nome, parte do nome ou da descrição).

    Returns:
        Uma tupla (project_key, error_message).
        - (project.key, None) se exatamente um projeto for encontrado.
        - (None, "mensagem de erro") se nenhum ou múltiplos projetos forem encontrados.
    """
    try:
        all_projects = jira_client.projects()
        normalized_identifier = identifier.lower()
        
        found_projects = []
        
        # Itera sobre todos os projetos para encontrar correspondências
        for project in all_projects:
            # Verifica a chave, nome e descrição
            key_match = project.key.lower() == normalized_identifier
            name_match = normalized_identifier in project.name.lower()
            
            description_match = False
            if hasattr(project, 'description') and project.description:
                description_match = normalized_identifier in project.description.lower()
            
            if key_match or name_match or description_match:
                found_projects.append(project)

        # Remove duplicatas se um projeto foi encontrado por múltiplos critérios
        unique_projects = list({p.key: p for p in found_projects}.values())

        if len(unique_projects) == 1:
            return unique_projects[0].key, None
        elif len(unique_projects) > 1:
            project_list = ", ".join([f"'{p.name}' ({p.key})" for p in unique_projects])
            return None, f"Ambiguidade encontrada. O termo '{identifier}' corresponde a múltiplos projetos: {project_list}. Por favor, seja mais específico ou use a chave do projeto."
        else:
            return None, f"Nenhum projeto encontrado com o identificador '{identifier}'."
            
    except Exception as e:
        return None, f"Erro ao buscar projeto no Jira: {e}"

def get_user_account_id_by_email(jira_client: JIRA, email: str) -> tuple[str | None, str | None]:
    """
    Busca o accountId de um usuário no Jira pelo seu email.

    Args:
        jira_client: O cliente JIRA inicializado.
        email: O email do usuário a ser buscado.

    Returns:
        Uma tupla (accountId, error_message).
    """
    try:
        users = jira_client.search_users(query=email, maxResults=1)
        if users:
            return users[0].accountId, None
        else:
            return None, f"Usuário com email '{email}' não encontrado."
    except JIRAError as e:
        if e.status_code == 403:
            return None, "O usuário configurado não tem permissão para buscar outros usuários no Jira."
        return None, f"Erro do Jira ao buscar usuário: {e.text}"
    except Exception as e:
        return None, f"Erro inesperado ao buscar usuário '{email}': {e}"

def find_issue_by_summary(jira_client: JIRA, project_key: str, summary: str, find_one: bool = False) -> tuple[list | str | None, str | None]:
    """
    Busca issues pelo nome (summary) dentro de um projeto.

    Args:
        jira_client: O cliente JIRA inicializado.
        project_key: A chave do projeto.
        summary: O nome (título) da issue.
        find_one: Se True, espera encontrar exatamente uma issue e retorna seu ID. Se False, retorna uma lista.

    Returns:
        Uma tupla (resultado, error_message).
        - Se find_one=True: (issue.key, None) ou (None, "erro").
        - Se find_one=False: ([lista de issues], None) ou (None, "erro").
    """
    try:
        jql = f'project = "{project_key}" AND summary ~ "{summary}" ORDER BY created DESC'
        issues = jira_client.search_issues(jql, maxResults=20)

        if find_one:
            if len(issues) == 1:
                return issues[0].key, None
            elif len(issues) > 1:
                issue_list = ", ".join([f"'{i.key}'" for i in issues])
                return None, f"Ambiguidade: Múltiplas issues encontradas ({issue_list}). Use a chave exata."
            else:
                return None, f"Nenhuma issue encontrada com o nome '{summary}' no projeto '{project_key}'."

        return issues, None

    except Exception as e:
        return None, f"Erro ao buscar issues: {e}"

def log_work_for_issue(jira_client: JIRA, issue_key: str, time_spent: str, work_start_date: str, work_description: str) -> tuple[bool, str]:
    """
    Registra o tempo de trabalho em uma issue específica e retorna um status.

    Args:
        jira_client: O cliente JIRA inicializado.
        issue_key: A chave exata da issue (ex: 'PROJ-123').
        time_spent: O tempo gasto (ex: '2h 30m').
        work_start_date: A data do trabalho.
        work_description: Descrição do trabalho.

    Returns:
        Uma tupla (sucesso, mensagem).
    """
    try:
        work_datetime = dateparser.parse(work_start_date, languages=['pt'], settings={'PREFER_DATES_FROM': 'past', 'DATE_ORDER': 'DMY'})
        if not work_datetime:
            return False, f"Data '{work_start_date}' inválida."
        
        jira_client.add_worklog(
            issue=issue_key,
            timeSpent=time_spent,
            started=work_datetime,
            comment=work_description
        )
        return True, f"{time_spent} registrados em '{issue_key}'."
    except Exception as e:
        return False, f"Falha ao registrar em '{issue_key}': {e}"

def resolve_issue_identifier(jira_client: JIRA, project_key: str, issue_identifier: str) -> tuple[str | None, str | None]:
    """
    Resolve um identificador de issue, que pode ser uma chave (PROJ-123) ou um nome/título.
    
    Args:
        jira_client: O cliente JIRA inicializado.
        project_key: A chave do projeto onde buscar a issue.
        issue_identifier: O identificador da issue (chave ou nome).
    
    Returns:
        Uma tupla (issue_key, error_message).
        - (issue_key, None) se a issue for encontrada.
        - (None, "mensagem de erro") se houver erro.
    """
    # Se o identificador já é uma chave válida (formato PROJ-123), retorna diretamente
    if re.match(r'^[A-Z]+-\d+$', issue_identifier.upper()):
        return issue_identifier.upper(), None
    
    # Caso contrário, busca pelo nome/título
    issue_key_found, error = find_issue_by_summary(jira_client, project_key, issue_identifier, find_one=True)
    if error:
        return None, f"Erro ao encontrar a issue: {error}"
    
    return issue_key_found, None

def validate_project_access(jira_client: JIRA, project_identifier: str) -> tuple[str | None, str | None]:
    """
    Valida e resolve um identificador de projeto.
    
    Args:
        jira_client: O cliente JIRA inicializado.
        project_identifier: O identificador do projeto.
    
    Returns:
        Uma tupla (project_key, error_message).
        - (project_key, None) se o projeto for encontrado.
        - (None, "mensagem de erro") se houver erro.
    """
    project_key, error_message = find_project_by_identifier(jira_client, project_identifier)
    if error_message:
        return None, f"Erro ao encontrar o projeto: {error_message}"
    
    return project_key, None 