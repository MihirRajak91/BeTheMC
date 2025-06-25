"""
Logging setup for the game.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with the specified name and level."""
    logger = logging.getLogger(name)
    
    # Set level from config if not specified
    if level is None:
        from .config import Config
        config = Config()
        level = config.get("logging.level", "INFO")
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(
        Path(__file__).parent.parent.parent.parent / "logs" / "game.log"
    )
    
    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

get_logger = setup_logger 