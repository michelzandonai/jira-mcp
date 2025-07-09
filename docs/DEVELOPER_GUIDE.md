# Guia do Desenvolvedor - Projeto Jira Agent

Bem-vindo ao guia de desenvolvimento do Jira Agent! Este documento serve como a principal referência técnica para entender a arquitetura do projeto, como as ferramentas funcionam e como adicionar novas funcionalidades de forma consistente e segura.

## 1. Arquitetura do Projeto

O projeto segue uma estrutura modular para separar responsabilidades, facilitando a manutenção e a escalabilidade.

```
/
├─── src/
│    ├─── agents/
│    │    ├─── agent.py         # Define o agente principal e suas ferramentas
│    │    └─── guardrails.py    # Implementa as travas de segurança (callbacks)
│    │
│    ├─── tools/                # Contém a lógica de cada ferramenta individual
│    │    ├─── create_issue.py
│    │    └─── ...
│    │
│    ├─── config.py             # Configurações centrais (modelo, credenciais)
│    └─── utils.py              # Funções utilitárias compartilhadas (ex: cliente Jira)
│
├─── docs/
│    └─── DEVELOPER_GUIDE.md    # Este guia
│
├─── requirements.txt          # Dependências do projeto
└─── README.md                 # Documentação da refatoração
```

-   **`src/agents`**: O cérebro do projeto. `agent.py` monta o agente, conectando o modelo de linguagem (LLM) às ferramentas disponíveis e definindo as instruções de comportamento. `guardrails.py` intercepta chamadas de ferramentas para validação.
-   **`src/tools`**: O "corpo" do projeto. Cada arquivo aqui representa uma habilidade específica que o agente pode executar (ex: criar uma issue, buscar um projeto).
-   **`src/config.py` e `src/utils.py`**: A espinha dorsal que fornece configuração e funcionalidades de apoio para as outras partes do sistema.

---

## 2. O Padrão de Ferramentas (Tool Pattern)

Para garantir que o agente interaja com as ferramentas de forma confiável, adotamos o padrão recomendado pelo **Google ADK**. Este padrão se baseia em três componentes principais:

1.  **`pydantic.BaseModel`**: Uma classe que define os **argumentos** que a ferramenta espera.
2.  **`@tool`**: Um decorador que transforma a função Python em uma `Tool` que o ADK entende.
3.  **Docstrings Descritivas**: Textos que explicam ao LLM o que a ferramenta e seus argumentos fazem.

### Exemplo Prático: `create_issue.py`

Vamos analisar a ferramenta `create_issue` como nosso caso de estudo.

```python
# src/tools/create_issue.py

from pydantic import BaseModel, Field
from google.adk.tools import tool
# ... outras importações

# 1. O Esquema de Entrada (Input Schema) com Pydantic
class CreateIssueInput(BaseModel):
    """Define os argumentos para a ferramenta de criação de issue."""
    project_name_or_key: str = Field(
        description="A chave ou nome do projeto Jira onde a issue será criada (ex: 'PROJ', 'Meu Projeto')."
    )
    summary: str = Field(
        description="O título ou resumo principal da issue."
    )
    # ... outros campos ...

# 2. A Definição da Ferramenta com o Decorador @tool
@tool
def create_issue(tool_input: CreateIssueInput) -> str:
    """
    Cria uma nova issue no Jira com base nos detalhes fornecidos.
    Use esta ferramenta para criar uma única tarefa, bug ou outra issue.

    Args:
        tool_input: Os dados necessários para criar a issue, validados pelo Pydantic.
    """
    # 3. A Lógica da Ferramenta
    try:
        # Acessa os dados de forma segura: tool_input.summary, tool_input.project_name_or_key
        # ...
        return "✅ Issue criada com sucesso!"
    except Exception as e:
        return f"❌ Erro: {e}"
```

#### Análise dos Componentes:

1.  **`CreateIssueInput(BaseModel)`**:
    -   Funciona como um "contrato" de dados.
    -   Cada `Field` define um argumento. O parâmetro `description` é **crucial**, pois é o texto que o LLM lê para entender o que ele deve fornecer para aquele campo.
    -   O Pydantic realiza a **validação automática**. Se o LLM tentar passar um dado no formato errado, a ferramenta nem chega a ser executada, retornando um erro claro.

2.  **`@tool`**:
    -   Este decorador "registra" a função `create_issue` como uma ferramenta oficial do ADK.
    -   Ele inspeciona a função, sua docstring e a anotação de tipo (`tool_input: CreateIssueInput`) para montar uma especificação detalhada que é enviada ao LLM.

3.  **Lógica da Ferramenta**:
    -   A função agora recebe um único argumento, `tool_input`, que é uma instância preenchida e validada da classe `CreateIssueInput`.
    -   O acesso aos dados é feito de forma segura e previsível (ex: `tool_input.summary`).

---

## 3. Como Adicionar uma Nova Ferramenta

Siga estes passos para adicionar uma nova ferramenta (ex: `minha_nova_ferramenta.py`):

1.  **Crie o Arquivo**: Crie `src/tools/minha_nova_ferramenta.py`.

2.  **Defina o Input**: Crie uma classe com `pydantic.BaseModel` para os argumentos da sua ferramenta. Lembre-se de usar `Field(description="...")` para cada argumento.

    ```python
    from pydantic import BaseModel, Field

    class MinhaNovaFerramentaInput(BaseModel):
        parametro1: str = Field(description="Descrição clara do que é o parâmetro 1.")
        parametro_opcional: int = Field(default=10, description="Descrição do parâmetro opcional.")
    ```

3.  **Crie a Função da Ferramenta**: Crie a função decorada com `@tool` e com uma docstring explicativa.

    ```python
    from google.adk.tools import tool

    @tool
    def minha_nova_ferramenta(tool_input: MinhaNovaFerramentaInput) -> str:
        """
        Esta docstring explica o que a ferramenta faz em alto nível.
        O LLM a usará para decidir quando chamar sua ferramenta.
        """
        # Sua lógica aqui
        # ...
        return "Resultado da sua ferramenta"
    ```

4.  **Registre a Ferramenta no Agente**: Abra `src/agents/agent.py`, importe sua nova ferramenta e adicione-a à lista `tools` na definição do `root_agent`.

    ```python
    # src/agents/agent.py
    
    # ... outras importações de ferramentas
    from tools.minha_nova_ferramenta import minha_nova_ferramenta # 1. Importe
    
    root_agent = Agent(
        # ...
        tools=[
            # ... outras ferramentas
            minha_nova_ferramenta, # 2. Adicione à lista
        ],
        # ...
    )
    ```

Pronto! Seguindo este padrão, você garante que sua nova ferramenta se integra perfeitamente ao sistema, aproveitando toda a robustez e segurança oferecidas pelo Google ADK.
