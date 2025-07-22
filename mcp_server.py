#!/usr/bin/env python3
"""
MCP Server para Jira Agent.
Este servidor expõe as funcionalidades do Jira Agent via protocolo MCP
para integração com IDEs que suportam MCP.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List
import logging
import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
JIRA_API_URL = os.getenv("JIRA_API_URL", "http://localhost:8000")
MCP_HOST = os.getenv("MCP_HOST", "localhost")
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))

# Criar servidor MCP
server = Server("jira-agent")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Lista todas as ferramentas disponíveis do Jira Agent."""
    return [
        Tool(
            name="search_projects",
            description="Buscar projetos no Jira por nome ou chave",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca para projetos"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_project_details",
            description="Obter detalhes completos de um projeto específico",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Chave do projeto (ex: DEMO, PROJ)"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="create_issue",
            description="Criar uma nova issue no Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Chave do projeto"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Título/resumo da issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição detalhada da issue"
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Tipo da issue (Task, Bug, Story, etc.)",
                        "default": "Task"
                    }
                },
                "required": ["project_key", "summary", "description"]
            }
        ),
        Tool(
            name="chat_with_jira_agent",
            description="Conversa natural com o Jira Agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mensagem para o agente"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Executa uma ferramenta específica."""
    try:
        if name == "search_projects":
            return await _search_projects(arguments["query"])
        elif name == "get_project_details":
            return await _get_project_details(arguments["project_key"])
        elif name == "create_issue":
            return await _create_issue(arguments)
        elif name == "chat_with_jira_agent":
            return await _chat_with_agent(arguments["message"])
        else:
            return [TextContent(type="text", text=f"Ferramenta '{name}' não encontrada")]
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {name}: {e}")
        return [TextContent(type="text", text=f"Erro: {str(e)}")]

async def _search_projects(query: str) -> List[TextContent]:
    """Buscar projetos no Jira."""
    try:
        response = requests.get(f"{JIRA_API_URL}/projects/search", params={"query": query})
        if response.status_code == 200:
            projects = response.json()
            if projects:
                result = "🔍 **Projetos encontrados:**\n\n"
                for project in projects:
                    result += f"• **{project['key']}** - {project['name']}\n"
                    if 'description' in project:
                        result += f"  📄 {project['description'][:100]}...\n"
                    result += "\n"
                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text=f"❌ Nenhum projeto encontrado para: '{query}'")]
        else:
            return [TextContent(type="text", text=f"❌ Erro na busca: {response.status_code}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro de conexão: {str(e)}")]

async def _get_project_details(project_key: str) -> List[TextContent]:
    """Obter detalhes de um projeto."""
    try:
        response = requests.get(f"{JIRA_API_URL}/projects/{project_key}")
        if response.status_code == 200:
            project = response.json()
            result = f"📊 **Detalhes do Projeto {project_key}**\n\n"
            result += f"**Nome:** {project.get('name', 'N/A')}\n"
            result += f"**Chave:** {project.get('key', 'N/A')}\n"
            result += f"**Tipo:** {project.get('projectTypeKey', 'N/A')}\n"
            if 'description' in project:
                result += f"**Descrição:** {project['description']}\n"
            if 'lead' in project:
                result += f"**Líder:** {project['lead'].get('displayName', 'N/A')}\n"
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"❌ Projeto '{project_key}' não encontrado")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro de conexão: {str(e)}")]

async def _create_issue(arguments: Dict[str, Any]) -> List[TextContent]:
    """Criar uma nova issue."""
    try:
        payload = {
            "project_key": arguments["project_key"],
            "summary": arguments["summary"],
            "description": arguments["description"],
            "issue_type": arguments.get("issue_type", "Task")
        }
        
        response = requests.post(f"{JIRA_API_URL}/issues", json=payload)
        if response.status_code == 201:
            issue = response.json()
            result = f"✅ **Issue criada com sucesso!**\n\n"
            result += f"**ID:** {issue.get('key', 'N/A')}\n"
            result += f"**Título:** {arguments['summary']}\n"
            result += f"**Projeto:** {arguments['project_key']}\n"
            result += f"**Tipo:** {arguments.get('issue_type', 'Task')}\n"
            if 'self' in issue:
                result += f"**URL:** {issue['self']}\n"
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"❌ Erro ao criar issue: {response.status_code}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro de conexão: {str(e)}")]

async def _chat_with_agent(message: str) -> List[TextContent]:
    """Conversar com o Jira Agent."""
    try:
        payload = {"message": message}
        response = requests.post(f"{JIRA_API_URL}/converse", json=payload)
        if response.status_code == 200:
            result = response.json()
            return [TextContent(type="text", text=result.get("response", "Sem resposta"))]
        else:
            return [TextContent(type="text", text=f"❌ Erro na conversa: {response.status_code}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro de conexão: {str(e)}")]

@server.list_resources()
async def list_resources() -> List[Resource]:
    """Lista recursos disponíveis."""
    return [
        Resource(
            uri="jira://config",
            name="Configuração do Jira Agent",
            description="Configurações atuais do sistema",
            mimeType="application/json"
        ),
        Resource(
            uri="jira://status",
            name="Status do Sistema",
            description="Status atual do Jira Agent",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Lê um recurso específico."""
    if uri == "jira://config":
        try:
            response = requests.get(f"{JIRA_API_URL}/config")
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            else:
                return json.dumps({"error": "Não foi possível obter configuração"})
        except:
            return json.dumps({"error": "Erro de conexão com o Jira Agent"})
    
    elif uri == "jira://status":
        try:
            response = requests.get(f"{JIRA_API_URL}/")
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            else:
                return json.dumps({"error": "Serviço indisponível"})
        except:
            return json.dumps({"error": "Erro de conexão com o Jira Agent"})
    
    else:
        return json.dumps({"error": f"Recurso não encontrado: {uri}"})

def start_health_check():
    """Health check simples para o container."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "healthy"}')
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Suprimir logs do health check
    
    def run_health_server():
        try:
            httpd = HTTPServer(("0.0.0.0", MCP_PORT), HealthHandler)
            httpd.serve_forever()
        except Exception as e:
            logger.error(f"Erro no health server: {e}")
    
    # Executar health server em thread separada
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

async def main():
    """Função principal do servidor MCP."""
    logger.info("🚀 Iniciando Jira Agent MCP Server...")
    logger.info(f"📡 Conectando ao Jira Agent em: {JIRA_API_URL}")
    
    # Verificar conexão com o Jira Agent
    try:
        response = requests.get(f"{JIRA_API_URL}/", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Conexão com Jira Agent estabelecida")
        else:
            logger.warning(f"⚠️ Jira Agent respondeu com status: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Não foi possível conectar ao Jira Agent: {e}")
        logger.info("🔄 Continuando mesmo assim - tentará reconectar automaticamente")
    
    # Temporariamente desabilitado para debug
    logger.info("🔌 Iniciando servidor MCP...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ stdio_server iniciado com sucesso")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jira-agent",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
    except Exception as e:
        logger.error(f"❌ Erro no stdio_server: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor MCP finalizado")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)