from jira import JIRA
import config
import utils

def get_project_details(project_name_or_key: str) -> str:
    """
    Obtém detalhes específicos de um projeto do Jira, buscando pelo nome ou chave.

    Args:
        project_name_or_key: A chave ('PROJ') ou o nome ('Meu Projeto') do projeto.

    Returns:
        Detalhes formatados do projeto incluindo descrição, lead, e componentes.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, project_name_or_key)
        
        if error_message:
            return f"❌ {error_message}"
        
        project = jira_client.project(project_key)
        
        result = [
            f"Detalhes do Projeto: {project.key}",
            "=" * 50,
            f"Nome: {project.name}",
            f"Chave: {project.key}",
            f"Tipo: {getattr(project, 'projectTypeKey', 'N/A')}",
        ]
        
        if hasattr(project, 'description') and project.description:
            result.append(f"Descrição: {project.description}")
        
        if hasattr(project, 'lead') and project.lead:
            result.append(f"Líder do Projeto: {project.lead.displayName}")
        
        components = jira_client.project_components(project_key)
        if components:
            result.append("\nComponentes disponíveis:")
            for component in components:
                result.append(f"• {component.name}")
        
        return "\n".join(result)

    except Exception as e:
        return f"Erro ao buscar detalhes do projeto '{project_name_or_key}': {e}" 