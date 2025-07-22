# PROJECT DOCUMENTATION - Jira Agent

## 📋 Status do Projeto

**Data da Análise**: 2025-07-22  
**Versão Analisada**: 1.1.0  
**Framework**: Google Agent Development Kit (ADK)  
**Estado**: Necessita reestruturação completa  

---

## 🔍 Análise do Estado Atual

### Problemas Identificados

1. **Arquitetura Inconsistente**
   - Mistura de padrões de implementação (`FunctionTool` vs `@tool`)
   - Estrutura de pastas não padronizada
   - Responsabilidades mal definidas

2. **Não Conformidade com Padrões ADK**
   - Uso de `FunctionTool` em vez do padrão oficial `@tool`
   - Falta de validação adequada com Pydantic
   - Documentação inline insuficiente

3. **Problemas de Código**
   - Mistura de português e inglês
   - Configurações espalhadas
   - Tratamento de erro inconsistente
   - Falta de testes

---

## 🛠️ Funcionalidades Existentes (3 Ferramentas)

### 1. **Ferramentas de Projeto (Implementadas)**
- `search_projects`: Busca e lista projetos Jira
- `get_project_details`: Obtém detalhes específicos de um projeto

### 2. **Ferramentas de Issues (Implementadas)**
- `create_issue`: Cria uma única issue no Jira com validação e worklog opcional

### 3. **Ferramentas Planejadas (Não Implementadas)**
- Ferramentas de busca de issues
- Ferramentas de atualização de issues
- Ferramentas de worklog individuais
- Ferramentas de operações em lote

### Análise Detalhada das Ferramentas

#### `search_jira_projects`
```python
# Localização: src/tools/search_jira_projects.py
# Padrão: FunctionTool (❌ Incorreto)
# Schema: SearchProjectsInput
```
**Funcionalidade**: Busca projetos por termo ou lista todos  
**Problemas**: Uso de FunctionTool, nome inconsistente  

#### `create_issue`
```python
# Localização: src/tools/create_issue.py  
# Padrão: FunctionTool (❌ Incorreto)
# Schema: CreateIssueInput
```
**Funcionalidade**: Cria issue individual com validação de projeto  
**Problemas**: Padrão incorreto, validação manual de data  

#### `batch_create_issues`
```python
# Localização: src/tools/batch_create_issues.py
# Padrão: FunctionTool (❌ Incorreto)  
# Schema: BatchCreateIssuesInput + IssueToCreate
```
**Funcionalidade**: Criação em lote com registro opcional de horas  
**Problemas**: Nome da tool incorreto no final, validação inconsistente  

---

## 🏗️ Arquitetura do Google ADK (Padrões Oficiais)

### Padrões de Implementação de Tools

#### ✅ Padrão Correto (ADK 2025)
```python
from google.adk.tools import tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    parameter: str = Field(description="Clear description for LLM")

@tool
def my_tool(tool_input: MyToolInput) -> str:
    """Tool description for LLM to understand when to use it."""
    # Implementation
    return "Result"
```

#### ❌ Padrão Atual (Incorreto)
```python
from google.adk.tools import FunctionTool

def my_tool_func(tool_input: MyToolInput) -> str:
    # Implementation
    pass

my_tool = FunctionTool(my_tool_func)
my_tool.name = "my_tool"
```

### Arquitetura Modular Recomendada

```
src/
├── core/                     # Configurações e exceções
│   ├── config.py
│   ├── exceptions.py
│   └── validators.py
├── infrastructure/           # Acesso a dados externos
│   ├── jira_client.py
│   └── repositories/
├── domain/                   # Lógica de negócio
│   ├── models/
│   └── services/
├── agents/                   # Agentes ADK
│   ├── jira_agent.py
│   └── middlewares/
├── tools/                    # Ferramentas organizadas
│   ├── project/
│   ├── issue/
│   └── worklog/
└── api/                      # Interface FastAPI
    ├── main.py
    └── routers/
```

---

## 🔧 Configurações e Ambiente

### Variáveis de Ambiente Atuais
```env
# Configurações Jira
JIRA_SERVER_URL="https://domain.atlassian.net"
JIRA_USERNAME="email@example.com"
JIRA_API_TOKEN="api-token"

# Configurações Google ADK
GOOGLE_API_KEY="google-api-key"
GOOGLE_MODEL="gemini-2.0-flash"
GOOGLE_GENAI_USE_VERTEXAI="false"
```

### Problemas de Configuração
- Nomes de variáveis inconsistentes (JIRA_SERVER vs JIRA_SERVER_URL)
- Falta de configurações de aplicação (APP_NAME, LOG_LEVEL)
- Sem validação de configurações obrigatórias

---

## 🔄 Integração com Jira

### Cliente Jira Atual
```python
# Localização: src/utils.py
def get_jira_client():
    jira_client = JIRA(
        server=config.JIRA_SERVER, 
        basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN)
    )
    return jira_client
```

### Funcionalidades de Utilidade
- `find_project_by_identifier`: Busca projeto por chave/nome
- `find_issue_by_summary`: Busca issue por título
- `resolve_issue_identifier`: Resolve identificador de issue
- `validate_project_access`: Valida acesso ao projeto
- `get_user_account_id_by_email`: Busca accountId por email
- `log_work_for_issue`: Registra trabalho em issue

### APIs Jira Utilizadas
- `jira_client.projects()`: Lista projetos
- `jira_client.create_issue()`: Cria issues
- `jira_client.search_issues()`: Busca issues
- `jira_client.add_worklog()`: Registra horas
- `jira_client.search_users()`: Busca usuários

---

## 🚧 Guardrails e Middleware

### Sistema Atual
```python
# Localização: src/agents/guardrails.py
def before_tool_callback_handler(tool, args, tool_context):
    # Apenas logging, sem validações
    logging.info(f"Tool '{tool.name}' executando com args: {args}")
    return None
```

**Funcionalidade**: Log de chamadas de ferramentas  
**Limitações**: Sem validação, sem controle de acesso  

---

## 📦 Dependências

### Requirements.txt Atual
```
google-adk
python-dotenv
jira
dateparser
fastapi
uvicorn[standard]
```

### Análise de Dependências
- **google-adk**: Framework principal ✅
- **jira**: Cliente oficial Jira ✅
- **fastapi**: API web framework ✅
- **dateparser**: Parse de datas ✅
- **python-dotenv**: Variáveis de ambiente ✅
- **uvicorn**: ASGI server ✅

---

## 🎯 Agente Principal

### Configuração Atual
```python
# Localização: src/agents/agent.py
root_agent = LlmAgent(
    name="JiraAgent",
    description="Agente para interagir com o Jira...",
    model=config.GOOGLE_MODEL,
    tools=[...],  # 11 ferramentas
    before_tool_callback=before_tool_callback_handler,
    instruction="Instruções em português..."
)
```

### Instruções do Agente
- Prioriza ferramentas em lote
- Instrução em português
- Foco em operações batch para eficiência

---

## 📚 Documentação Existente

### README.md
- Instruções de instalação ✅
- Exemplos de uso ✅
- Configuração de ambiente ✅
- Documentação do FastAPI ✅

### DEVELOPER_GUIDE.md
- Explicação da arquitetura ✅
- Padrão de ferramentas ✅
- Guia de desenvolvimento ✅
- Limitado ao padrão atual ❌

### Task Documentation
- `batch_create_issues.md`: Plano de implementação
- `batch_log_work.md`: Plano de implementação

---

## 🧪 Testes

**Status**: ❌ Não existem testes automatizados  
**Necessário**: Implementar testes unitários para todas as ferramentas

---

## 📊 Métricas do Projeto

- **Linhas de código**: ~1,500 linhas
- **Ferramentas**: 11 ferramentas funcionais
- **Cobertura de testes**: 0%
- **Documentação**: Parcial
- **Conformidade ADK**: 0% (uso de FunctionTool)

---

## 🎯 Plano de Reestruturação

### Prioridades de Reestruturação

1. **Alta Prioridade**
   - Migrar de FunctionTool para @tool
   - Reestruturar arquitetura modular
   - Padronizar nomes e convenções
   - Centralizar configurações

2. **Média Prioridade**
   - Implementar testes unitários
   - Melhorar documentação inline
   - Padronizar tratamento de erros
   - Implementar logging estruturado

3. **Baixa Prioridade**
   - Otimizar performance
   - Adicionar métricas
   - Implementar cache
   - Melhorar UI/UX da API

### Cronograma Estimado

- **Fase 1** (4-6 horas): Documentação e nova arquitetura
- **Fase 2** (8-10 horas): Reestruturação e migração
- **Fase 3** (4-6 horas): Testes e validação
- **Total**: 16-22 horas de desenvolvimento

---

## 🔄 Nova Estrutura Proposta

```
jira-agent/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configurações centralizadas
│   │   ├── exceptions.py          # Exceções customizadas
│   │   └── validators.py          # Validadores reutilizáveis
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── jira_client.py         # Cliente Jira especializado
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── project_repository.py
│   │       ├── issue_repository.py
│   │       └── worklog_repository.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── issue.py
│   │   │   └── worklog.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── project_service.py
│   │       ├── issue_service.py
│   │       └── worklog_service.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── jira_agent.py          # Agente principal
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── auth_middleware.py
│   │       └── validation_middleware.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── project/
│   │   │   ├── __init__.py
│   │   │   ├── search_projects.py
│   │   │   └── get_project_details.py
│   │   ├── issue/
│   │   │   ├── __init__.py
│   │   │   ├── create_issue.py
│   │   │   ├── get_issue_details.py
│   │   │   ├── search_issues.py
│   │   │   ├── update_issue_status.py
│   │   │   ├── update_issue_estimates.py
│   │   │   ├── get_issue_types.py
│   │   │   └── batch_create_issues.py
│   │   └── worklog/
│   │       ├── __init__.py
│   │       ├── log_work.py
│   │       └── batch_log_work.py
│   └── api/
│       ├── __init__.py
│       ├── main.py                # FastAPI app
│       ├── routers/
│       │   ├── __init__.py
│       │   └── agent_router.py
│       └── schemas/
│           ├── __init__.py
│           └── api_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_tools/
│   ├── test_services/
│   └── test_integration/
├── docs/
│   ├── README.md
│   ├── DEVELOPER_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
├── .env.example                   # Template de variáveis
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── PROJECT_DOCUMENTATION.md      # Este arquivo
```

---

## 📝 Considerações Finais

O projeto atual funciona mas não segue os padrões modernos do Google ADK. A reestruturação proposta irá:

1. **Melhorar Manutenibilidade**: Código organizado e padronizado
2. **Facilitar Expansão**: Arquitetura modular permite novas funcionalidades
3. **Garantir Qualidade**: Testes e validações adequadas
4. **Seguir Padrões**: Conformidade com Google ADK 2025
5. **Melhorar Documentação**: Guias técnicos completos

O investimento na reestruturação criará uma base sólida para o crescimento futuro do projeto.