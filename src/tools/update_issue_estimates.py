from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class UpdateEstimatesInput(BaseModel):
    """Define os argumentos para a ferramenta de atualização de estimativas."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde a issue está (ex: 'Meu Projeto', 'PROJ').")
    issue_identifier: str = Field(description="O identificador da issue (ex: 'PROJ-123', '123', ou parte do título)."
)
    original_estimate: str = Field(default="", description="A nova estimativa de tempo original para a issue (ex: '2w', '1d', '4h').")
    remaining_estimate: str = Field(default="", description="A nova estimativa de tempo restante para a issue (ex: '1d', '4h').")

def update_issue_estimates_func(tool_input: UpdateEstimatesInput) -> str:
    """
    Atualiza as estimativas de tempo (original e/ou restante) de uma issue existente.
    Use esta ferramenta para ajustar o planejamento de tempo de uma tarefa.
    """
    try:
        if not tool_input.original_estimate and not tool_input.remaining_estimate:
            return "⚠️ Nenhuma estimativa fornecida. Você deve informar 'original_estimate' ou 'remaining_estimate'."

        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ {error_message}"

        issue_key_to_update, error_message = utils.resolve_issue_identifier(jira_client, project_key, tool_input.issue_identifier)
        if error_message:
            return f"❌ {error_message}"

        timetracking_dict = {}
        if tool_input.original_estimate: timetracking_dict["originalEstimate"] = tool_input.original_estimate
        if tool_input.remaining_estimate: timetracking_dict["remainingEstimate"] = tool_input.remaining_estimate

        issue = jira_client.issue(issue_key_to_update)
        issue.update(fields={"timetracking": timetracking_dict})
        
        results = []
        if tool_input.original_estimate: results.append(f"✅ Estimativa Original da issue {issue_key_to_update} atualizada para {tool_input.original_estimate}.")
        if tool_input.remaining_estimate: results.append(f"✅ Estimativa Restante da issue {issue_key_to_update} atualizada para {tool_input.remaining_estimate}.")
        
        return "\n".join(results)

    except Exception as e:
        return f"❌ Erro ao atualizar estimativas: {e}"

update_issue_estimates = FunctionTool(update_issue_estimates_func)
update_issue_estimates.name = "update_issue_estimates" 