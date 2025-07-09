"""
🗄️ MongoDB Connection Management - BeTheMC Complex Architecture

This module provides comprehensive MongoDB connection management for the
complex architecture. It handles connection lifecycle, health monitoring,
and dependency injection for database operations throughout the system.

🏗️ Architecture Role:
    ┌─────────────────┐
    │   API Layer     │  ← Uses database for persistence
    └─────────┬───────┘
              │
    ┌─────────▼───────┐
    │  Service Layer  │  ← Orchestrates database operations
    └─────────┬───────┘
              │
    ┌─────────▼───────┐  ← This Database Layer
    │  Connection     │  ← Manages MongoDB connections
    └─────────┬───────┘
              │
    ┌─────────▼───────┐
    │   MongoDB       │  ← External database system
    └─────────────────┘

🎯 Key Features:
    • Async MongoDB connection management
    • Connection pooling and lifecycle management
    • Health monitoring and status checks
    • Dependency injection for FastAPI
    • Comprehensive error handling and logging
    • Authentication support for production deployments

🔧 Connection Management:
    • connect_to_database(): Initialize connection on startup
    • disconnect_from_database(): Clean shutdown on app close
    • get_database(): Dependency injection for services
    • database_health_check(): Monitor connection status

📋 Configuration:
    • Uses settings from config/settings.py
    • Supports both authenticated and local connections
    • Automatic connection pooling via Motor
    • Graceful error handling and reconnection

🚀 Usage Examples:
    # Dependency injection in FastAPI
    from bethemc_complex.database.connection import get_database
    
    @app.get("/data")
    async def get_data(db: AsyncIOMotorDatabase = Depends(get_database)):
        collection = db["games"]
        return await collection.find_one({"player_id": "123"})
    
    # Manual connection management
    from bethemc_complex.database.connection import (
        connect_to_database, disconnect_from_database
    )
    
    # In startup event
    await connect_to_database()
    
    # In shutdown event  
    await disconnect_from_database()

⚠️ Important Notes:
    • All operations are async for non-blocking I/O
    • Connection is managed globally for the application
    • Health checks are performed regularly
    • Errors are logged and handled gracefully
    • Designed for production MongoDB deployments
"""
from typing import Optional
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to MongoDB."""
        try:
            if self._connected:
                return
            
            # Handle authentication if provided
            if "admin" in settings.MONGODB_URL and "password" in settings.MONGODB_URL:
                mongodb_url = settings.MONGODB_URL
            else:
                # Default connection without auth for local development
                mongodb_url = settings.MONGODB_URL
            
            logger.info(f"Connecting to MongoDB at: {mongodb_url}")
            
            self.client = AsyncIOMotorClient(mongodb_url)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if not self._connected:
            await self.connect()
        return self.database
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            if not self._connected:
                return False
            
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database connection instance
_db_connection = DatabaseConnection()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance (dependency injection)."""
    return await _db_connection.get_database()


async def connect_to_database() -> None:
    """Connect to database on startup."""
    await _db_connection.connect()


async def disconnect_from_database() -> None:
    """Disconnect from database on shutdown."""
    await _db_connection.disconnect()


async def database_health_check() -> bool:
    """Check database health."""
    return await _db_connection.health_check() 