from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src import utils

class UpdateStatusInput(BaseModel):
    """Define os argumentos para a ferramenta de atualização de status."""
    project_identifier: str = Field(description="O nome ou chave do projeto onde a issue está.")
    issue_identifier: str = Field(description="O identificador da issue (ex: 'PROJ-123', '123', ou parte do título).")
    new_status: str = Field(description="O novo status desejado para a issue (ex: 'Em Andamento', 'Concluído').")

def update_issue_status_func(tool_input: UpdateStatusInput) -> str:
    """
    Atualiza o status de uma issue (ex: de 'A Fazer' para 'Em Andamento').
    A ferramenta busca o status mais próximo do que foi solicitado e lista as opções se a transição não for direta.
    """
    try:
        jira_client = utils.get_jira_client()
        
        project_key, error_message = utils.validate_project_access(jira_client, tool_input.project_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        issue_key, error_message = utils.resolve_issue_identifier(jira_client, project_key, tool_input.issue_identifier)
        if error_message:
            return f"❌ {error_message}"
        
        resolved_status, error_message = utils.find_closest_status(jira_client, project_key, tool_input.new_status)
        if error_message:
            return f"❌ {error_message}"
        
        if resolved_status.lower() != tool_input.new_status.lower():
            print(f"📝 Status '{tool_input.new_status}' mapeado para '{resolved_status}'")
        
        issue = jira_client.issue(issue_key)
        transitions = jira_client.transitions(issue)
        
        target_transition = None
        for transition in transitions:
            if transition['to']['name'].lower() == resolved_status.lower():
                target_transition = transition
                break
        
        if not target_transition:
            available_transitions = [t['to']['name'] for t in transitions]
            transitions_text = ", ".join([f"'{t}'" for t in available_transitions])
            return f"❌ Não é possível transicionar a issue {issue_key} para o status '{resolved_status}'. Transições disponíveis: {transitions_text}"
        
        jira_client.transition_issue(issue, target_transition['id'])
        
        return f"✅ Status da issue {issue_key} atualizado para '{resolved_status}' com sucesso!"
        
    except Exception as e:
        return f"❌ Erro ao atualizar status da issue: {e}"

update_issue_status = FunctionTool(update_issue_status_func)
update_issue_status.name = "update_issue_status" 