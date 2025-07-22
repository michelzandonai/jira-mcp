#!/usr/bin/env python3
"""
MCP Server simplificado para debug
"""

import asyncio
import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Função principal simplificada."""
    logger.info("🚀 Iniciando MCP Server Simplificado...")
    
    try:
        logger.info("📚 Importando bibliotecas MCP...")
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.server.models import InitializationOptions
        from mcp.types import ServerCapabilities
        logger.info("✅ Bibliotecas importadas com sucesso")
        
        # Criar servidor
        logger.info("🔨 Criando servidor MCP...")
        server = Server("jira-agent")
        logger.info("✅ Servidor criado com sucesso")
        
        # Adicionar uma ferramenta simples para teste
        @server.list_tools()
        async def list_tools():
            return []
        
        @server.call_tool()
        async def call_tool(name, arguments):
            return []
        
        logger.info("🔌 Iniciando stdio_server...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ stdio_server iniciado")
            logger.info("🎯 Executando servidor...")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jira-agent",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={},
                        resources={}
                    )
                )
            )
            
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor finalizado")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)