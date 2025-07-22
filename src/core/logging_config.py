"""
Configuração centralizada de logging para Jira Agent.

Este módulo configura o sistema de logging estruturado
para toda a aplicação.
"""

import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime

from .config import get_settings


class StructuredFormatter(logging.Formatter):
    """
    Formatter para logs estruturados em JSON.
    
    Converte registros de log em formato JSON estruturado
    com metadados consistentes.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log como JSON estruturado.
        
        Args:
            record: Registro de log do Python
            
        Returns:
            str: Log formatado como JSON
        """
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar campos extras se disponíveis
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)
        
        # Adicionar informações de exceção se disponível
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class SimpleFormatter(logging.Formatter):
    """
    Formatter simples para desenvolvimento.
    
    Formato legível para desenvolvimento local.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log de forma simples.
        
        Args:
            record: Registro de log do Python
            
        Returns:
            str: Log formatado de forma simples
        """
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Formato básico
        formatted = f"{timestamp} - {record.name} - {record.levelname} - {record.getMessage()}"
        
        # Adicionar exceção se disponível
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def configure_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Configura handlers, formatters e níveis de log
    baseado nas configurações da aplicação.
    """
    settings = get_settings()
    
    # Obter logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Limpar handlers existentes
    root_logger.handlers.clear()
    
    # Criar handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Escolher formatter baseado na configuração
    if settings.log_format.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = SimpleFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configurar loggers específicos
    _configure_specific_loggers()
    
    # Log inicial
    logger = logging.getLogger(__name__)
    logger.info(
        "Sistema de logging configurado",
        extra={
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "environment": settings.environment
        }
    )


def _configure_specific_loggers() -> None:
    """
    Configura loggers específicos para bibliotecas externas.
    
    Ajusta níveis de log para bibliotecas que são muito verbosas
    ou que precisam de configuração especial.
    """
    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Google ADK pode ser verboso
    logging.getLogger("google").setLevel(logging.INFO)
    logging.getLogger("google.adk").setLevel(logging.INFO)
    
    # Jira library
    logging.getLogger("jira").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para um componente específico.
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Registra uma mensagem com contexto estruturado.
    
    Args:
        logger: Logger a ser usado
        level: Nível do log (info, warning, error, etc.)
        message: Mensagem do log
        **context: Contexto adicional como chaves/valores
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=context)


class LoggerMixin:
    """
    Mixin para adicionar logging estruturado a classes.
    
    Fornece um logger configurado e métodos de conveniência
    para logging com contexto.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Obtém o logger para esta classe."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_info(self, message: str, **context: Any) -> None:
        """Registra uma mensagem de informação."""
        self.logger.info(message, extra=context)
    
    def log_warning(self, message: str, **context: Any) -> None:
        """Registra uma mensagem de aviso."""
        self.logger.warning(message, extra=context)
    
    def log_error(self, message: str, **context: Any) -> None:
        """Registra uma mensagem de erro."""
        self.logger.error(message, extra=context)
    
    def log_debug(self, message: str, **context: Any) -> None:
        """Registra uma mensagem de debug."""
        self.logger.debug(message, extra=context)