"""
Logging utilities
"""
import logging
import logging.config
import sys
from typing import Optional
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup application logging configuration
    """
    level = log_level or settings.log_level
    
    # Create logs directory if it doesn't exist
    # Always create the logs directory for default log files
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # If a specific log file is provided, ensure its directory exists
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "detailed",
                "filename": log_file or "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": log_file or "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "app": {
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        }
    }
    
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    """
    return logging.getLogger(name)


class RequestLogger:
    """
    Context manager for request logging
    """
    
    def __init__(self, logger: logging.Logger, request_id: str, method: str, path: str):
        self.logger = logger
        self.request_id = request_id
        self.method = method
        self.path = path
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.info(
            f"Request {self.request_id}: {self.method} {self.path} started"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type:
            self.logger.error(
                f"Request {self.request_id}: {self.method} {self.path} failed "
                f"after {duration:.4f}s - {exc_val}"
            )
        else:
            self.logger.info(
                f"Request {self.request_id}: {self.method} {self.path} completed "
                f"in {duration:.4f}s"
            )
