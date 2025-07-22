#!/bin/bash

# Script de deploy para Jira Agent MCP Server
# Autor: Jira Agent Team
# Versão: 1.0.0

set -e

echo "🚀 Deploy Jira Agent MCP Server"
echo "================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Docker está rodando
check_docker() {
    log_info "Verificando Docker..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker não está rodando. Por favor, inicie o Docker."
        exit 1
    fi
    log_success "Docker está rodando"
}

# Parar containers existentes
stop_containers() {
    log_info "Parando containers existentes..."
    docker-compose down --remove-orphans 2>/dev/null || true
    log_success "Containers parados"
}

# Build das imagens
build_images() {
    log_info "Construindo imagens Docker..."
    docker-compose build --no-cache
    log_success "Imagens construídas"
}

# Iniciar serviços
start_services() {
    log_info "Iniciando serviços..."
    docker-compose up -d
    log_success "Serviços iniciados"
}

# Aguardar serviços ficarem prontos
wait_for_services() {
    log_info "Aguardando serviços ficarem prontos..."
    
    # Aguardar API
    echo -n "  Aguardando Jira Agent API..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo " ✅"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Aguardar MCP Server
    echo -n "  Aguardando MCP Server..."
    for i in {1..30}; do
        if docker exec jira-mcp-server python -c "import socket; s=socket.socket(); s.connect(('localhost', 3000)); s.close()" 2>/dev/null; then
            echo " ✅"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    log_success "Todos os serviços estão prontos"
}

# Teste básico
test_services() {
    log_info "Testando serviços..."
    
    # Teste API
    log_info "  Testando Jira Agent API..."
    if response=$(curl -s http://localhost:8000/); then
        if echo "$response" | grep -q "healthy"; then
            log_success "  API está respondendo corretamente"
        else
            log_warning "  API respondeu mas sem status healthy"
        fi
    else
        log_error "  API não está respondendo"
        return 1
    fi
    
    # Teste configuração
    log_info "  Testando configuração..."
    if curl -s http://localhost:8000/config > /dev/null; then
        log_success "  Configuração acessível"
    else
        log_warning "  Configuração não acessível"
    fi
}

# Mostrar status dos containers
show_status() {
    log_info "Status dos containers:"
    docker-compose ps
    
    echo ""
    log_info "Logs recentes:"
    docker-compose logs --tail=10
}

# Mostrar informações de acesso
show_access_info() {
    echo ""
    echo "🎉 Deploy concluído com sucesso!"
    echo "================================"
    echo ""
    echo "📍 Endpoints disponíveis:"
    echo "  🏠 API Principal:     http://localhost:8000"
    echo "  📚 Documentação:      http://localhost:8000/docs"
    echo "  📖 ReDoc:             http://localhost:8000/redoc"
    echo "  🔌 MCP Server:        Container jira-mcp-server (porta 3000)"
    echo ""
    echo "🔧 Configuração MCP para sua IDE:"
    echo "  Arquivo: claude_desktop_config.json"
    echo "  Conteúdo:"
    cat claude_desktop_config.json | sed 's/^/    /'
    echo ""
    echo "🛠️ Comandos úteis:"
    echo "  Ver logs:           docker-compose logs -f"
    echo "  Parar serviços:     docker-compose down"
    echo "  Reiniciar:          ./deploy.sh"
    echo "  Status:             docker-compose ps"
    echo ""
}

# Função principal
main() {
    # Verificar argumentos
    case "${1:-deploy}" in
        "deploy")
            check_docker
            stop_containers
            build_images
            start_services
            wait_for_services
            test_services
            show_status
            show_access_info
            ;;
        "stop")
            log_info "Parando todos os serviços..."
            docker-compose down
            log_success "Serviços parados"
            ;;
        "restart")
            log_info "Reiniciando serviços..."
            docker-compose restart
            wait_for_services
            log_success "Serviços reiniciados"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            show_status
            ;;
        "help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos:"
            echo "  deploy    - Deploy completo (padrão)"
            echo "  stop      - Parar todos os serviços"
            echo "  restart   - Reiniciar serviços"
            echo "  logs      - Mostrar logs em tempo real"
            echo "  status    - Mostrar status dos containers"
            echo "  help      - Mostrar esta ajuda"
            ;;
        *)
            log_error "Comando inválido: $1"
            echo "Use: $0 help"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"