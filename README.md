# Jira MCP Agent

Um agente de protocolo de máquina (`MCP - Machine-to-Machine Communication Protocol`) para interagir com o Jira. Este agente permite explorar projetos, criar issues e gerenciar o tempo gasto em tarefas diretamente através de uma interface de conversação.

## Funcionalidades

- **Explorador de Projetos**: Liste e visualize detalhes dos projetos no Jira.
- **Criador de Issues**: Crie novas issues (tarefas, bugs, etc.) em qualquer projeto.
- **Gestão de Tempo**: Adicione registros de tempo (worklogs) às issues existentes.

## Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

1. **Clone o repositório:**
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
   cd jira-mcp-server
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *No Windows, use `venv\\Scripts\\activate`.*

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

Antes de executar o agente, você precisa configurar suas credenciais e variáveis de ambiente.

1. Crie um arquivo chamado `.env` na raiz do projeto.

2. Adicione as seguintes variáveis ao arquivo `.env`:

   ```env
   # Credenciais do Jira
   JIRA_SERVER_URL="https://seu-dominio.atlassian.net"
   JIRA_USERNAME="seu-email@exemplo.com"
   JIRA_API_TOKEN="seu_api_token_do_jira"

   # Configuração do Google AI
   GOOGLE_API_KEY="sua_chave_de_api_do_google"
   GOOGLE_MODEL="gemini-1.5-flash"
   ```

   - `JIRA_SERVER_URL`: A URL da sua instância do Jira Cloud.
   - `JIRA_USERNAME`: O email da sua conta Jira.
   - `JIRA_API_TOKEN`: [Crie um token de API na sua conta Atlassian](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
   - `GOOGLE_API_KEY`: Sua chave de API do Google para usar os modelos de IA generativa.
   - `GOOGLE_MODEL`: O modelo do Google a ser utilizado (ex: `gemini-pro`, `gemini-1.5-flash`).

## Como Usar

Com o ambiente virtual ativado e o arquivo `.env` configurado, inicie o agente com o seguinte comando:

```bash
python src/agent.py
```

O agente será iniciado e estará pronto para receber comandos via MCP. 