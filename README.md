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
   GOOGLE_MODEL="gemini-2.5-flash"
   ```

   - `JIRA_SERVER_URL`: A URL da sua instância do Jira Cloud.
   - `JIRA_USERNAME`: O email da sua conta Jira.
   - `JIRA_API_TOKEN`: Seu token de API pessoal para autenticação. Veja como obtê-lo abaixo.
   - `GOOGLE_API_KEY`: Sua chave de API do Google para usar os modelos de IA generativa. Veja como obtê-la abaixo.
   - `GOOGLE_MODEL`: O modelo do Google a ser utilizado (ex: `gemini-pro`, `gemini-2.5-flash`).

### Obtendo as Chaves de API

#### 1. Jira API Token
Para criar seu token de API do Jira:

1.  Acesse sua conta Atlassian e navegue para a seção de segurança ou clique diretamente em: [Criar um token de API](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
2.  Clique em **Criar token de API**.
3.  Dê um nome (label) para o token, por exemplo, `jira-mcp-agent`.
4.  Copie o token gerado. **Guarde-o em um local seguro, pois você não poderá visualizá-lo novamente.**
5.  Cole o token no seu arquivo `.env`.

#### 2. Google API Key (para Gemini)
Para obter sua chave de API do Google AI:

1.  Acesse o **[Google AI Studio](https://aistudio.google.com/)**.
2.  Faça login com sua Conta Google.
3.  No menu à esquerda, clique em **"Obter chave de API"** (Get API key).
4.  Clique em **"Criar chave de API em um novo projeto"** (Create API key in new project).
5.  Copie a chave gerada e cole no seu arquivo `.env`.

## Como Usar

Com o ambiente virtual ativado e o arquivo `.env` configurado, inicie o agente com o seguinte comando:

```bash
python src/agent.py
```

O agente será iniciado e estará pronto para receber comandos via MCP. 