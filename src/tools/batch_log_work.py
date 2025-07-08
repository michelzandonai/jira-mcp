from jira import JIRA
from typing import List, Dict, Any

import config
import utils

def batch_log_work(project_identifier: str, work_logs: List[Dict[str, Any]]) -> str:
    """
    Registra o tempo de trabalho em um lote de issues de um único projeto.
    """
    try:
        jira_client = utils.get_jira_client()
        report = []

        # Validação centralizada do projeto
        project_key, error_message = utils.validate_project_access(jira_client, project_identifier)
        if error_message:
            return f"❌ Erro Crítico: {error_message}. Nenhum registro processado."

        # Itera sobre cada registro de trabalho
        for log in work_logs:
            issue_identifier = log.get('issue_identifier')
            time_spent = log.get('time_spent')
            work_start_date = log.get('work_start_date')
            work_description = log.get('work_description', "")

            if not all([issue_identifier, time_spent, work_start_date]):
                report.append(f"❌ Falha: Item inválido, faltam dados. Item: {log}")
                continue

            # Resolução centralizada do identificador da issue
            issue_key, error_message = utils.resolve_issue_identifier(jira_client, project_key, issue_identifier)
            if error_message:
                report.append(f"❌ Falha na task '{issue_identifier}': {error_message}")
                continue
            
            # Chama a função auxiliar para registrar o trabalho
            success, message = utils.log_work_for_issue(jira_client, issue_key, time_spent, work_start_date, work_description)
            
            if success:
                report.append(f"✅ Sucesso: {message}")
            else:
                report.append(f"❌ Falha: {message}")

        return "\n".join(report) if report else "Nenhum item para processar."

    except Exception as e:
        return f"❌ Erro geral ao processar o lote: {e}" 