from jira import JIRA
import config
import utils

def get_issue_types(project_name_or_key: str) -> str:
    """
    Busca os tipos de issues (ex: 'Bug', 'Task') disponíveis em um projeto.
    """
    try:
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        project_key, error_message = utils.find_project_by_identifier(jira_client, project_name_or_key)
        if error_message:
            return f"❌ Erro: {error_message}"
        
        createmeta = jira_client.createmeta(projectKeys=project_key, expand="projects.issuetypes")
        
        if not createmeta['projects']:
            return f"Não foi possível obter tipos de issues para o projeto '{project_name_or_key}'."
        
        project_data = createmeta['projects'][0]
        available_types = project_data['issuetypes']
        
        result = [f"Tipos de Issues disponíveis no projeto {project_name_or_key} (Chave: {project_key}):", ""]
        for issue_type in available_types:
            result.append(f"• {issue_type['name']} - {issue_type.get('description', 'Sem descrição')}")
        
        return "\n".join(result)

    except Exception as e:
        return f"❌ Erro ao buscar tipos de issues: {e}" 