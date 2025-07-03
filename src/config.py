import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env.
# Como o `cwd` é definido no mcp.json para a raiz do projeto,
# a biblioteca encontrará o arquivo .env automaticamente.
load_dotenv()

# --- Configuração das Credenciais do Jira ---
JIRA_SERVER = os.getenv("JIRA_SERVER_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# --- Configuração do Google Gemini ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")  # Valor padrão se não especificado

# Verificação para garantir que todas as variáveis necessárias foram carregadas
if not all([JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN]):
    raise ValueError(
        "As variáveis de ambiente JIRA_SERVER_URL, JIRA_USERNAME, e JIRA_API_TOKEN "
        "devem ser definidas no arquivo .env na raiz do diretório 'jira_mcp_server'."
    )

if not GOOGLE_API_KEY:
    raise ValueError(
        "A variável de ambiente GOOGLE_API_KEY deve ser definida no arquivo .env "
        "para que o agente possa acessar o modelo Gemini."
    ) 