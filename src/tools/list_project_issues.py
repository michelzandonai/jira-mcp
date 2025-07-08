"""
Lista todas as issues de um projeto específico com filtros opcionais.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_jira_client, validate_project_access


def list_project_issues(project_identifier: str, status_filter: str = None, name_filter: str = None):
    """
    Lista todas as issues de um projeto com filtros opcionais.
    
    Args:
        project_identifier: Identificador do projeto (chave ou nome).
        status_filter: Filtro opcional por status exato (case insensitive).
        name_filter: Filtro opcional por nome/título (busca parcial).
    
    Returns:
        Lista de issues encontradas ou mensagem de erro.
    """
    try:
        jira = get_jira_client()
        
        # Valida e resolve o projeto
        project_key, error = validate_project_access(jira, project_identifier)
        if error:
            return {"error": error}
        
        # Constrói a query JQL
        jql_parts = [f'project = "{project_key}"']
        
        if status_filter:
            jql_parts.append(f'status = "{status_filter}"')
        
        if name_filter:
            jql_parts.append(f'summary ~ "{name_filter}"')
        
        jql = " AND ".join(jql_parts) + " ORDER BY created DESC"
        
        # Busca as issues
        issues = jira.search_issues(jql, maxResults=100, expand='changelog')
        
        if not issues:
            return {"message": f"Nenhuma issue encontrada no projeto '{project_key}' com os filtros aplicados."}
        
        # Formata os resultados
        results = []
        for issue in issues:
            issue_info = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "type": issue.fields.issuetype.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "Sem prioridade",
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Não atribuído",
                "created": issue.fields.created,
                "updated": issue.fields.updated
            }
            results.append(issue_info)
        
        return {
            "project_key": project_key,
            "total_issues": len(results),
            "filters_applied": {
                "status": status_filter,
                "name": name_filter
            },
            "issues": results
        }
        
    except Exception as e:
        return {"error": f"Erro ao listar issues: {e}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python list_project_issues.py <projeto> [status] [nome]")
        print("Exemplo: python list_project_issues.py 'PROJ' 'Done' 'bug'")
        sys.exit(1)
    
    project = sys.argv[1]
    status = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != 'None' else None
    name = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != 'None' else None
    
    result = list_project_issues(project, status, name)
    
    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
    elif "message" in result:
        print(f"ℹ️  {result['message']}")
    else:
        print(f"📋 Projeto: {result['project_key']}")
        print(f"📊 Total de issues: {result['total_issues']}")
        
        if result['filters_applied']['status']:
            print(f"🔍 Filtro de status: {result['filters_applied']['status']}")
        if result['filters_applied']['name']:
            print(f"🔍 Filtro de nome: {result['filters_applied']['name']}")
        
        print("\n" + "="*80)
        
        for issue in result['issues']:
            print(f"🎫 {issue['key']}: {issue['summary']}")
            print(f"   📊 Status: {issue['status']} | Tipo: {issue['type']} | Prioridade: {issue['priority']}")
            print(f"   👤 Responsável: {issue['assignee']}")
            print(f"   📅 Criado: {issue['created'][:10]} | Atualizado: {issue['updated'][:10]}")
            print("-" * 80) 