# Agente Especialista em Criar Issues do Jira
from .agents.issue_creator_agent import issue_creator_agent

# O ADK procura por uma variável chamada 'root_agent'
root_agent = issue_creator_agent 