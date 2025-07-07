from jira import JIRA
import re
import config
import utils

def update_issue_estimates(
    project_identifier: str,
    issue_identifier: str,
    original_estimate: str = "",
    remaining_estimate: str = ""
) -> str:
    """
    Atualiza as estimativas de tempo de uma issue, buscando o projeto e a issue de forma inteligente.
    """
    try:
        if not original_estimate and not remaining_estimate:
            return "⚠️ Nenhuma estimativa fornecida."

        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        # Busca inteligente do projeto
        project_key, error_message = utils.find_project_by_identifier(jira_client, project_identifier)
        if error_message:
            return f"❌ Erro ao encontrar o projeto: {error_message}"

        issue_key_to_update = issue_identifier
        # Se o identificador da issue não for uma chave, busca pelo nome
        if not re.match(r'^[A-Z]+-\d+$', issue_identifier.upper()):
            issue_key_found, error = utils.find_issue_by_summary(jira_client, project_key, issue_identifier, find_one=True)
            if error:
                return f"❌ Erro ao encontrar a issue: {error}"
            issue_key_to_update = issue_key_found

        timetracking_dict = {}
        if original_estimate: timetracking_dict["originalEstimate"] = original_estimate
        if remaining_estimate: timetracking_dict["remainingEstimate"] = remaining_estimate

        issue = jira_client.issue(issue_key_to_update)
        issue.update(fields={"timetracking": timetracking_dict})
        
        results = []
        if original_estimate: results.append(f"✅ Estimativa Original da issue {issue_key_to_update} atualizada.")
        if remaining_estimate: results.append(f"✅ Estimativa Restante da issue {issue_key_to_update} atualizada.")
        
        return "\n".join(results)

    except Exception as e:
        return f"❌ Erro ao atualizar estimativas: {e}" 