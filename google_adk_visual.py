#!/usr/bin/env python3
"""
Google ADK Visual - Interface visual para Jira Agent
Utilizando apenas o Google ADK sem MCP ou Docker
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

def setup_environment():
    """Configurar variáveis de ambiente para Google ADK."""
    print("🔧 Configurando ambiente Google ADK...")
    
    # Verificar configuração do Vertex AI
    use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
    
    if use_vertexai:
        # Configuração para Vertex AI
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        region = os.getenv("GOOGLE_CLOUD_REGION")
        
        if not project:
            print("❌ GOOGLE_CLOUD_PROJECT não encontrado para Vertex AI!")
            return False
            
        print(f"✅ Vertex AI configurado - Projeto: {project}")
        if region:
            print(f"✅ Região: {region}")
    else:
        # Configuração para Google AI Studio
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada!")
            print("📋 Configure com: export GOOGLE_API_KEY='sua_key'")
            print("🔗 Obtenha sua chave em: https://aistudio.google.com/apikey")
            return False
        
        print(f"✅ Google AI Studio configurado: {api_key[:10]}...")
    
    return True

def create_visual_interface():
    """Criar interface visual usando Google ADK."""
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI importado com sucesso")
        
        # Configurar API key
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        # Listar modelos disponíveis
        print("\n📋 Modelos disponíveis:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  • {model.name}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar Google Generative AI: {e}")
        print("💡 Instale com: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_simple_chat_interface():
    """Criar interface de chat simples."""
    try:
        import google.generativeai as genai
        
        # Usar modelo configurado no .env
        model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)
        print(f"🤖 Usando modelo: {model_name}")
        
        print("\n🤖 Chat com Gemini iniciado!")
        print("Digite 'sair' para finalizar\n")
        
        while True:
            user_input = input("Você: ")
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("👋 Tchau!")
                break
            
            try:
                response = model.generate_content(user_input)
                print(f"Gemini: {response.text}\n")
            except Exception as e:
                print(f"❌ Erro na resposta: {e}\n")
                
    except Exception as e:
        print(f"❌ Erro ao criar chat: {e}")

def main():
    """Função principal."""
    print("🚀 Google ADK Visual - Jira Agent")
    print("=" * 40)
    
    # Configurar ambiente
    if not setup_environment():
        return
    
    # Criar interface visual
    if not create_visual_interface():
        return
    
    # Iniciar chat
    create_simple_chat_interface()

if __name__ == "__main__":
    main()