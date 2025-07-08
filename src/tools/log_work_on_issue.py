from jira import JIRA
import dateparser
import config
import utils

def log_work_on_issue(
    project_identifier: str,
    issue_identifier: str,
    time_spent: str,
    work_start_date: str,
    work_description: str = ""
) -> str:
    """
    Registra o tempo trabalhado em uma issue existente, buscando o projeto e a issue de forma inteligente.
    """
    try:
        jira_client = utils.get_jira_client()
        
        # Validação centralizada do projeto
        project_key, error_message = utils.validate_project_access(jira_client, project_identifier)
        if error_message:
            return f"❌ {error_message}"

        # Resolução centralizada do identificador da issue
        issue_key_to_log, error_message = utils.resolve_issue_identifier(jira_client, project_key, issue_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        work_datetime = dateparser.parse(work_start_date, languages=['pt'], settings={'PREFER_DATES_FROM': 'past', 'DATE_ORDER': 'DMY'})
        if not work_datetime:
            return f"❌ Erro: Não foi possível entender a data '{work_start_date}'."

        jira_client.add_worklog(
            issue=issue_key_to_log,
            timeSpent=time_spent,
            started=work_datetime,
            comment=work_description
        )
        
        confirmation_date = work_datetime.strftime('%Y-%m-%d')
        return f"✅ Tempo registrado com sucesso na issue {issue_key_to_log}: {time_spent} em {confirmation_date}."

    except Exception as e:
        return f"❌ Erro ao registrar trabalho: {e}." 