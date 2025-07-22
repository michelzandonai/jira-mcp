FROM python:3.11-slim

# Metadados
LABEL maintainer="Jira Agent MCP Server"
LABEL version="1.0.0"
LABEL description="MCP Server for Jira Agent integration"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Criar usuário não-root
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependência MCP
RUN pip install --no-cache-dir mcp>=0.9.0

# Copiar código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /app/logs && chown -R mcp:mcp /app

# Mudar para usuário não-root
USER mcp

# Porta para o MCP server
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 3000)); s.close()" || exit 1

# Comando padrão
CMD ["python", "mcp_server.py"]