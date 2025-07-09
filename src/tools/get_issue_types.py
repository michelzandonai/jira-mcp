from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class GetIssueTypesInput(BaseModel):
    """Define os argumentos para a ferramenta de busca de tipos de issue."""
    project_name_or_key: str = Field(description="O nome ou chave do projeto para o qual os tipos de issue serão listados.")

def get_issue_types_func(tool_input: GetIssueTypesInput) -> str:
    """
    Busca os tipos de issues (ex: 'Bug', 'Task', 'Story') disponíveis em um projeto específico.
    Use esta ferramenta antes de criar uma issue para saber quais tipos são permitidos no projeto.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_name_or_key)
        if error_message:
            return f"❌ {error_message}"
        
        createmeta = jira_client.createmeta(projectKeys=project_key, expand="projects.issuetypes")
        
        if not createmeta['projects']:
            return f"Não foi possível obter tipos de issues para o projeto '{tool_input.project_name_or_key}'."
        
        project_data = createmeta['projects'][0]
        available_types = project_data['issuetypes']
        
        result = [f"Tipos de Issues disponíveis no projeto {tool_input.project_name_or_key} (Chave: {project_key}):", ""]
        for issue_type in available_types:
            result.append(f"• {issue_type['name']} - {issue_type.get('description', 'Sem descrição')}")
        
        return "\n".join(result)

    except Exception as e:
        return f"❌ Erro ao buscar tipos de issues: {e}"

get_issue_types = FunctionTool(get_issue_types_func)
get_issue_types.name = "get_issue_types" 