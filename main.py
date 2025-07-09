# main.py
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
import asyncio

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importa o seu agente principal
from src.agents.agent import root_agent

# --- Modelos de Dados para a API ---
class ConverseRequest(BaseModel):
    """Define o corpo da requisição para o endpoint de conversa."""
    message: str
    session_id: str | None = None

class ConverseResponse(BaseModel):
    """Define o corpo da resposta do endpoint de conversa."""
    response: str
    session_id: str

# --- Criação da Aplicação FastAPI ---
app = FastAPI(
    title="Jira Agent API",
    description="API para interagir com o Jira Agent usando o Google ADK.",
    version="1.1.0",
)

# --- Configuração do Runner ---
runner = InMemoryRunner(agent=root_agent)

@app.post("/converse", response_model=ConverseResponse, summary="Endpoint de Conversa com o Agente")
async def converse(request: ConverseRequest):
    """
    Envia uma mensagem para o agente e recebe sua resposta.
    Gerencia a sessão de forma automática.
    """
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "user"  # Pode ser um ID de usuário fixo ou dinâmico

    # Converte a mensagem de string para o formato esperado pelo ADK
    new_message = genai_types.Content(parts=[genai_types.Part(text=request.message)])

    # Executa o agente de forma assíncrona
    events_generator = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    )

    final_response = ""
    for event in events_generator:
        if event.type == "model_response":
            final_response = event.content.parts[0].text

    return ConverseResponse(response=final_response, session_id=session_id)

@app.get("/", summary="Endpoint de Verificação de Saúde")
async def root():
    """Verifica se o servidor está online."""
    return {"message": "Jira Agent API está online. Use o endpoint /converse para interagir."}

# --- Ponto de Entrada para Execução ---
if __name__ == "__main__":
    # Executa o servidor com uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
