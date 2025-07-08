from jira import JIRA
import config
import utils

def update_issue_status(
    project_identifier: str,
    issue_identifier: str,
    new_status: str
) -> str:
    """
    Atualiza o status de uma issue usando correspondência inteligente de status.
    
    Args:
        project_identifier: O identificador do projeto (chave ou nome).
        issue_identifier: O identificador da issue (chave ou nome).
        new_status: O novo status desejado (será mapeado inteligentemente).
    
    Returns:
        Mensagem de sucesso ou erro.
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
        
        # Resolve o status usando correspondência inteligente
        resolved_status, error_message = utils.find_closest_status(jira_client, project_key, new_status)
        if error_message:
            return f"❌ {error_message}"
        
        # Informa qual status foi encontrado se diferente do digitado
        if resolved_status.lower() != new_status.lower():
            print(f"📝 Status '{new_status}' mapeado para '{resolved_status}'")
        
        # Busca as transições disponíveis para a issue
        issue = jira_client.issue(issue_key)
        transitions = jira_client.transitions(issue)
        
        # Encontra a transição que leva ao status desejado
        target_transition = None
        for transition in transitions:
            if transition['to']['name'] == resolved_status:
                target_transition = transition
                break
        
        if not target_transition:
            # Lista as transições disponíveis
            available_transitions = [t['to']['name'] for t in transitions]
            transitions_text = ", ".join([f"'{t}'" for t in available_transitions])
            return f"❌ Não é possível transicionar a issue {issue_key} para o status '{resolved_status}'. Transições disponíveis: {transitions_text}"
        
        # Executa a transição
        jira_client.transition_issue(issue, target_transition['id'])
        
        return f"✅ Status da issue {issue_key} atualizado para '{resolved_status}' com sucesso!"
        
    except Exception as e:
        return f"❌ Erro ao atualizar status da issue: {e}" 