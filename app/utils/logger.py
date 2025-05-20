import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(name: str = 'briefed', 
                log_level: str = 'INFO',
                log_file: Optional[str] = 'logs/app.log') -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers
    
    Args:
        name: Logger name
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None to disable file logging)
    """
    logger = logging.getLogger(name)
    
    try:
        level = getattr(logging, log_level.upper())
        logger.setLevel(level)
    except AttributeError:
        logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if enabled)
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5 MB
                backupCount=3,
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.error(f"Failed to setup file logging: {e}")

    return logger

logger = setup_logger()