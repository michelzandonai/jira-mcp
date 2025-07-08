from jira import JIRA, JIRAError
from datetime import datetime
import config
import utils

def create_issue(
    project_name_or_key: str, 
    summary: str, 
    description: str, 
    issuetype: str = "Task",
    original_estimate: str = "",
    remaining_estimate: str = "",
    time_spent: str = "",
    work_start_date: str = ""
) -> str:
    """
    Cria uma nova issue no Jira.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, project_name_or_key)
        if error_message:
            return f"❌ {error_message}"

        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
        }
        
        # Busca o accountId do usuário e o adiciona ao dicionário da issue.
        # Usa o JIRA_USERNAME (email) para a busca.
        if config.JIRA_USERNAME:
            account_id, error_message = utils.get_user_account_id_by_email(jira_client, config.JIRA_USERNAME)
            if error_message:
                # Adiciona um aviso em vez de bloquear a criação da issue
                print(f"⚠️ Aviso: Não foi possível atribuir a issue. Motivo: {error_message}")
            elif account_id:
                issue_dict["assignee"] = {"accountId": account_id}

        if original_estimate or remaining_estimate:
            issue_dict["timetracking"] = {
                "originalEstimate": original_estimate,
                "remainingEstimate": remaining_estimate,
            }
        
        new_issue = jira_client.create_issue(fields=issue_dict)
        
        if time_spent:
            if not work_start_date:
                return f"❌ Erro: 'work_start_date' é obrigatório ao informar 'time_spent'."
            
            work_datetime = datetime.strptime(work_start_date, '%Y-%m-%d')
            jira_client.add_worklog(new_issue.key, timeSpent=time_spent, started=work_datetime)
        
        return f"✅ Issue {new_issue.key} criada com sucesso! URL: {new_issue.permalink()}"

    except JIRAError as e:
        return f"❌ Erro do Jira ao criar issue: {e.status_code} - {e.text}"
    except Exception as e:
        return f"❌ Erro ao criar issue: {e}" 