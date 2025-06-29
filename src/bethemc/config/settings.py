"""
Application settings and configuration.
"""
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pathlib import Path
import secrets
import os

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "BeTheMC"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://192.168.1.68:27017"  # MongoDB connection string
    MONGODB_DB: str = "bethemc"  # Database name
    MONGODB_DB_NAME: str = "bethemc"  # Alias for compatibility with existing code
    MONGODB_TIMEOUT_MS: int = 5000  # 5 seconds
    
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
    
    # Email (Optional)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            # This allows using environment variables to override settings
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

# Create directories if they don't exist
os.makedirs("data/saves", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)

# Global settings instance
settings = Settings()
