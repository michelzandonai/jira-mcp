from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class GetProjectDetailsInput(BaseModel):
    """Define os argumentos para a ferramenta de busca de detalhes de projeto."""
    project_name_or_key: str = Field(description="A chave ('PROJ') ou o nome ('Meu Projeto') do projeto a ser detalhado.")

def get_project_details_func(tool_input: GetProjectDetailsInput) -> str:
    """
    Obtém detalhes específicos de um projeto do Jira, como descrição, líder e componentes.
    Use esta ferramenta quando precisar de informações aprofundadas sobre um projeto específico.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_name_or_key)
        
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
        return f"Erro ao buscar detalhes do projeto '{tool_input.project_name_or_key}': {e}"

get_project_details = FunctionTool(get_project_details_func)
get_project_details.name = "get_project_details" 