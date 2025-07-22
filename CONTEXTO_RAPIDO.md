# 🎯 Contexto Rápido - Jira Agent

**O que você pode fazer AGORA neste projeto**

---

## ✅ O QUE FUNCIONA (Estado Atual)

### 🤖 Agentes Disponíveis
- **1 Agente Principal**: Jira Agent (integração com Jira via Google ADK)

### 🛠️ Ferramentas Funcionais (3 no total)

#### 📁 **Projetos**
- ✅ **`search_projects`** - Buscar e listar projetos Jira
  - Lista todos os projetos disponíveis
  - Busca por nome ou chave do projeto
  - Retorna: chave, nome e tipo do projeto

- ✅ **`get_project_details`** - Detalhes específicos de um projeto
  - Informações completas sobre um projeto
  - Inclui descrição, tipo, lead, URL
  - Valida se o projeto existe e você tem acesso

#### 📋 **Issues**
- ✅ **`create_issue`** - Criar issues no Jira
  - Cria issue com título, descrição e tipo
  - Validação automática de dados
  - Estimativas de tempo (opcional)
  - Worklog imediato (opcional)
  - Atribuição automática para você
  - Retorna chave da issue e URL

### 🔌 Integrações Ativas
- ✅ **Jira API** - Totalmente funcional
- ✅ **Google ADK** - Configurado corretamente
- ✅ **FastAPI** - API REST funcionando

### 📊 Arquitetura Limpa
- ✅ **Validação centralizada** - Todos os dados são validados
- ✅ **Tratamento de erros** - Erros claros e informativos
- ✅ **Configuração por ambiente** - .env file
- ✅ **Logging estruturado** - Para debugging

---

## ❌ O QUE NÃO FUNCIONA (Ainda)

### 🚫 Ferramentas Não Implementadas
- ❌ Buscar issues por título/resumo
- ❌ Obter detalhes de issues específicas
- ❌ Atualizar status de issues
- ❌ Atualizar estimativas de tempo
- ❌ Listar tipos de issues disponíveis
- ❌ Registrar worklog em issues existentes
- ❌ Operações em lote (criar múltiplas issues)
- ❌ Operações em lote (worklog múltiplo)

### 🚫 Recursos Não Disponíveis
- ❌ Múltiplos agentes
- ❌ Cache de dados
- ❌ Rate limiting
- ❌ Monitoramento avançado
- ❌ Testes automatizados
- ❌ Repository Pattern (planejado)

---

## 🎮 COMO USAR - Guia Rápido

### 1. **Configuração Obrigatória**
```bash
# 1. Copie o arquivo de exemplo
cp .env.example .env

# 2. Configure TODAS as variáveis obrigatórias no .env
# (TODAS são obrigatórias - sistema não funciona sem elas)
JIRA_SERVER_URL="https://sua-empresa.atlassian.net"
JIRA_USERNAME="seu-email@empresa.com"
JIRA_API_TOKEN="seu-token-aqui"
GOOGLE_API_KEY="sua-chave-google"
GOOGLE_MODEL="gemini-2.0-flash"
# ... e mais 9 variáveis obrigatórias (ver .env.example)

# 3. Execute
python main.py
```

### 2. **Exemplos de Uso Imediato**

#### 📁 **Ver Projetos**
```bash
curl -X POST "http://127.0.0.1:8000/converse" \
  -H "Content-Type: application/json" \
  -d '{"message": "Liste todos os projetos"}'
```

#### 📋 **Criar Issue**
```bash
curl -X POST "http://127.0.0.1:8000/converse" \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie uma task no projeto DEMO com título Bug no login"}'
```

#### 🔍 **Buscar Projeto Específico**
```bash
curl -X POST "http://127.0.0.1:8000/converse" \
  -H "Content-Type: application/json" \
  -d '{"message": "Encontre projetos com mobile no nome"}'
```

---

## 💬 COMANDOS QUE FUNCIONAM

### Para o Agente (linguagem natural):

#### ✅ **Projetos**
- "Liste todos os projetos"
- "Encontre projetos com 'mobile' no nome"
- "Me mostre detalhes do projeto DEMO"
- "Quais projetos estão disponíveis?"

#### ✅ **Issues**
- "Crie uma task no projeto DEMO com título 'Bug no login'"
- "Crie uma issue tipo Story no projeto ABC"
- "Crie uma task com 4 horas de estimativa"
- "Crie uma issue e registre 2 horas de trabalho para hoje"

---

## 🚨 LIMITAÇÕES ATUAIS

### 🔒 **O que você NÃO pode fazer:**
- ❌ Buscar issues existentes
- ❌ Atualizar issues
- ❌ Ver worklogs existentes
- ❌ Fazer operações em lote
- ❌ Usar múltiplos agentes simultâneos
- ❌ Cache de resultados
- ❌ Operações offline

### ⚠️ **Restrições:**
- **Configuração**: TODAS as 14 variáveis de ambiente são obrigatórias
- **Dependências**: Precisa de internet (Jira API + Google ADK)  
- **Autenticação**: Só funciona com token de API válido
- **Permissões**: Limitado às permissões do usuário no Jira
- **Rate Limits**: Sujeito aos limites da API do Jira

---

## 🎯 CASOS DE USO IDEAIS (Agora)

### ✅ **O que funciona bem:**
1. **Explorar projetos** - Ver o que existe na sua instância Jira
2. **Criar issues rapidamente** - Sem precisar abrir o Jira
3. **Automação básica** - Via API REST ou comandos diretos
4. **Prototipagem** - Testar integrações com Jira

### ❌ **O que ainda não é viável:**
1. **Gestão completa de issues** - Precisa das ferramentas de atualização
2. **Relatórios de worklog** - Precisa das ferramentas de consulta
3. **Workflows complexos** - Precisa de mais ferramentas
4. **Operações em massa** - Precisa das ferramentas de lote

---

## 🚀 PRÓXIMOS PASSOS SUGERIDOS

### Para tornar o projeto mais útil:
1. **Implementar busca de issues** (`search_issues_by_summary`)
2. **Implementar detalhes de issues** (`get_issue_details`)
3. **Implementar atualização de status** (`update_issue_status`)
4. **Implementar worklog** (`log_work_on_issue`)

### Para melhorar a experiência:
1. **Adicionar testes automatizados**
2. **Implementar cache básico**
3. **Melhorar documentação das APIs**
4. **Adicionar mais exemplos de uso**

---

## 📋 RESUMO EXECUTIVO

**🟢 PRONTO PARA USO:**
- Listar e buscar projetos ✅
- Criar issues básicas ✅
- Integração Jira funcional ✅
- API REST operacional ✅

**🟡 EM DESENVOLVIMENTO:**
- Ferramentas de gestão de issues
- Operações em lote
- Funcionalidades avançadas

**🔴 NÃO DISPONÍVEL:**
- Gestão completa de issues
- Relatórios e analytics
- Workflows complexos
- Operações offline

**💡 MELHOR USO ATUAL:** Automação simples de criação de issues e exploração de projetos Jira via linguagem natural.