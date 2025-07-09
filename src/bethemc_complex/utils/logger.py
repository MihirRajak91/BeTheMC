"""
📝 Logging Utilities - BeTheMC Complex Architecture

This module provides centralized logging configuration for the complex
architecture. It sets up structured logging with both console and file
output, configurable log levels, and consistent formatting across all
application layers.

🏗️ Logging Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    Application Layers                       │
    │  • API Layer (FastAPI routes)                             │
    │  • Service Layer (Business logic)                         │
    │  • Database Layer (MongoDB operations)                    │
    │  • AI Layer (Story generation)                            │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                    Logger Factory                          │
    │  • setup_logger(): Creates configured loggers              │
    │  • get_logger(): Alias for setup_logger                   │
    │  • Configurable log levels and formats                     │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                    Output Handlers                          │
    │  • Console Handler: Real-time development logging          │
    │  • File Handler: Persistent log storage                    │
    │  • Structured Format: Timestamp, module, level, message   │
    └─────────────────────────────────────────────────────────────┘

🎯 Key Features:
    • Centralized logging configuration
    • Dual output (console + file)
    • Configurable log levels per module
    • Structured log formatting
    • Automatic log file rotation
    • Integration with application config

🔧 Log Levels:
    • DEBUG: Detailed debugging information
    • INFO: General application information
    • WARNING: Warning messages for potential issues
    • ERROR: Error messages for handled exceptions
    • CRITICAL: Critical errors requiring immediate attention

📋 Usage Examples:
    from bethemc_complex.utils.logger import setup_logger
    
    # Create logger for a module
    logger = setup_logger(__name__)
    
    # Log different levels
    logger.debug("Detailed debugging info")
    logger.info("Application started successfully")
    logger.warning("Database connection slow")
    logger.error("Failed to process request")
    logger.critical("System shutdown required")
    
    # With custom level
    logger = setup_logger("my_module", level="DEBUG")

⚠️ Important Notes:
    • Log files are stored in logs/game.log
    • Console output for development, file for production
    • Log levels can be configured via environment variables
    • All loggers use consistent formatting
    • File logging includes automatic directory creation
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