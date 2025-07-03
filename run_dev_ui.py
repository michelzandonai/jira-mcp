"""
Script para iniciar o servidor de desenvolvimento do Google ADK (com a Dev-UI).

Este script contorna problemas onde o comando 'google-adk serve' não é encontrado,
iniciando o servidor web 'uvicorn' programaticamente.
"""
import uvicorn
from google.adk.server import app
from src import agent  # Importar o módulo do agente é crucial para que o servidor o descubra.

if __name__ == "__main__":
    print("Iniciando servidor de desenvolvimento do ADK...")
    print("Acesse a interface de chat em: http://127.0.0.1:8000/dev-ui/")
    
    # O servidor do ADK descobre automaticamente a instância do 'Agent'
    # que está no escopo global do módulo 'agent' importado.
    uvicorn.run(app, host="127.0.0.1", port=8000) 