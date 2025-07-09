from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from typing import List
from src import utils

class WorkLogItem(BaseModel):
    """Define a estrutura de um único registro de trabalho em um lote."""
    issue_identifier: str = Field(description="O identificador da issue (ex: 'PROJ-123', '123', ou parte do título).")
    time_spent: str = Field(description="O tempo a ser registrado (ex: '2h', '30m').")
    work_start_date: str = Field(description="A data em que o trabalho foi realizado. Formatos flexíveis são aceitos (ex: 'hoje', 'ontem', '25/12/2023').")
    work_description: str = Field(default="", description="Uma descrição ou comentário opcional sobre o trabalho realizado.")

class BatchLogWorkInput(BaseModel):
    """Define os argumentos para a ferramenta de registro de trabalho em lote."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde as issues estão. Todos os registros de trabalho devem ser para este projeto.")
    work_logs: List[WorkLogItem] = Field(description="Uma lista de registros de trabalho a serem adicionados.")

def batch_log_work_func(tool_input: BatchLogWorkInput) -> str:
    """
    Registra o tempo de trabalho em um lote de issues de um único projeto.
    Use esta ferramenta para registrar horas em várias tarefas de um mesmo projeto de uma só vez.
    """
    try:
        jira_client = utils.get_jira_client()
        report = []

        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ Erro Crítico: {error_message}. Nenhum registro processado."

        if not tool_input.work_logs:
            return "Nenhum item para processar. Forneça uma lista de registros em 'work_logs'."

        for log in tool_input.work_logs:
            issue_key, error_message = utils.resolve_issue_identifier(jira_client, project_key, log.issue_identifier)
            if error_message:
                report.append(f"❌ Falha na task '{log.issue_identifier}': {error_message}")
                continue
            
            success, message = utils.log_work_for_issue(
                jira_client=jira_client,
                issue_key=issue_key,
                time_spent=log.time_spent,
                work_start_date=log.work_start_date,
                work_description=log.work_description
            )
            
            if success:
                report.append(f"✅ Sucesso: {message}")
            else:
                report.append(f"❌ Falha: {message}")

        return "\n".join(report)

    except Exception as e:
        return f"❌ Erro geral ao processar o lote: {e}"

batch_log_work = FunctionTool(batch_log_work_func)
batch_log_work.name = "batch_log_work"
 