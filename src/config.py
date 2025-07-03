import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env que deve estar na raiz do projeto 'jira_mcp_server'
# O path é relativo a onde o script é executado, então buscamos a partir do diretório do arquivo.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

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