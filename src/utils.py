import os
from jira import JIRA
import dateparser

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