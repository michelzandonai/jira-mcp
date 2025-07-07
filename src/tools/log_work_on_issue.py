from jira import JIRA
import dateparser
import re
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
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        # Busca inteligente do projeto
        project_key, error_message = utils.find_project_by_identifier(jira_client, project_identifier)
        if error_message:
            return f"❌ Erro ao encontrar o projeto: {error_message}"

        issue_key_to_log = issue_identifier
        # Se o identificador da issue não for uma chave, busca pelo nome
        if not re.match(r'^[A-Z]+-\d+$', issue_identifier.upper()):
            issue_key_found, error = utils.find_issue_by_summary(jira_client, project_key, issue_identifier, find_one=True)
            if error:
                return f"❌ Erro ao encontrar a issue: {error}"
            issue_key_to_log = issue_key_found
        
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