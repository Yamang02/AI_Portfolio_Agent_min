"""Structured logging configuration"""

import logging
import json
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields from extra
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_ip"):
            log_data["user_ip"] = record.user_ip
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        
        return json.dumps(log_data)


def configure_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(JsonFormatter())
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO)


def get_logger(name: str) -> logging.LoggerAdapter:
    """
    Get a logger with structured context support
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        LoggerAdapter for structured logging
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, {})


def log_security_event(
    event_type: str,
    severity: str = "INFO",
    message: str = "",
    **context: Any
) -> None:
    """
    Log security-related events
    
    Args:
        event_type: Type of security event (rate_limit, injection_attempt, etc.)
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        message: Event description
        **context: Additional context data
    """
    logger = get_logger("security")
    extra = {
        "event_type": event_type,
        **context
    }
    
    log_method = getattr(logger, severity.lower(), logger.info)
    log_method(f"Security Event: {event_type} - {message}", extra=extra)
