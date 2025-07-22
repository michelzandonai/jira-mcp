"""
FastAPI application for Jira Agent.

This module provides a REST API interface for interacting with the Jira Agent
using the Google ADK framework.
"""

import logging
import uuid
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

from ..core.config import get_settings
from ..agents.jira_agent import jira_agent

# Configure logging
from ..core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


class ConverseRequest(BaseModel):
    """Request model for agent conversation."""
    
    message: str
    session_id: Optional[str] = None


class ConverseResponse(BaseModel):
    """Response model for agent conversation."""
    
    response: str
    session_id: str


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="API para interagir com o Jira usando um agente inteligente baseado no Google ADK",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    if settings.cors_origins != "*":
        origins = [origin.strip() for origin in settings.cors_origins.split(",")]
    else:
        origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize ADK runner
    runner = InMemoryRunner(agent=jira_agent)
    
    @app.get("/", summary="Verificação de Saúde")
    async def health_check():
        """Verifica se a API está funcionando."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        }
    
    @app.post("/converse", response_model=ConverseResponse, summary="Conversar com o Agente Jira")
    async def converse(request: ConverseRequest):
        """
        Envia uma mensagem para o agente Jira e recebe uma resposta.
        
        Este endpoint permite interagir com o agente Jira usando linguagem natural.
        O agente pode ajudar você a buscar projetos, criar issues e realizar outras operações do Jira.
        
        Exemplos do que você pode perguntar:
        - "Liste todos os projetos"
        - "Mostre-me detalhes do projeto DEMO"
        - "Crie uma tarefa no projeto DEMO com título 'Corrigir bug de login'"
        - "Busque projetos que contenham 'mobile'"
        """
        try:
            # Generate session ID if not provided
            session_id = request.session_id or str(uuid.uuid4())
            user_id = "api_user"  # Could be made dynamic with authentication
            
            # Convert message to ADK format
            new_message = genai_types.Content(
                parts=[genai_types.Part(text=request.message)]
            )
            
            # Run the agent
            events = runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            )
            
            # Extract the final response
            final_response = ""
            for event in events:
                if event.type == "model_response":
                    final_response = event.content.parts[0].text
            
            if not final_response:
                final_response = "Desculpe, não consegui processar sua solicitação. Por favor, tente novamente."
            
            logger.info(
                "Resposta do agente gerada com sucesso",
                extra={
                    "session_id": session_id,
                    "user_id": user_id,
                    "message_length": len(request.message),
                    "response_length": len(final_response),
                    "operation": "converse"
                }
            )
            
            return ConverseResponse(
                response=final_response,
                session_id=session_id
            )
            
        except Exception as e:
            from ..core.error_handler import ErrorHandler
            
            error_response = ErrorHandler.handle_api_error(
                error=e,
                endpoint="/converse",
                context={"session_id": session_id, "message_length": len(request.message)}
            )
            
            raise HTTPException(
                status_code=error_response["status_code"],
                detail=error_response["error"]["message"]
            )
    
    @app.get("/config", summary="Obter Configuração do Agente")
    async def get_config():
        """Obtém informações básicas de configuração sobre o agente."""
        return {
            "agent_name": "JiraAgent",
            "model": settings.google_model,
            "available_tools": [
                "search_projects",
                "get_project_details", 
                "create_issue"
            ],
            "environment": settings.environment
        }
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.auto_reload and settings.environment == "development",
        log_level=settings.log_level.lower()
    )