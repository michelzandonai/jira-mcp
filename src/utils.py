import os
from jira import JIRA

def find_project_by_identifier(jira_client: JIRA, identifier: str) -> tuple[str | None, str | None]:
    """
    Busca um projeto de forma inteligente pelo identificador, procurando na chave, nome e descrição.

    Args:
        jira_client: O cliente JIRA inicializado.
        identifier: O termo de busca (chave, nome, parte do nome ou da descrição).

    Returns:
        Uma tupla (project_key, error_message).
        - (project.key, None) se exatamente um projeto for encontrado.
        - (None, "mensagem de erro") se nenhum ou múltiplos projetos forem encontrados.
    """
    try:
        all_projects = jira_client.projects()
        normalized_identifier = identifier.lower()
        
        found_projects = []
        
        # Itera sobre todos os projetos para encontrar correspondências
        for project in all_projects:
            # Verifica a chave, nome e descrição
            key_match = project.key.lower() == normalized_identifier
            name_match = normalized_identifier in project.name.lower()
            
            description_match = False
            if hasattr(project, 'description') and project.description:
                description_match = normalized_identifier in project.description.lower()
            
            if key_match or name_match or description_match:
                found_projects.append(project)

        # Remove duplicatas se um projeto foi encontrado por múltiplos critérios
        unique_projects = list({p.key: p for p in found_projects}.values())

        if len(unique_projects) == 1:
            return unique_projects[0].key, None
        elif len(unique_projects) > 1:
            project_list = ", ".join([f"'{p.name}' ({p.key})" for p in unique_projects])
            return None, f"Ambiguidade encontrada. O termo '{identifier}' corresponde a múltiplos projetos: {project_list}. Por favor, seja mais específico ou use a chave do projeto."
        else:
            return None, f"Nenhum projeto encontrado com o identificador '{identifier}'."
            
    except Exception as e:
        return None, f"Erro ao buscar projeto no Jira: {e}" 