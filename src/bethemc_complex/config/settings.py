"""
Application settings and configuration.
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
    MONGODB_URL: str = "mongodb://admin:password@localhost:27017/bethemc?authSource=admin"
    MONGODB_DATABASE: str = "bethemc"
    MONGODB_COLLECTION_PLAYERS: str = "players"
    MONGODB_COLLECTION_GAMES: str = "game_states"
    MONGODB_COLLECTION_SAVES: str = "saves"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
