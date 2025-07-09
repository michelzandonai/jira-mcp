from jira.exceptions import JIRAError
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from typing import List
from src import utils

class IssueToCreate(BaseModel):
    """Define a estrutura de uma única issue a ser criada em um lote."""
    project_name_or_key: str = Field(description="O nome ou chave do projeto onde a issue será criada.")
    summary: str = Field(description="O título ou resumo principal da issue.")
    description: str = Field(description="A descrição detalhada da issue.")
    issuetype: str = Field(default="Task", description="O tipo da issue (ex: 'Task', 'Bug'). Padrão: 'Task'.")
    original_estimate: str = Field(default="", description="Estimativa de tempo original (ex: '2w', '1d', '4h').")
    time_spent: str = Field(default="", description="Tempo já gasto, para ser registrado na criação (ex: '2h', '30m').")
    work_start_date: str = Field(default="", description="Data de início do trabalho se 'time_spent' for informado. Formato: YYYY-MM-DD.")

class BatchCreateIssuesInput(BaseModel):
    """Define a lista de issues para a ferramenta de criação em lote."""
    issues_to_create: List[IssueToCreate] = Field(description="Uma lista de issues a serem criadas, cada uma com seus próprios detalhes.")

def batch_create_issues_func(tool_input: BatchCreateIssuesInput) -> str:
    """
    Cria um lote de issues no Jira. Ideal para criar múltiplas tarefas de uma só vez.
    Pode opcionalmente registrar tempo de trabalho em cada issue no momento da criação.
    """
    try:
        jira_client = utils.get_jira_client()
        report = []

        if not tool_input.issues_to_create:
            return "Nenhum item para processar. Forneça uma lista de issues em 'issues_to_create'."

        for issue_data in tool_input.issues_to_create:
            # Valida o projeto
            project_key, error_message = utils.validate_project_access(jira_client, issue_data.project_name_or_key)
            if error_message:
                report.append(f"❌ Falha para '{issue_data.summary}': {error_message}")
                continue

            # Monta o dicionário para criação
            issue_dict = {
                "project": {"key": project_key},
                "summary": issue_data.summary,
                "description": issue_data.description,
                "issuetype": {"name": issue_data.issuetype},
            }
            
            if issue_data.original_estimate:
                issue_dict["timetracking"] = {"originalEstimate": issue_data.original_estimate}

            try:
                new_issue = jira_client.create_issue(fields=issue_dict)
                creation_message = f"Issue '{new_issue.key}' criada."

                if issue_data.time_spent and issue_data.work_start_date:
                    if not utils.is_valid_date(issue_data.work_start_date):
                        report.append(f"⚠️ Alerta: {creation_message} Mas falhou ao registrar tempo: 'work_start_date' deve estar no formato YYYY-MM-DD.")
                        continue

                    log_success, log_message = utils.log_work_for_issue(
                        jira_client=jira_client,
                        issue_key=new_issue.key,
                        time_spent=issue_data.time_spent,
                        work_start_date=issue_data.work_start_date,
                        work_description=issue_data.description
                    )
                    if log_success:
                        report.append(f"✅ Sucesso: {creation_message} {log_message}")
                    else:
                        report.append(f"⚠️ Alerta: {creation_message} Mas falhou ao registrar tempo: {log_message}")
                else:
                    report.append(f"✅ Sucesso: {creation_message}")

            except JIRAError as e:
                error_text = e.text if e.text else "Nenhuma mensagem de erro detalhada recebida."
                report.append(f"❌ Falha ao criar issue '{issue_data.summary}': {e.status_code} - {error_text}")
            except Exception as e:
                report.append(f"❌ Falha ao criar issue '{issue_data.summary}': {e}")
        
        return "\n".join(report)

    except Exception as e:
        return f"❌ Erro geral ao processar o lote de criação: {e}"

batch_create_issues = FunctionTool(batch_create_issues_func)
batch_create_issues.name = "batch_create_issues" 