from jira import JIRA
from datetime import datetime
import config
import utils

def get_issue_details(project_identifier: str, issue_identifier: str) -> str:
    """
    Busca detalhes completos de uma issue específica no Jira.
    
    Args:
        project_identifier: O identificador do projeto (chave ou nome).
        issue_identifier: O identificador da issue (chave como 'AM-23' ou nome/título).
    
    Returns:
        Detalhes formatados da issue com todas as informações disponíveis.
    """
    try:
        jira_client = utils.get_jira_client()
        
        # Validação centralizada do projeto
        project_key, error_message = utils.validate_project_access(jira_client, project_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        # Resolução centralizada do identificador da issue
        issue_key, error_message = utils.resolve_issue_identifier(jira_client, project_key, issue_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        # Busca a issue com todos os campos
        issue = jira_client.issue(issue_key, expand='changelog')
        
        # Formata os detalhes
        result_lines = []
        
        # Cabeçalho
        result_lines.append(f"📋 Detalhes da Issue: {issue.key}")
        result_lines.append("=" * 60)
        
        # Informações básicas
        result_lines.append(f"🏷️  Título: {issue.fields.summary}")
        result_lines.append(f"📝 Tipo: {issue.fields.issuetype.name}")
        result_lines.append(f"🔄 Status: {issue.fields.status.name}")
        result_lines.append(f"⚡ Prioridade: {issue.fields.priority.name if issue.fields.priority else 'Não definida'}")
        result_lines.append("")
        
        # Pessoas
        result_lines.append("👥 Pessoas:")
        result_lines.append(f"   • Responsável: {issue.fields.assignee.displayName if issue.fields.assignee else 'Não atribuído'}")
        result_lines.append(f"   • Criador: {issue.fields.creator.displayName if issue.fields.creator else 'Não informado'}")
        result_lines.append(f"   • Reporter: {issue.fields.reporter.displayName if issue.fields.reporter else 'Não informado'}")
        result_lines.append("")
        
        # Datas
        result_lines.append("📅 Datas:")
        created = datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
        result_lines.append(f"   • Criada: {created.strftime('%d/%m/%Y às %H:%M')}")
        
        updated = datetime.strptime(issue.fields.updated[:19], '%Y-%m-%dT%H:%M:%S')
        result_lines.append(f"   • Atualizada: {updated.strftime('%d/%m/%Y às %H:%M')}")
        
        if issue.fields.duedate:
            result_lines.append(f"   • Vencimento: {issue.fields.duedate}")
        
        if issue.fields.resolutiondate:
            resolved = datetime.strptime(issue.fields.resolutiondate[:19], '%Y-%m-%dT%H:%M:%S')
            result_lines.append(f"   • Resolvida: {resolved.strftime('%d/%m/%Y às %H:%M')}")
        
        result_lines.append("")
        
        # Estimativas de tempo
        if hasattr(issue.fields, 'timetracking') and issue.fields.timetracking:
            result_lines.append("⏱️  Tempo:")
            timetracking = issue.fields.timetracking
            if hasattr(timetracking, 'originalEstimate') and timetracking.originalEstimate:
                result_lines.append(f"   • Estimativa Original: {timetracking.originalEstimate}")
            if hasattr(timetracking, 'remainingEstimate') and timetracking.remainingEstimate:
                result_lines.append(f"   • Estimativa Restante: {timetracking.remainingEstimate}")
            if hasattr(timetracking, 'timeSpent') and timetracking.timeSpent:
                result_lines.append(f"   • Tempo Gasto: {timetracking.timeSpent}")
            result_lines.append("")
        
        # Descrição
        if issue.fields.description:
            result_lines.append("📄 Descrição:")
            # Limita a descrição a 500 caracteres para não ficar muito longa
            description = issue.fields.description
            if len(description) > 500:
                description = description[:500] + "..."
            result_lines.append(f"   {description}")
            result_lines.append("")
        
        # Componentes
        if issue.fields.components:
            result_lines.append("🔧 Componentes:")
            for component in issue.fields.components:
                result_lines.append(f"   • {component.name}")
            result_lines.append("")
        
        # Labels
        if issue.fields.labels:
            result_lines.append("🏷️  Labels:")
            result_lines.append(f"   {', '.join(issue.fields.labels)}")
            result_lines.append("")
        
        # Subtarefas
        if issue.fields.subtasks:
            result_lines.append("📋 Subtarefas:")
            for subtask in issue.fields.subtasks:
                result_lines.append(f"   • [{subtask.key}] {subtask.fields.summary} - {subtask.fields.status.name}")
            result_lines.append("")
        
        # Issue pai (se for uma subtarefa)
        if hasattr(issue.fields, 'parent') and issue.fields.parent:
            result_lines.append("📋 Issue Pai:")
            result_lines.append(f"   [{issue.fields.parent.key}] {issue.fields.parent.fields.summary}")
            result_lines.append("")
        
        # Worklog (últimos 5 registros)
        worklogs = jira_client.worklogs(issue_key)
        if worklogs:
            result_lines.append("⏰ Registros de Trabalho (últimos 5):")
            for worklog in worklogs[-5:]:  # Últimos 5
                started = datetime.strptime(worklog.started[:19], '%Y-%m-%dT%H:%M:%S')
                author = worklog.author.displayName if worklog.author else 'Usuário desconhecido'
                result_lines.append(f"   • {started.strftime('%d/%m/%Y')} - {worklog.timeSpent} por {author}")
                if hasattr(worklog, 'comment') and worklog.comment:
                    comment = worklog.comment[:100] + "..." if len(worklog.comment) > 100 else worklog.comment
                    result_lines.append(f"     Comentário: {comment}")
            result_lines.append("")
        
        # Link para a issue
        result_lines.append("🔗 Links:")
        result_lines.append(f"   • Jira: {issue.permalink()}")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"❌ Erro ao buscar detalhes da issue: {e}" 