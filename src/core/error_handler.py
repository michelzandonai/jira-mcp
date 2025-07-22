"""
Error Handler centralizado para Jira Agent.

Este módulo fornece tratamento padronizado de erros para
todas as camadas da aplicação.
"""

import logging
from typing import Tuple, Optional, Any, Dict
from enum import Enum

from .exceptions import (
    JiraAgentError,
    JiraConnectionError, 
    JiraAuthenticationError,
    ProjectNotFoundError,
    IssueNotFoundError,
    ValidationError,
    PermissionError as JiraPermissionError,
    ToolExecutionError
)

logger = logging.getLogger(__name__)




class ErrorSeverity(Enum):
    """Níveis de severidade dos erros."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorHandler:
    """
    Handler centralizado para tratamento de erros.
    
    Fornece métodos padronizados para diferentes contextos
    da aplicação com logging e formatação consistentes.
    """
    
    @staticmethod
    def handle_tool_error(
        error: Exception, 
        tool_name: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Trata erros em ferramentas ADK.
        
        Args:
            error: A exceção ocorrida
            tool_name: Nome da ferramenta onde ocorreu o erro
            context: Contexto adicional sobre o erro
            
        Returns:
            str: Mensagem de erro formatada para o usuário
        """
        error_msg = ErrorHandler._format_error_for_user(error)
        
        # Log do erro para debugging
        logger.error(
            f"Erro na ferramenta '{tool_name}': {str(error)}", 
            extra={
                "tool_name": tool_name,
                "error_type": type(error).__name__,
                "context": context,
                "severity": ErrorHandler._get_error_severity(error).value
            }
        )
        
        return f"❌ {error_msg}"
    
    @staticmethod
    def handle_service_error(
        error: Exception, 
        service_name: str, 
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trata erros em serviços de domínio.
        
        Args:
            error: A exceção ocorrida
            service_name: Nome do serviço onde ocorreu o erro
            operation: Operação que estava sendo executada
            context: Contexto adicional sobre o erro
            
        Raises:
            JiraAgentError: Sempre relança como exceção apropriada
        """
        # Log do erro
        logger.error(
            f"Erro no serviço '{service_name}' durante '{operation}': {str(error)}", 
            extra={
                "service_name": service_name,
                "operation": operation,
                "error_type": type(error).__name__,
                "context": context,
                "severity": ErrorHandler._get_error_severity(error).value
            }
        )
        
        # Relançar como exceção apropriada
        if isinstance(error, JiraAgentError):
            raise error
        else:
            raise JiraConnectionError(f"Falha na operação '{operation}': {str(error)}")
    
    @staticmethod
    def handle_infrastructure_error(
        error: Exception, 
        component: str, 
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        Trata erros na camada de infraestrutura.
        
        Args:
            error: A exceção ocorrida
            component: Componente de infraestrutura onde ocorreu o erro
            operation: Operação que estava sendo executada
            context: Contexto adicional sobre o erro
            
        Returns:
            Tuple[Optional[Any], Optional[str]]: (resultado, mensagem_erro)
        """
        error_msg = ErrorHandler._format_error_for_user(error)
        
        # Log do erro
        logger.error(
            f"Erro na infraestrutura '{component}' durante '{operation}': {str(error)}", 
            extra={
                "component": component,
                "operation": operation,
                "error_type": type(error).__name__,
                "context": context,
                "severity": ErrorHandler._get_error_severity(error).value
            }
        )
        
        return None, error_msg
    
    @staticmethod
    def handle_api_error(
        error: Exception, 
        endpoint: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trata erros em endpoints da API.
        
        Args:
            error: A exceção ocorrida
            endpoint: Endpoint onde ocorreu o erro
            context: Contexto adicional sobre o erro
            
        Returns:
            Dict[str, Any]: Resposta de erro padronizada para API
        """
        error_msg = ErrorHandler._format_error_for_user(error)
        severity = ErrorHandler._get_error_severity(error)
        
        # Log do erro
        logger.error(
            f"Erro na API '{endpoint}': {str(error)}", 
            extra={
                "endpoint": endpoint,
                "error_type": type(error).__name__,
                "context": context,
                "severity": severity.value
            }
        )
        
        # Determinar status code HTTP
        status_code = 500
        if isinstance(error, (ProjectNotFoundError, IssueNotFoundError)):
            status_code = 404
        elif isinstance(error, (ValidationError, ValueError)):
            status_code = 400
        elif isinstance(error, (JiraAuthenticationError, JiraPermissionError)):
            status_code = 403
        
        return {
            "error": {
                "message": error_msg,
                "type": type(error).__name__,
                "severity": severity.value,
                "code": getattr(error, 'error_code', 'UNKNOWN_ERROR')
            },
            "status_code": status_code
        }
    
    @staticmethod
    def _format_error_for_user(error: Exception) -> str:
        """
        Formata erro para exibição ao usuário.
        
        Args:
            error: A exceção a ser formatada
            
        Returns:
            str: Mensagem de erro amigável ao usuário
        """
        if isinstance(error, JiraAgentError):
            return error.message
        elif isinstance(error, ValueError):
            return str(error)
        else:
            return f"Erro inesperado: {str(error)}"
    
    @staticmethod
    def _get_error_severity(error: Exception) -> ErrorSeverity:
        """
        Determina a severidade do erro.
        
        Args:
            error: A exceção a ser analisada
            
        Returns:
            ErrorSeverity: Nível de severidade
        """
        if isinstance(error, (JiraAuthenticationError, JiraConnectionError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (ProjectNotFoundError, IssueNotFoundError)):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, (ValidationError, ValueError)):
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.HIGH
    
    @staticmethod
    def create_validation_error(field: str, value: str, reason: str) -> ValidationError:
        """
        Cria um erro de validação padronizado.
        
        Args:
            field: Campo que falhou na validação
            value: Valor que causou o erro
            reason: Motivo da falha
            
        Returns:
            ValidationError: Exceção de validação formatada
        """
        return ValidationError(field, value, reason)
    
    @staticmethod
    def create_tool_execution_error(tool_name: str, message: str) -> ToolExecutionError:
        """
        Cria um erro de execução de ferramenta padronizado.
        
        Args:
            tool_name: Nome da ferramenta
            message: Mensagem de erro
            
        Returns:
            ToolExecutionError: Exceção de execução de ferramenta
        """
        return ToolExecutionError(tool_name, message)
    
    @staticmethod
    def log_warning(
        message: str, 
        component: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra um aviso padronizado.
        
        Args:
            message: Mensagem do aviso
            component: Componente que gerou o aviso
            context: Contexto adicional
        """
        logger.warning(
            f"Aviso em '{component}': {message}",
            extra={
                "component": component,
                "context": context,
                "level": "warning"
            }
        )
    
    @staticmethod
    def log_info(
        message: str, 
        component: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra uma informação padronizada.
        
        Args:
            message: Mensagem informativa
            component: Componente que gerou a informação
            context: Contexto adicional
        """
        logger.info(
            f"Info em '{component}': {message}",
            extra={
                "component": component,
                "context": context,
                "level": "info"
            }
        )