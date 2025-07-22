#!/usr/bin/env python3
"""
MCP Server funcional para Jira Agent
"""

import asyncio
import json
import logging
import os
import requests
from typing import Any, Dict, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
JIRA_API_URL = os.getenv("JIRA_API_URL", "http://jira-agent-api:8000")

async def main():
    """Função principal do servidor MCP."""
    logger.info("🚀 Iniciando Jira Agent MCP Server...")
    
    try:
        # Importar bibliotecas MCP
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.server.models import InitializationOptions
        from mcp.types import (
            Tool,
            TextContent,
            ServerCapabilities,
            ToolsCapability,
            ResourcesCapability
        )
        
        logger.info("✅ Bibliotecas MCP importadas")
        
        # Criar servidor
        server = Server("jira-agent")
        
        # Definir ferramentas
        @server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="search_projects",
                    description="Buscar projetos no Jira",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Termo de busca"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_project_details",
                    description="Obter detalhes de um projeto",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "Chave do projeto"
                            }
                        },
                        "required": ["project_key"]
                    }
                )
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "search_projects":
                    return await search_projects(arguments["query"])
                elif name == "get_project_details":
                    return await get_project_details(arguments["project_key"])
                else:
                    return [TextContent(type="text", text=f"Ferramenta '{name}' não encontrada")]
            except Exception as e:
                logger.error(f"Erro na ferramenta {name}: {e}")
                return [TextContent(type="text", text=f"Erro: {str(e)}")]
        
        # Verificar conexão com API
        try:
            response = requests.get(f"{JIRA_API_URL}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Conexão com Jira Agent estabelecida")
            else:
                logger.warning(f"⚠️ API respondeu com status: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Erro conectando à API: {e}")
        
        # Iniciar servidor
        logger.info("🔌 Iniciando servidor MCP...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ Servidor MCP iniciado")
            
            # Usar capabilities simples
            capabilities = ServerCapabilities(
                tools=ToolsCapability(listChanged=False),
                resources=ResourcesCapability(subscribe=False, listChanged=False)
            )
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jira-agent",
                    server_version="1.0.0",
                    capabilities=capabilities
                )
            )
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def search_projects(query: str):
    """Buscar projetos no Jira."""
    from mcp.types import TextContent
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

async def get_project_details(project_key: str):
    """Obter detalhes de um projeto."""
    from mcp.types import TextContent
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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor finalizado")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        exit(1)