# src/agents/guardrails.py
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any
import logging

# Configura o logging para exibir informações de debug
logging.basicConfig(level=logging.INFO)

def before_tool_callback_handler(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Função de guardrail executada antes de cada chamada de ferramenta.

    Esta função serve como um ponto de controle central para:
    1. Registrar as chamadas de ferramentas e seus argumentos.
    2. Validar ou modificar os argumentos antes da execução.
    3. Bloquear a execução de uma ferramenta se os argumentos não estiverem
       em conformidade com as políticas de segurança definidas.

    Atualmente, ela apenas registra a chamada para fins de auditoria e permite
    que a execução continue.

    Args:
        tool: O objeto da ferramenta que está prestes a ser chamada.
        args: O dicionário de argumentos gerado pelo LLM para a ferramenta.
        tool_context: O contexto da ferramenta, que fornece acesso ao estado da sessão.

    Returns:
        None: Se a execução da ferramenta for permitida.
        Dict: Um dicionário representando o resultado da ferramenta,
              caso a execução deva ser bloqueada.
    """
    agent_name = tool_context.agent_name
    tool_name = tool.name
    
    logging.info(
        f"[GUARDRAIL] Agente '{agent_name}' vai executar a ferramenta '{tool_name}' "
        f"com os seguintes argumentos: {args}"
    )

    # --- Ponto de Extensão para Validações Futuras ---
    # Exemplo: Bloquear uma ferramenta específica se um argumento for inválido.
    #
    # if tool_name == "minha_ferramenta_critica":
    #     if "parametro_sensivel" in args and args["parametro_sensivel"] == "valor_proibido":
    #         logging.warning(f"[GUARDRAIL] Bloqueando a execução da ferramenta '{tool_name}' devido a argumento inválido.")
    #         return {
    #             "status": "error",
    #             "error_message": "A execução foi bloqueada pela política de segurança."
    #         }

    # Permite a execução da ferramenta
    return None
