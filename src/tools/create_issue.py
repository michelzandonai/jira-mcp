from jira import JIRAError
from datetime import datetime
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import config
from src import utils

class CreateIssueInput(BaseModel):
    """Define os argumentos para a ferramenta de criação de issue."""
    project_name_or_key: str = Field(description="A chave ou nome do projeto Jira onde a issue será criada (ex: 'PROJ', 'Meu Projeto').")
    summary: str = Field(description="O título ou resumo principal da issue.")
    description: str = Field(description="A descrição detalhada da issue, que pode incluir formatação de texto.")
    issuetype: str = Field(default="Task", description="O tipo da issue (ex: 'Task', 'Bug', 'Story'). O padrão é 'Task'.")
    original_estimate: str = Field(default="", description="Estimativa de tempo original para a issue (ex: '2w', '1d', '4h').")
    remaining_estimate: str = Field(default="", description="Estimativa de tempo restante para a issue (ex: '1d', '4h').")
    time_spent: str = Field(default="", description="Tempo já gasto na issue, para ser registrado imediatamente (ex: '2h', '30m').")
    work_start_date: str = Field(default="", description="Data de início do trabalho, obrigatória se 'time_spent' for informado. Formato: YYYY-MM-DD.")

def create_issue_func(tool_input: CreateIssueInput) -> str:
    """
    Cria uma nova issue no Jira com base nos detalhes fornecidos.
    Use esta ferramenta para criar uma única tarefa, bug ou outra issue.

    Args:
        tool_input: Os dados necessários para criar a issue, validados pelo Pydantic.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_name_or_key)
        if error_message:
            return f"❌ {error_message}"

        issue_dict = {
            "project": {"key": project_key},
            "summary": tool_input.summary,
            "description": tool_input.description,
            "issuetype": {"name": tool_input.issuetype},
        }
        
        if config.JIRA_USERNAME:
            account_id, error_message = utils.get_user_account_id_by_email(jira_client, config.JIRA_USERNAME)
            if error_message:
                print(f"⚠️ Aviso: Não foi possível atribuir a issue. Motivo: {error_message}")
            elif account_id:
                issue_dict["assignee"] = {"accountId": account_id}

        if tool_input.original_estimate or tool_input.remaining_estimate:
            issue_dict["timetracking"] = {}
            if tool_input.original_estimate:
                issue_dict["timetracking"]["originalEstimate"] = tool_input.original_estimate
            if tool_input.remaining_estimate:
                issue_dict["timetracking"]["remainingEstimate"] = tool_input.remaining_estimate
        
        new_issue = jira_client.create_issue(fields=issue_dict)
        
        if tool_input.time_spent:
            if not tool_input.work_start_date or not utils.is_valid_date(tool_input.work_start_date):
                 return f"❌ Erro: 'work_start_date' é obrigatório e deve estar no formato YYYY-MM-DD ao informar 'time_spent'."
            
            work_datetime = datetime.strptime(tool_input.work_start_date, '%Y-%m-%d')
            jira_client.add_worklog(new_issue.key, timeSpent=tool_input.time_spent, started=work_datetime)
        
        return f"✅ Issue {new_issue.key} criada com sucesso! URL: {new_issue.permalink()}"

    except JIRAError as e:
        error_text = e.text if e.text else "Nenhuma mensagem de erro detalhada recebida."
        return f"❌ Erro do Jira ao criar issue: {e.status_code} - {error_text}"
    except Exception as e:
        return f"❌ Erro ao criar issue: {e}"

create_issue = FunctionTool(create_issue_func)
create_issue.name = "create_issue" 