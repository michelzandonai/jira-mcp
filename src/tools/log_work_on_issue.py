from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
import dateparser
from src import utils

class LogWorkInput(BaseModel):
    """Define os argumentos para a ferramenta de registro de trabalho."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde a issue está (ex: 'Meu Projeto', 'PROJ').")
    issue_identifier: str = Field(description="O identificador da issue (ex: 'PROJ-123', '123', ou parte do título).")
    time_spent: str = Field(description="O tempo a ser registrado (ex: '2h', '30m').")
    work_start_date: str = Field(description="A data em que o trabalho foi realizado. Formatos flexíveis são aceitos (ex: 'hoje', 'ontem', '25/12/2023').")
    work_description: str = Field(default="", description="Uma descrição ou comentário opcional sobre o trabalho realizado.")

def log_work_on_issue_func(tool_input: LogWorkInput) -> str:
    """
    Registra o tempo trabalhado em uma issue existente, buscando o projeto e a issue de forma inteligente.
    Use esta ferramenta para adicionar um registro de trabalho (worklog) a uma tarefa específica.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ {error_message}"

        issue_key_to_log, error_message = utils.resolve_issue_identifier(jira_client, project_key, tool_input.issue_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        work_datetime = dateparser.parse(tool_input.work_start_date, languages=['pt'], settings={'PREFER_DATES_FROM': 'past', 'DATE_ORDER': 'DMY'})
        if not work_datetime:
            return f"❌ Erro: Não foi possível entender a data '{tool_input.work_start_date}'."

        jira_client.add_worklog(
            issue=issue_key_to_log,
            timeSpent=tool_input.time_spent,
            started=work_datetime,
            comment=tool_input.work_description
        )
        
        confirmation_date = work_datetime.strftime('%Y-%m-%d')
        return f"✅ Tempo registrado com sucesso na issue {issue_key_to_log}: {tool_input.time_spent} em {confirmation_date}."

    except Exception as e:
        return f"❌ Erro ao registrar trabalho: {e}."

log_work_on_issue = FunctionTool(log_work_on_issue_func)
log_work_on_issue.name = "log_work_on_issue" 