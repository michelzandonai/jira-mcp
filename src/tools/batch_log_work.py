from jira import JIRA
import re
from typing import List, Dict, Any

import config
import utils

def batch_log_work(project_identifier: str, work_logs: List[Dict[str, Any]]) -> str:
    """
    Registra o tempo de trabalho em um lote de issues de um único projeto.
    """
    try:
        jira_client = JIRA(server=config.JIRA_SERVER, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
        report = []

        # Primeiro, valida o projeto uma única vez
        project_key, proj_error = utils.find_project_by_identifier(jira_client, project_identifier)
        if proj_error:
            return f"❌ Erro Crítico: Projeto '{project_identifier}' não pôde ser validado. Nenhum registro processado. Motivo: {proj_error}"

        # Itera sobre cada registro de trabalho
        for log in work_logs:
            issue_identifier = log.get('issue_identifier')
            time_spent = log.get('time_spent')
            work_start_date = log.get('work_start_date')
            work_description = log.get('work_description', "")

            if not all([issue_identifier, time_spent, work_start_date]):
                report.append(f"❌ Falha: Item inválido, faltam dados. Item: {log}")
                continue

            # Busca a issue
            issue_key, issue_error = utils.find_issue_by_summary(jira_client, project_key, issue_identifier, find_one=True)
            if not re.match(r'^[A-Z]+-\d+$', str(issue_identifier).upper()):
                if issue_error:
                    report.append(f"❌ Falha na task '{issue_identifier}': {issue_error}")
                    continue
            else:
                issue_key = issue_identifier
            
            # Chama a função auxiliar para registrar o trabalho
            success, message = utils.log_work_for_issue(jira_client, issue_key, time_spent, work_start_date, work_description)
            
            if success:
                report.append(f"✅ Sucesso: {message}")
            else:
                report.append(f"❌ Falha: {message}")

        return "\n".join(report) if report else "Nenhum item para processar."

    except Exception as e:
        return f"❌ Erro geral ao processar o lote: {e}" 