from jira import JIRA
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

        jira_client = utils.get_jira_client()
        
        # Validação centralizada do projeto
        project_key, error_message = utils.validate_project_access(jira_client, project_identifier)
        if error_message:
            return f"❌ {error_message}"

        # Resolução centralizada do identificador da issue
        issue_key_to_update, error_message = utils.resolve_issue_identifier(jira_client, project_key, issue_identifier)
        if error_message:
            return f"❌ {error_message}"

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