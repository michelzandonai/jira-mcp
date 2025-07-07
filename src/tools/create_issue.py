from jira import JIRA
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
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        project_key, error_message = utils.find_project_by_identifier(jira_client, project_name_or_key)
        if error_message:
            return f"❌ Erro: {error_message}"

        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
        }
        
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

    except Exception as e:
        return f"❌ Erro ao criar issue: {e}" 