#!/usr/bin/env python3
"""
Teste simples para identificar problemas com MCP server.
"""

import asyncio
import sys
import traceback

print("🔍 Testando importações...")

try:
    from mcp.server import Server
    print("✅ mcp.server importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar mcp.server: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from mcp.server.stdio import stdio_server
    print("✅ stdio_server importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar stdio_server: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from mcp.server.models import InitializationOptions
    print("✅ InitializationOptions importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar InitializationOptions: {e}")
    traceback.print_exc()
    sys.exit(1)

print("🚀 Testando criação do servidor...")

try:
    server = Server("test-server")
    print("✅ Servidor MCP criado com sucesso")
except Exception as e:
    print(f"❌ Erro ao criar servidor: {e}")
    traceback.print_exc()
    sys.exit(1)

print("🔌 Testando stdio_server...")

async def test_stdio():
    try:
        print("Iniciando teste stdio_server...")
        async with stdio_server() as (read_stream, write_stream):
            print("✅ stdio_server funcionando")
            return True
    except Exception as e:
        print(f"❌ Erro no stdio_server: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_stdio())
        if result:
            print("✅ Teste completado com sucesso!")
        else:
            print("❌ Teste falhou")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        traceback.print_exc()
        sys.exit(1)