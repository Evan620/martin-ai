"""
Structured logging configuration using loguru.

Provides consistent logging across the application with file rotation
and structured JSON formatting for production environments.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.config.settings import get_settings


def setup_logger(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    json_format: bool = False,
) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        json_format: Use JSON formatting for structured logs
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    if json_format:
        logger.add(
            sys.stderr,
            level=level,
            serialize=True,  # JSON format
        )
    else:
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )
    
    # File handler with rotation
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            level=level,
            rotation="100 MB",  # Rotate when file reaches 100 MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
            serialize=json_format,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
    
    logger.info(f"Logger initialized with level: {level}")


def get_logger(name: str):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Initialize default logger
setup_logger()
