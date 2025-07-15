"""
⚙️ Application Configuration - BeTheMC Complex Architecture

This module provides centralized configuration management for the complex
architecture. It uses Pydantic Settings for type-safe configuration with
environment variable support, validation, and default values.

🏗️ Configuration Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    Environment Variables                   │
    │  • .env file                                              │
    │  • System environment variables                           │
    │  • Docker environment variables                           │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                    Pydantic Settings                       │
    │  • Type validation and conversion                          │
    │  • Default value management                                │
    │  • Environment variable mapping                            │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                    Application Layers                       │
    │  • API configuration (CORS, endpoints)                    │
    │  • Database configuration (MongoDB)                        │
    │  • Game configuration (locations, saves)                   │
    │  • AI configuration (LLM providers)                        │
    └─────────────────────────────────────────────────────────────┘

🎯 Configuration Categories:
    • Application Settings: Project name, version, debug mode
    • API Settings: CORS origins, endpoints, validation
    • Database Settings: MongoDB connection and collections
    • Game Settings: Starting locations, save directories
    • AI Settings: LLM providers, model configurations
    • Logging Settings: Log levels and output configuration

🔧 Environment Variables:
    • MONGODB_URL: Database connection string
    • MONGODB_DATABASE: Database name
    • BACKEND_CORS_ORIGINS: Allowed CORS origins
    • LOG_LEVEL: Application logging level
    • DEBUG: Enable debug mode
    • FRONTEND_URL: Frontend application URL

📋 Usage Examples:
    from bethemc_complex.config.settings import settings
    
    # Access configuration values
    database_url = settings.MONGODB_URL
    cors_origins = settings.BACKEND_CORS_ORIGINS
    save_directory = settings.SAVE_DIR
    
    # Use in FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )
    
    # Use in database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)

⚠️ Important Notes:
    • All settings are type-validated by Pydantic
    • Environment variables override defaults
    • .env file is automatically loaded
    • CORS origins support both string and list formats
    • Database settings include authentication support
"""
from pydantic import AnyHttpUrl, HttpUrl, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pathlib import Path
import os

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "BeTheMC"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Game Settings
    DEFAULT_STARTING_LOCATION: str = "Pallet Town"
    SAVE_DIR: str = "data/saves"
    
    # File Storage
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 5  # 5MB
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017/bethemc"
    MONGODB_DATABASE: str = "bethemc"
    MONGODB_COLLECTION_PLAYERS: str = "players"
    MONGODB_COLLECTION_GAMES: str = "game_states"
    MONGODB_COLLECTION_SAVES: str = "saves"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment

# Create settings instance
settings = Settings()
