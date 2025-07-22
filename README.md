# Jira Agent - Nova Arquitetura

Um agente moderno de integração com Jira construído com **Google Agent Development Kit (ADK)** seguindo melhores práticas e padrões de arquitetura limpa.

## 🚀 Início Rápido

### 1. Configuração do Ambiente

```bash
# Clone e navegue para o projeto
cd jira-agent

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com seus valores reais:

```env
# Configuração do Jira
JIRA_SERVER_URL="https://seu-dominio.atlassian.net"
JIRA_USERNAME="seu-email@exemplo.com"
JIRA_API_TOKEN="seu-token-api"

# Configuração do Google ADK
GOOGLE_API_KEY="sua-chave-api-google"
GOOGLE_MODEL="gemini-2.0-flash"
```

**Obtenha suas credenciais:**
- **Token API Jira**: https://id.atlassian.com/manage-profile/security/api-tokens
- **Chave API Google**: https://aistudio.google.com/app/apikey

### 3. Execute a Aplicação

```bash
python main.py
```

A aplicação será iniciada em:
- **API**: http://127.0.0.1:8000
- **Documentação**: http://127.0.0.1:8000/docs
- **Docs Interativa**: http://127.0.0.1:8000/redoc

## 📊 Nova Arquitetura

### Princípios de Arquitetura Limpa

```
src/
├── core/                     # Configurações e utilitários principais
│   ├── config.py            # Gerenciamento centralizado de configuração
│   ├── exceptions.py        # Definições de exceções customizadas
│   └── validators.py        # Funções de validação reutilizáveis
├── infrastructure/          # Integração com serviços externos
│   └── jira_client.py      # Cliente da API Jira com tratamento de erros
├── domain/                  # Camada de lógica de negócio
│   ├── models/             # Modelos de domínio com validação
│   └── services/           # Serviços de negócio
├── agents/                  # Configuração dos agentes ADK
│   └── jira_agent.py       # Agente principal com ferramentas
├── tools/                   # Ferramentas ADK (estruturadas corretamente)
│   ├── project/            # Ferramentas relacionadas a projetos
│   ├── issue/              # Ferramentas relacionadas a issues
│   └── worklog/            # Ferramentas relacionadas a worklog
└── api/                     # Aplicação FastAPI
    └── main.py             # Endpoints da API e configuração
```

### Principais Melhorias

#### ✅ Padrões ADK Corretos
- Usa `FunctionTool` seguindo padrões ADK 2025
- Validação Pydantic adequada com descrições detalhadas
- Configuração de agente limpa com padrões oficiais ADK

#### ✅ Separação de Responsabilidades
- Camada Core para configuração e utilitários
- Camada Infrastructure para APIs externas
- Camada Domain para lógica de negócio
- Organização limpa de ferramentas por funcionalidade

#### ✅ Tratamento Robusto de Erros
- Exceções customizadas com códigos de erro
- Validação abrangente em todos os níveis
- Recuperação elegante de erros e feedback ao usuário

#### ✅ Gerenciamento de Configuração
- Configuração baseada em ambiente com validação
- Configurações centralizadas com padrões adequados
- Configuração para desenvolvimento vs produção

#### ✅ Práticas Modernas de Python
- Type hints em todo o código
- Pydantic v2 para validação de dados
- Logging estruturado para melhor debugging

## 🛠️ Ferramentas Disponíveis

#### Ferramentas de Projeto
- `search_projects`: Buscar projetos ou listar todos os projetos disponíveis
- `get_project_details`: Obter informações detalhadas sobre um projeto específico

#### Ferramentas de Issues  
- `create_issue`: Criar novas issues com validação e worklog opcional

### Ferramentas Planejadas (Implementação Futura)
- Ferramentas adicionais de gerenciamento de issues
- Ferramentas de gerenciamento de worklog
- Operações em lote
- Capacidades avançadas de busca

## 🧪 Exemplos de Uso

### Conversar com o Agente

```bash
curl -X POST "http://127.0.0.1:8000/converse" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Liste todos os projetos que contêm mobile"
  }'
```

### Exemplos de Conversas

**Buscar Projetos:**
```
Usuário: "Mostre-me todos os projetos"
Agente: Lista todos os projetos disponíveis com chaves e nomes

Usuário: "Encontre projetos com 'mobile' no nome"
Agente: Mostra resultados filtrados
```

**Detalhes do Projeto:**
```
Usuário: "Me fale sobre o projeto DEMO"
Agente: Fornece informações detalhadas do projeto incluindo descrição e tipo
```

**Criar Issues:**
```
Usuário: "Crie uma task no projeto DEMO com título 'Corrigir bug do login' e descrição 'O botão de login não está funcionando em dispositivos móveis'"
Agente: Cria a issue e fornece a chave da issue e URL
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

- **Core**: Configuração, exceções, validadores
- **Infrastructure**: Clientes de serviços externos (Jira)
- **Domain**: Modelos de negócio e serviços
- **Agents**: Configuração dos agentes ADK
- **Tools**: Ferramentas ADK individuais com `FunctionTool`
- **API**: Aplicação FastAPI e endpoints

### Adicionando Novas Ferramentas

1. Crie o arquivo da ferramenta na categoria apropriada (`src/tools/categoria/`)
2. Defina o modelo de entrada Pydantic com descrições claras
3. Implemente a função da ferramenta com `FunctionTool`
4. Adicione tratamento abrangente de erros
5. Registre a ferramenta na configuração do agente

Exemplo:
```python
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool, ToolContext

class MyToolInput(BaseModel):
    parameter: str = Field(..., description="Descrição clara para o LLM")

def my_tool_function(tool_input: MyToolInput, tool_context: ToolContext = None) -> dict:
    """Descrição da ferramenta para o LLM entender quando usá-la."""
    # Implementação
    return {"status": "success", "result": "Resultado"}

# Criar a instância FunctionTool
my_tool = FunctionTool(func=my_tool_function)
```

### Testes

```bash
# Instalar dependências de desenvolvimento
pip install pytest pytest-asyncio httpx

# Executar testes (quando implementados)
pytest tests/
```

## 📝 Migração da Versão Anterior

Esta versão representa uma reescrita completa seguindo as melhores práticas do Google ADK:

### O que Mudou
- ✅ Uso adequado do `FunctionTool` (era `@tool` incorreto)
- ✅ Arquitetura limpa com separação de responsabilidades
- ✅ Gerenciamento centralizado de configuração
- ✅ Tratamento abrangente de erros e validação
- ✅ Padrões modernos de Python e type hints
- ✅ Melhor estrutura e organização do projeto

### O que Permaneceu Igual
- Mesma funcionalidade principal (projetos, issues, worklog)
- Mesmos endpoints da API para compatibilidade
- Mesmos nomes de variáveis de ambiente
- Mesmas capacidades de integração com Jira

## 🔍 Solução de Problemas

### Problemas Comuns

**"Falha ao carregar configurações da aplicação"**
- Verifique se seu arquivo `.env` existe e tem todas as variáveis necessárias
- Verifique se as credenciais do Jira estão corretas
- Certifique-se de que a chave da API do Google é válida

**"Erro de conexão com Jira"**
- Verifique se JIRA_SERVER_URL está correto (incluir https://)
- Confirme que JIRA_USERNAME é um endereço de email
- Confirme que JIRA_API_TOKEN é válido e tem as permissões adequadas

**"Permissão negada"**
- Certifique-se de que seu usuário Jira tem permissões apropriadas
- Algumas operações requerem permissões de admin do projeto ou superiores

### Debug

Habilite logging de debug configurando no `.env`:
```env
LOG_LEVEL="DEBUG"
DETAILED_ERRORS="true"
```

## 📄 Licença

Este projeto segue práticas modernas de desenvolvimento de software e é projetado para uso em produção com tratamento adequado de erros, validação e capacidades de monitoramento.

## 🤝 Contribuindo

A nova arquitetura torna fácil contribuir:
1. Faça um fork do repositório
2. Crie uma branch de feature
3. Siga os padrões estabelecidos para novas ferramentas ou recursos
4. Adicione testes para nova funcionalidade
5. Envie um pull request

Para perguntas ou suporte, consulte o PROJECT_DOCUMENTATION.md para informações técnicas detalhadas.