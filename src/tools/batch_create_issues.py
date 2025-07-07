from jira import JIRA
from typing import List, Dict, Any

import config
import utils

def batch_create_issues(issues_to_create: List[Dict[str, Any]]) -> str:
    """
    Cria um lote de issues no Jira, com a opção de registrar tempo de trabalho na criação.
    """
    try:
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        report = []

        for issue_data in issues_to_create:
            project_identifier = issue_data.get('project_identifier')
            summary = issue_data.get('summary')
            description = issue_data.get('description')
            
            if not all([project_identifier, summary, description]):
                report.append(f"❌ Falha: Item inválido, faltam dados obrigatórios (projeto, título, descrição). Item: {issue_data}")
                continue

            # Valida o projeto
            project_key, proj_error = utils.find_project_by_identifier(jira_client, project_identifier)
            if proj_error:
                report.append(f"❌ Falha para '{summary}': {proj_error}")
                continue

            # Monta o dicionário para criação
            issue_dict = {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_data.get("issuetype", "Task")},
            }
            if issue_data.get("original_estimate"):
                issue_dict["timetracking"] = {"originalEstimate": issue_data["original_estimate"]}

            try:
                # Passo 1: Criar a issue
                new_issue = jira_client.create_issue(fields=issue_dict)
                creation_message = f"Issue '{new_issue.key}' criada."

                # Passo 2 (Reutilização): Registrar tempo, se houver
                time_spent = issue_data.get('time_spent')
                work_start_date = issue_data.get('work_start_date')
                if time_spent and work_start_date:
                    log_success, log_message = utils.log_work_for_issue(
                        jira_client=jira_client,
                        issue_key=new_issue.key,
                        time_spent=time_spent,
                        work_start_date=work_start_date,
                        work_description=issue_data.get("work_description", "Trabalho inicial registrado na criação.")
                    )
                    if log_success:
                        report.append(f"✅ Sucesso: {creation_message} {log_message}")
                    else:
                        report.append(f"⚠️ Alerta: {creation_message} Mas falhou ao registrar tempo: {log_message}")
                else:
                    report.append(f"✅ Sucesso: {creation_message}")

            except Exception as e:
                report.append(f"❌ Falha ao criar issue '{summary}': {e}")
        
        return "\n".join(report) if report else "Nenhum item para processar."

    except Exception as e:
        return f"❌ Erro geral ao processar o lote de criação: {e}" 