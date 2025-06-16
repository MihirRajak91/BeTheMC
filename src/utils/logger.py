"""
Logging configuration for the game.
"""
import logging
import os
from pathlib import Path
from .config import config

def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with the specified name."""
    logger = logging.getLogger(name)
    
    # Get logging configuration
    log_level = config.get('logging.level', 'INFO')
    log_format = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('logging.file', 'logs/game.log')
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # Set log level
    logger.setLevel(getattr(logging, log_level))
    
    return logger

# Create a default logger
logger = setup_logger('betheMC') 