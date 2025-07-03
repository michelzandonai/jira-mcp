import os
from dotenv import load_dotenv
from jira import JIRA
from google.adk.agents import Agent
from datetime import datetime, date
import re

# Importa as configurações já carregadas
import config

def _find_project_key_by_name_or_key(jira_client: JIRA, project_identifier: str) -> str | None:
    """
    Busca a chave de um projeto pelo nome (parcial ou completo) ou pela chave exata.

    Args:
        jira_client: O cliente JIRA inicializado.
        project_identifier: O nome (ex: 'Meu Projeto', 'Bolt') ou a chave exata (ex: 'MP').

    Returns:
        A chave do projeto encontrada ou uma mensagem de erro se for ambíguo ou não encontrado.
    """
    try:
        projects = jira_client.projects()
        normalized_identifier = project_identifier.lower()
        
        found_projects = []
        for project in projects:
            # Busca pela chave exata ou pelo nome parcial (contém)
            if project.key.lower() == normalized_identifier:
                return project.key # Retorna imediatamente se encontrar a chave exata
            if normalized_identifier in project.name.lower():
                found_projects.append(project)

        if len(found_projects) == 1:
            return found_projects[0].key
        elif len(found_projects) > 1:
            # Se mais de um projeto for encontrado, retorna uma mensagem de erro para desambiguação
            project_list = ", ".join([f"'{p.name}' ({p.key})" for p in found_projects])
            return f"Ambiguidade encontrada. O termo '{project_identifier}' corresponde a múltiplos projetos: {project_list}. Por favor, seja mais específico ou use a chave do projeto."
        
        return None # Nenhum projeto encontrado
    except Exception:
        return None

def create_issue(
    project_name_or_key: str, 
    summary: str, 
    description: str, 
    issuetype: str = "Task",
    original_estimate: str = "",
    remaining_estimate: str = "",
    time_spent: str = "",
    work_start_date: str = ""
) -> str:
    """
    Cria uma nova issue no Jira. Esta é a única ferramenta para criação de issues. 
    Ela suporta, opcionalmente, todos os campos de controle de tempo.

    Args:
        project_name_or_key: O nome ('Meu Projeto') ou a chave ('MP') do projeto.
        summary: O título (resumo) da issue.
        description: A descrição detalhada da issue.
        issuetype: O tipo da issue. Padrão 'Task'.
        original_estimate: (Opcional) Estimativa de tempo original (ex: '2w 4d 6h 45m').
        remaining_estimate: (Opcional) Tempo restante para concluir (ex: '1w 2d').
        time_spent: (Opcional) Tempo já gasto a ser registrado (ex: '1h 30m').
        work_start_date: (Opcional) Data de início do trabalho (YYYY-MM-DD). Obrigatório se 'time_spent' for informado.

    Returns:
        Confirmação da criação da issue com detalhes de tempo, se houver.
    """
    try:
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        project_key_or_error = _find_project_key_by_name_or_key(jira_client, project_name_or_key)
        if not project_key_or_error or "Ambiguidade encontrada" in project_key_or_error:
            error_message = project_key_or_error or f"Projeto '{project_name_or_key}' não encontrado."
            return f"❌ Erro: {error_message} Verifique o nome ou a chave."
        project_key = project_key_or_error

        if time_spent and not work_start_date:
            return "❌ Erro: 'Data de Início' (work_start_date) é obrigatória ao informar 'Tempo Gasto' (time_spent)."
        if work_start_date and time_spent:
            try:
                datetime.strptime(work_start_date, '%Y-%m-%d')
            except ValueError:
                return "❌ Erro: Formato de data inválido para 'work_start_date'. Use YYYY-MM-DD."

        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
        }
        
        timetracking_dict = {}
        if original_estimate: timetracking_dict["originalEstimate"] = original_estimate
        if remaining_estimate: timetracking_dict["remainingEstimate"] = remaining_estimate
        if timetracking_dict: issue_dict["timetracking"] = timetracking_dict
        
        new_issue = jira_client.create_issue(fields=issue_dict)
        
        if time_spent and work_start_date:
            work_datetime = datetime.strptime(work_start_date, '%Y-%m-%d')
            work_started_iso = work_datetime.strftime('%Y-%m-%dT08:00:00.000+0000')
            jira_client.add_worklog(new_issue.key, timeSpent=time_spent, started=work_started_iso)
        
        # Monta a resposta final
        result = [
            f"✅ Issue {new_issue.key} criada com sucesso!",
            f"URL: {new_issue.permalink()}"
        ]

        # Busca os detalhes de tempo para confirmação
        updated_issue = jira_client.issue(new_issue.key, fields="timetracking")
        if hasattr(updated_issue, 'fields') and hasattr(updated_issue.fields, 'timetracking'):
            tracking_info = updated_issue.fields.timetracking
            if hasattr(tracking_info, 'originalEstimate'): result.append(f"📊 Estimativa Original: {tracking_info.originalEstimate}")
            if hasattr(tracking_info, 'timeSpent'): result.append(f"⏱️ Tempo Registrado: {tracking_info.timeSpent}")
            if hasattr(tracking_info, 'remainingEstimate'): result.append(f"⏰ Tempo Restante: {tracking_info.remainingEstimate}")

        return "\n".join(result)

    except Exception as e:
        return f"❌ Erro ao criar issue: {e}"

def get_issue_types(project_name_or_key: str) -> str:
    """
    Busca os tipos de issues (ex: 'Bug', 'Task') disponíveis em um projeto.
    Args:
        project_name_or_key: O nome ('Meu Projeto') ou a chave ('MP') do projeto.
    Returns:
        Lista dos tipos de issues disponíveis no projeto.
    """
    try:
        jira_client = JIRA(
            server=config.JIRA_SERVER, 
            basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN)
        )
        
        project_key_or_error = _find_project_key_by_name_or_key(jira_client, project_name_or_key)
        if not project_key_or_error or "Ambiguidade encontrada" in project_key_or_error:
            error_message = project_key_or_error or f"Projeto '{project_name_or_key}' não encontrado."
            return f"❌ Erro: {error_message} Verifique o nome ou a chave."
        
        project_key = project_key_or_error
        
        # Busca os tipos de issues disponíveis no projeto
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

def update_estimates(
    project_name_or_key: str,
    original_estimate: str,
    remaining_estimate: str
) -> str:
    """
    Atualiza as estimativas de um projeto no Jira.

    Args:
        project_name_or_key: O nome ('Meu Projeto') ou a chave ('MP') do projeto.
        original_estimate: A nova estimativa de tempo original (ex: '2w 4d 6h 45m').
        remaining_estimate: A nova estimativa de tempo restante (ex: '1w 2d').

    Returns:
        Confirmação da atualização das estimativas.
    """
    try:
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        
        project_key_or_error = _find_project_key_by_name_or_key(jira_client, project_name_or_key)
        if not project_key_or_error or "Ambiguidade encontrada" in project_key_or_error:
            error_message = project_key_or_error or f"Projeto '{project_name_or_key}' não encontrado."
            return f"❌ Erro: {error_message} Verifique o nome ou a chave."
        project_key = project_key_or_error

        issue_dict = {
            "project": {"key": project_key},
            "timetracking": {
                "originalEstimate": original_estimate,
                "remainingEstimate": remaining_estimate
            }
        }
        
        jira_client.update_issue(fields=issue_dict)
        
        return "✅ Estimativas atualizadas com sucesso!"

    except Exception as e:
        return f"❌ Erro ao atualizar estimativas: {e}" 