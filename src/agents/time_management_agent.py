import os
from dotenv import load_dotenv
from jira import JIRA
from google.adk.agents import Agent
from datetime import datetime
import dateparser

# Carrega as configurações diretamente
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Configurações
JIRA_SERVER = os.getenv("JIRA_SERVER_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

def log_work_on_issue(
    issue_key: str,
    time_spent: str,
    work_start_date: str,
    work_description: str = ""
) -> str:
    """
    Registra o tempo trabalhado (log de trabalho) em uma issue existente. Use esta ferramenta quando o usuário falar em 'registrar horas' ou 'tempo gasto'.

    Args:
        issue_key: A chave da issue (ex: 'PROJ-123').
        time_spent: O tempo gasto a ser registrado (ex: '2h 30m').
        work_start_date: A data em que o trabalho foi realizado (pode ser em linguagem natural, como 'ontem' ou '1 de julho').
        work_description: (Opcional) Descrição do trabalho realizado.

    Returns:
        Confirmação do registro de tempo.
    """
    try:
        jira_client = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        
        # Tenta analisar a data em linguagem natural (ex: "hoje", "2 days ago", "15/03/2024")
        # A biblioteca dateparser lida com a conversão para um objeto datetime.
        # Língua portuguesa é priorizada para formatos como 'DD/MM/YYYY'.
        work_datetime = dateparser.parse(work_start_date, languages=['pt'], settings={'PREFER_DATES_FROM': 'past', 'DATE_ORDER': 'DMY'})

        if not work_datetime:
            return f"❌ Erro: Não foi possível entender a data '{work_start_date}'. Por favor, use um formato claro como 'hoje', 'ontem', 'DD/MM/YYYY' ou 'YYYY-MM-DD'."

        jira_client.add_worklog(
            issue=issue_key,
            timeSpent=time_spent,
            started=work_datetime,
            comment=work_description
        )
        
        # Formata a data de volta para um padrão consistente para a mensagem de confirmação
        confirmation_date = work_datetime.strftime('%Y-%m-%d')
        return f"✅ Tempo registrado com sucesso na issue {issue_key}: {time_spent} em {confirmation_date}."

    except Exception as e:
        # Adiciona mais detalhes ao erro para depuração
        return f"❌ Erro ao registrar trabalho (log work): {e}. Verifique se a issue '{issue_key}' existe e se o formato de tempo '{time_spent}' é válido (ex: '1h 30m')."

def update_issue_estimates(
    issue_key: str,
    original_estimate: str = "",
    remaining_estimate: str = ""
) -> str:
    """
    Atualiza as estimativas de tempo de uma issue. Use para alterar a 'estimativa original' (tempo total previsto) ou o 'tempo restante'.

    Args:
        issue_key: A chave da issue a ser ajustada (ex: 'PROJ-123').
        original_estimate: (Opcional) Novo valor para a 'Estimativa Original'.
        remaining_estimate: (Opcional) Novo valor para o 'Tempo Restante'.

    Returns:
        Confirmação das alterações de estimativa.
    """
    try:
        if not original_estimate and not remaining_estimate:
            return "⚠️ Nenhuma estimativa fornecida. Forneça 'original_estimate' ou 'remaining_estimate'."

        jira_client = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        
        timetracking_dict = {}
        if original_estimate:
            timetracking_dict["originalEstimate"] = original_estimate
        if remaining_estimate:
            timetracking_dict["remainingEstimate"] = remaining_estimate

        issue = jira_client.issue(issue_key)
        issue.update(fields={"timetracking": timetracking_dict})
        
        results = []
        if original_estimate:
            results.append(f"✅ Estimativa Original da issue {issue_key} atualizada para {original_estimate}.")
        if remaining_estimate:
            results.append(f"✅ Estimativa Restante da issue {issue_key} atualizada para {remaining_estimate}.")
        
        return "\n".join(results)

    except Exception as e:
        return f"❌ Erro ao atualizar estimativas: {e}" 