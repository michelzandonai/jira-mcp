from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from datetime import datetime
from src import utils

class GetIssueDetailsInput(BaseModel):
    """Define os argumentos para a ferramenta de busca de detalhes de issue."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde a issue está.")
    issue_identifier: str = Field(description="O identificador da issue (ex: 'PROJ-123', '123', ou parte do título).")

def get_issue_details_func(tool_input: GetIssueDetailsInput) -> str:
    """
    Busca e exibe detalhes completos de uma issue específica no Jira.
    Use esta ferramenta para obter um panorama completo de uma tarefa, incluindo status, responsável, tempo e comentários.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        issue_key, error_message = utils.resolve_issue_identifier(jira_client, project_key, tool_input.issue_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        issue = jira_client.issue(issue_key, expand='changelog')
        
        result_lines = []
        result_lines.append(f"📋 Detalhes da Issue: {issue.key}")
        result_lines.append("=" * 60)
        result_lines.append(f"🏷️  Título: {issue.fields.summary}")
        result_lines.append(f"📝 Tipo: {issue.fields.issuetype.name}")
        result_lines.append(f"🔄 Status: {issue.fields.status.name}")
        result_lines.append(f"⚡ Prioridade: {issue.fields.priority.name if issue.fields.priority else 'Não definida'}")
        result_lines.append("")
        
        result_lines.append("👥 Pessoas:")
        result_lines.append(f"   • Responsável: {issue.fields.assignee.displayName if issue.fields.assignee else 'Não atribuído'}")
        result_lines.append(f"   • Criador: {issue.fields.creator.displayName if issue.fields.creator else 'Não informado'}")
        result_lines.append("")
        
        result_lines.append("📅 Datas:")
        created = datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
        result_lines.append(f"   • Criada: {created.strftime('%d/%m/%Y às %H:%M')}")
        updated = datetime.strptime(issue.fields.updated[:19], '%Y-%m-%dT%H:%M:%S')
        result_lines.append(f"   • Atualizada: {updated.strftime('%d/%m/%Y às %H:%M')}")
        if issue.fields.resolutiondate:
            resolved = datetime.strptime(issue.fields.resolutiondate[:19], '%Y-%m-%dT%H:%M:%S')
            result_lines.append(f"   • Resolvida: {resolved.strftime('%d/%m/%Y às %H:%M')}")
        result_lines.append("")
        
        if hasattr(issue.fields, 'timetracking') and issue.fields.timetracking:
            result_lines.append("⏱️  Tempo:")
            timetracking = issue.fields.timetracking
            if hasattr(timetracking, 'originalEstimate'): result_lines.append(f"   • Estimativa Original: {timetracking.originalEstimate}")
            if hasattr(timetracking, 'remainingEstimate'): result_lines.append(f"   • Estimativa Restante: {timetracking.remainingEstimate}")
            if hasattr(timetracking, 'timeSpent'): result_lines.append(f"   • Tempo Gasto: {timetracking.timeSpent}")
            result_lines.append("")
        
        if issue.fields.description:
            result_lines.append("📄 Descrição:")
            description = issue.fields.description
            result_lines.append(f"   {description[:500] + '...' if len(description) > 500 else description}")
            result_lines.append("")
        
        worklogs = jira_client.worklogs(issue_key)
        if worklogs:
            result_lines.append("⏰ Registros de Trabalho (últimos 5):")
            for worklog in worklogs[-5:]:
                started = datetime.strptime(worklog.started[:19], '%Y-%m-%dT%H:%M:%S')
                author = worklog.author.displayName if worklog.author else 'Usuário desconhecido'
                result_lines.append(f"   • {started.strftime('%d/%m/%Y')} - {worklog.timeSpent} por {author}")
            result_lines.append("")
        
        result_lines.append(f"🔗 Link: {issue.permalink()}")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"❌ Erro ao buscar detalhes da issue: {e}"

get_issue_details = FunctionTool(get_issue_details_func)
get_issue_details.name = "get_issue_details" 