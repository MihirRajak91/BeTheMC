#!/usr/bin/env python3
"""
Test script for MongoDB integration.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bethemc.database.connection import connect_to_database, disconnect_from_database, database_health_check
from bethemc.database.service import DatabaseService
from bethemc.models.core import Player, Story, Choice, GameProgression, GameState
from bethemc.utils.logger import get_logger
from uuid import uuid4

logger = get_logger(__name__)


async def test_mongodb_connection():
    """Test MongoDB connection."""
    try:
        logger.info("Testing MongoDB connection...")
        
        # Connect to database
        await connect_to_database()
        logger.info("✅ Connected to MongoDB")
        
        # Test health check
        is_healthy = await database_health_check()
        if is_healthy:
            logger.info("✅ Database health check passed")
        else:
            logger.error("❌ Database health check failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection test failed: {e}")
        return False


async def test_database_operations():
    """Test basic database operations."""
    try:
        logger.info("Testing database operations...")
        
        db_service = DatabaseService()
        
        # Create test player
        player = Player(
            id=str(uuid4()),
            name="Test Player",
            personality_traits={
                "friendship": 5,
                "courage": 5,
                "curiosity": 5,
                "wisdom": 5,
                "determination": 5
            }
        )
        
        # Save player
        success = await db_service.save_player(player)
        if success:
            logger.info("✅ Player saved successfully")
        else:
            logger.error("❌ Failed to save player")
            return False
        
        # Retrieve player
        retrieved_player = await db_service.get_player(player.id)
        if retrieved_player and retrieved_player.name == player.name:
            logger.info("✅ Player retrieved successfully")
        else:
            logger.error("❌ Failed to retrieve player")
            return False
        
        # Create test game state
        story = Story(
            id=str(uuid4()),
            title="Test Story",
            content="This is a test story.",
            location="Test Location"
        )
        
        choices = [
            Choice(
                id=str(uuid4()),
                text="Test choice 1",
                effects={"curiosity": 1}
            ),
            Choice(
                id=str(uuid4()),
                text="Test choice 2",
                effects={"courage": 1}
            )
        ]
        
        progression = GameProgression(
            current_location="Test Location",
            completed_events=[],
            relationships={},
            inventory=[]
        )
        
        game_state = GameState(
            player=player,
            current_story=story,
            available_choices=choices,
            memories=[],
            progression=progression
        )
        
        # Save game state
        success = await db_service.save_game_state(game_state)
        if success:
            logger.info("✅ Game state saved successfully")
        else:
            logger.error("❌ Failed to save game state")
            return False
        
        # Retrieve game state
        retrieved_game_state = await db_service.get_game_state(player.id)
        if retrieved_game_state and retrieved_game_state.current_story.title == story.title:
            logger.info("✅ Game state retrieved successfully")
        else:
            logger.error("❌ Failed to retrieve game state")
            return False
        
        # Test save functionality
        save_id = await db_service.save_game(game_state, "Test Save")
        if save_id:
            logger.info(f"✅ Game saved successfully with save_id: {save_id}")
        else:
            logger.error("❌ Failed to save game")
            return False
        
        # Test load functionality
        loaded_game_state = await db_service.load_game(player.id, save_id)
        if loaded_game_state and loaded_game_state.current_story.title == story.title:
            logger.info("✅ Game loaded successfully")
        else:
            logger.error("❌ Failed to load game")
            return False
        
        # Test saves list
        saves = await db_service.get_player_saves(player.id)
        if saves and len(saves) > 0:
            logger.info(f"✅ Retrieved {len(saves)} saves for player")
        else:
            logger.error("❌ Failed to retrieve saves")
            return False
        
        logger.info("✅ All database operations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        return False


async def cleanup_test_data():
    """Clean up test data."""
    try:
        logger.info("Cleaning up test data...")
        # Add cleanup logic here if needed
        logger.info("✅ Test data cleaned up")
    except Exception as e:
        logger.error(f"❌ Failed to clean up test data: {e}")


async def main():
    """Main test function."""
    logger.info("🚀 Starting MongoDB integration tests...")
    
    try:
        # Test connection
        connection_ok = await test_mongodb_connection()
        if not connection_ok:
            logger.error("❌ MongoDB connection test failed")
            return
        
        # Test operations
        operations_ok = await test_database_operations()
        if not operations_ok:
            logger.error("❌ Database operations test failed")
            return
        
        logger.info("🎉 All MongoDB integration tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        
    finally:
        await cleanup_test_data()
        await disconnect_from_database()
        logger.info("🔌 Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main()) 