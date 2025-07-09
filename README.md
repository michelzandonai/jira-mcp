# Jira Agent (ADK)

Bem-vindo ao **Jira Agent**, um assistente inteligente construído com o **Google Agent Development Kit (ADK)** para interagir com a plataforma Jira.

Este agente permite que você gerencie projetos, crie tarefas e registre horas de trabalho diretamente através de uma interface de chat, utilizando o poder de um Modelo de Linguagem (LLM) para entender seus comandos em linguagem natural.

## ✨ Funcionalidades

-   **Busca de Projetos**: Liste todos os projetos ou encontre um específico por nome ou chave.
-   **Criação de Issues**: Crie tarefas, bugs ou outras issues individualmente ou em lote.
-   **Registro de Trabalho (Worklog)**: Registre horas em uma ou várias tarefas de forma rápida.
-   **Detalhes de Issues e Projetos**: Obtenha informações detalhadas sobre qualquer projeto ou tarefa.
-   **Atualização de Issues**: Modifique o status e as estimativas de tempo das suas tarefas.
-   **Interação Inteligente**: O agente é projetado para entender o contexto e priorizar ações em lote sempre que possível.

---

## 🚀 Começando

Siga os passos abaixo para configurar e executar o agente em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.9 ou superior
-   Acesso a uma conta Jira com permissões de API

### 2. Instalação

**a. Clone o Repositório:**
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd jira-agent
```

**b. Crie e Ative um Ambiente Virtual (Recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate
# No Windows, use: venv\Scripts\activate
```

**c. Instale as Dependências:**
```bash
pip install -r requirements.txt
```

### 3. Configuração

O agente precisa de credenciais para se conectar à sua conta Jira. A forma mais segura de fornecê-las é através de variáveis de ambiente.

**a. Crie um arquivo `.env`** na raiz do projeto. Este arquivo não deve ser enviado para o controle de versão.

**b. Adicione as seguintes variáveis ao arquivo `.env`:**

```dotenv
# URL da sua instância Jira (ex: https://meudominio.atlassian.net)
JIRA_SERVER="SUA_URL_JIRA"

# Email da sua conta Jira
JIRA_USERNAME="seu-email@exemplo.com"

# Token de API gerado no Jira
# Veja como gerar: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
JIRA_API_TOKEN="SEU_TOKEN_DE_API"
```

### 4. Executando o Agente

Este projeto é servido como uma aplicação FastAPI e inclui a **Dev-UI** do Google ADK para testes e interação.

**a. Instale as dependências (se ainda não o fez):**
```bash
pip install -r requirements.txt
```

**b. Inicie o servidor com Uvicorn:**
```bash
uvicorn main:app --reload
```

O comando acima iniciará um servidor web local. A opção `--reload` faz com que o servidor reinicie automaticamente após qualquer alteração no código.

**c. Acesse a Documentação da API:**
Abra seu navegador e acesse o seguinte endereço para ver a documentação interativa da API (gerada pelo Swagger UI):
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

A partir desta página, você pode testar o endpoint `/converse` diretamente.

---

## 🛠️ Como Usar

Após iniciar a Dev-UI, você pode enviar mensagens ao agente na interface de chat.

**Exemplos de Comandos:**

-   `Liste todos os projetos que contenham a palavra 'Mobile'`
-   `Crie uma tarefa no projeto 'Mobile App' com o título 'Corrigir bug no login' e descrição 'O botão de login não funciona no iOS 17'`
-   `Registre 2 horas na tarefa MOB-123 hoje com a descrição 'Desenvolvimento da tela inicial'`
-   `Qual o status da tarefa MOB-123?`
-   `Mude o status da tarefa MOB-123 para 'Em Andamento'`
-   `Crie as seguintes tarefas no projeto 'Website': 1. Título: 'Atualizar footer', Descrição: 'Adicionar novos links'. 2. Título: 'Criar página de contato', Descrição: 'Formulário com nome, email e mensagem'`

---

## ⚙️ Estrutura e Desenvolvimento

Para informações sobre a arquitetura do projeto, o padrão de ferramentas utilizado e como adicionar novas funcionalidades, consulte o nosso **[Guia do Desenvolvedor](./docs/DEVELOPER_GUIDE.md)**.