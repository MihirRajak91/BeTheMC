"""
MongoDB database connection and utilities.
"""
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING
from pymongo.errors import ConnectionFailure

from src.bethemc.config import settings


class MongoDB:
    """MongoDB connection manager."""
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB and initialize indexes."""
        if not settings.MONGODB_URL:
            raise ValueError("MONGODB_URL is not set in settings")

        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]
        
        # Test the connection
        try:
            await cls.client.admin.command('ping')
            print("✅ Connected to MongoDB")
        except ConnectionFailure as e:
            print("❌ Could not connect to MongoDB")
            raise e

        # Initialize indexes
        await cls._create_indexes()

    @classmethod
    async def _create_indexes(cls):
        """Create necessary indexes for collections."""
        # User collection indexes
        await cls.db.users.create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="unique_email"),
            IndexModel([("username", ASCENDING)], unique=True, name="unique_username"),
            IndexModel([("created_at", ASCENDING)], name="created_at_idx"),
        ])

    @classmethod
    async def close(cls):
        """Close the MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("✅ Closed MongoDB connection")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not cls.db:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db


# Create a single instance
mongodb = MongoDB()
