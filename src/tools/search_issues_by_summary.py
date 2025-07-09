from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class SearchIssuesInput(BaseModel):
    """Define os argumentos para a ferramenta de busca de issues."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde a busca será realizada (ex: 'Meu Projeto', 'PROJ').")
    summary: str = Field(description="O título ou parte do título da issue a ser buscada.")

def search_issues_by_summary_func(tool_input: SearchIssuesInput) -> str:
    """
    Busca por issues (tarefas) em um projeto específico do Jira pelo seu título (summary).
    Use esta ferramenta para encontrar tarefas existentes quando você sabe parte do título delas.
    """
    try:
        jira_client = utils.get_jira_client()

        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ {error_message}"

        issues, error = utils.find_issue_by_summary(jira_client, project_key, tool_input.summary)
        if error:
            return f"❌ Erro ao buscar issues: {error}"
        
        if not issues:
            return f"Nenhuma issue encontrada no projeto '{project_key}' com o título contendo '{tool_input.summary}'."

        result = [f"Issues encontradas em '{tool_input.project_identifier}' (Projeto: {project_key}) com o termo '{tool_input.summary}':", ""]
        for issue in issues:
            result.append(f"• [{issue.key}] {issue.fields.summary}")

        return "\n".join(result)

    except Exception as e:
        return f"❌ Erro ao buscar issues no Jira: {e}"

search_issues_by_summary = FunctionTool(search_issues_by_summary_func)
search_issues_by_summary.name = "search_issues_by_summary" 