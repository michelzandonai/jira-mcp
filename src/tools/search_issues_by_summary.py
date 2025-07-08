from jira import JIRA
import config
import utils

def search_issues_by_summary(project_identifier: str, summary: str) -> str:
    """
    Busca por issues (tarefas) em um projeto específico do Jira pelo seu título (summary),
    encontrando o projeto de forma inteligente.

    Args:
        project_identifier: O identificador do projeto ou parte dele (ex: 'PROJ' ou 'Project').
        summary: O título ou parte do título da issue a ser buscada.

    Returns:
        Uma lista formatada de issues encontradas com suas chaves e títulos, ou uma mensagem se nada for encontrado.
    """
    try:
        jira_client = utils.get_jira_client()

        # Validação centralizada do projeto
        project_key, error_message = utils.validate_project_access(jira_client, project_identifier)
        if error_message:
            return f"❌ {error_message}"

        issues, error = utils.find_issue_by_summary(jira_client, project_key, summary)
        if error:
            return f"❌ Erro ao buscar issues: {error}"
        
        if not issues:
            return f"Nenhuma issue encontrada no projeto '{project_key}' com o título contendo '{summary}'."

        result = [f"Issues encontradas em '{project_identifier}' (Projeto: {project_key}) com o termo '{summary}':", ""]
        for issue in issues:
            result.append(f"• [{issue.key}] {issue.fields.summary}")

        return "\n".join(result)

    except Exception as e:
        return f"❌ Erro ao buscar issues no Jira: {e}" 