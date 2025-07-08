"""
Simple Database Service - Easy database operations!

This file handles ALL database operations in a simple, clear way.
No complex document models or adapters - just simple database operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import uuid4

from ..models.simple_models import GameState, Player, Story, Choice, Memory, GameProgression
from .connection import get_database
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SimpleDatabaseService:
    """
    Simple Database Service - handles all database operations!
    
    What this class does:
    1. Saves and loads game states
    2. Manages player data
    3. Handles save files
    4. Does it all in a simple, clear way!
    
    No complex document models - just simple dictionaries and objects.
    """
    
    def __init__(self):
        """Initialize the simple database service."""
        self.database: Optional[AsyncIOMotorDatabase] = None
        logger.info("Simple Database Service initialized!")
    
    async def _get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection (connects if needed)."""
        if self.database is None:
            self.database = await get_database()
        return self.database
    
    async def save_player(self, player: Player) -> bool:
        """
        Save a player to the database.
        
        Simple: Just convert player to dict and save it.
        """
        try:
            db = await self._get_database()
            players_collection = db[settings.MONGODB_COLLECTION_PLAYERS]
            
            # Convert player to simple dictionary
            player_data = {
                "player_id": player.id,
                "name": player.name,
                "personality_traits": player.personality_traits,
                "updated_at": datetime.utcnow()
            }
            
            # Save player (replace if exists, create if new)
            await players_collection.replace_one(
                {"player_id": player.id},
                player_data,
                upsert=True
            )
            
            logger.info(f"✅ Saved player: {player.name} (ID: {player.id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save player {player.id}: {e}")
            return False
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """
        Get a player from the database.
        
        Simple: Find player by ID and convert back to Player object.
        """
        try:
            db = await self._get_database()
            players_collection = db[settings.MONGODB_COLLECTION_PLAYERS]
            
            # Find player in database
            player_data = await players_collection.find_one({"player_id": player_id})
            if not player_data:
                logger.info(f"No player found with ID: {player_id}")
                return None
            
            # Convert back to Player object
            player = Player(
                id=player_data["player_id"],
                name=player_data["name"],
                personality_traits=player_data["personality_traits"]
            )
            
            logger.info(f"✅ Found player: {player.name}")
            return player
            
        except Exception as e:
            logger.error(f"❌ Failed to get player {player_id}: {e}")
            return None
    
    async def save_game_state(self, game_state: GameState) -> bool:
        """
        Save a complete game state to the database.
        
        Simple: Convert everything to dictionaries and save.
        """
        try:
            db = await self._get_database()
            games_collection = db[settings.MONGODB_COLLECTION_GAMES]
            
            # First save the player
            await self.save_player(game_state.player)
            
            # Convert game state to simple dictionary
            game_data = {
                "player_id": game_state.player.id,
                
                # Current story
                "current_story": {
                    "id": game_state.current_story.id,
                    "title": game_state.current_story.title,
                    "content": game_state.current_story.content,
                    "location": game_state.current_story.location
                },
                
                # Available choices
                "available_choices": [
                    {
                        "id": choice.id,
                        "text": choice.text,
                        "effects": choice.effects
                    }
                    for choice in game_state.available_choices
                ],
                
                # Memories
                "memories": [
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "memory_type": memory.memory_type,
                        "timestamp": memory.timestamp
                    }
                    for memory in game_state.memories
                ],
                
                # Game progression
                "progression": {
                    "current_location": game_state.progression.current_location,
                    "completed_events": game_state.progression.completed_events,
                    "relationships": game_state.progression.relationships,
                    "inventory": game_state.progression.inventory
                },
                
                # Metadata
                "last_updated": datetime.utcnow()
            }
            
            # Save game state (replace if exists, create if new)
            await games_collection.replace_one(
                {"player_id": game_state.player.id},
                game_data,
                upsert=True
            )
            
            logger.info(f"✅ Saved game state for: {game_state.player.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save game state for {game_state.player.id}: {e}")
            return False
    
    async def get_game_state(self, player_id: str) -> Optional[GameState]:
        """
        Get a complete game state from the database.
        
        Simple: Find game data and convert back to GameState object.
        """
        try:
            db = await self._get_database()
            games_collection = db[settings.MONGODB_COLLECTION_GAMES]
            
            # Find game data in database
            game_data = await games_collection.find_one({"player_id": player_id})
            if not game_data:
                logger.info(f"No game state found for player: {player_id}")
                return None
            
            # Get player data
            player = await self.get_player(player_id)
            if not player:
                logger.error(f"Player not found: {player_id}")
                return None
            
            # Convert back to GameState object
            game_state = GameState(
                player=player,
                
                # Current story
                current_story=Story(
                    id=game_data["current_story"]["id"],
                    title=game_data["current_story"]["title"],
                    content=game_data["current_story"]["content"],
                    location=game_data["current_story"]["location"]
                ),
                
                # Available choices
                available_choices=[
                    Choice(
                        id=choice_data["id"],
                        text=choice_data["text"],
                        effects=choice_data["effects"]
                    )
                    for choice_data in game_data["available_choices"]
                ],
                
                # Memories
                memories=[
                    Memory(
                        id=memory_data["id"],
                        content=memory_data["content"],
                        memory_type=memory_data["memory_type"],
                        timestamp=memory_data["timestamp"]
                    )
                    for memory_data in game_data["memories"]
                ],
                
                # Game progression
                progression=GameProgression(
                    current_location=game_data["progression"]["current_location"],
                    completed_events=game_data["progression"]["completed_events"],
                    relationships=game_data["progression"]["relationships"],
                    inventory=game_data["progression"]["inventory"]
                )
            )
            
            logger.info(f"✅ Retrieved game state for: {player.name}")
            return game_state
            
        except Exception as e:
            logger.error(f"❌ Failed to get game state for {player_id}: {e}")
            return None
    
    async def save_game(self, game_state: GameState, save_name: str) -> str:
        """
        Save a game to the saves collection.
        
        Simple: Copy current game state and save it with a name.
        """
        try:
            db = await self._get_database()
            saves_collection = db[settings.MONGODB_COLLECTION_SAVES]
            
            # Generate unique save ID
            save_id = str(uuid4())
            
            # Create save data (copy of current game state)
            save_data = {
                "save_id": save_id,
                "player_id": game_state.player.id,
                "save_name": save_name,
                "created_at": datetime.utcnow(),
                
                # Copy all the game data
                "player_name": game_state.player.name,
                "personality_traits": game_state.player.personality_traits,
                
                "current_story": {
                    "id": game_state.current_story.id,
                    "title": game_state.current_story.title,
                    "content": game_state.current_story.content,
                    "location": game_state.current_story.location
                },
                
                "available_choices": [
                    {
                        "id": choice.id,
                        "text": choice.text,
                        "effects": choice.effects
                    }
                    for choice in game_state.available_choices
                ],
                
                "memories": [
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "memory_type": memory.memory_type,
                        "timestamp": memory.timestamp
                    }
                    for memory in game_state.memories
                ],
                
                "progression": {
                    "current_location": game_state.progression.current_location,
                    "completed_events": game_state.progression.completed_events,
                    "relationships": game_state.progression.relationships,
                    "inventory": game_state.progression.inventory
                }
            }
            
            # Save to database
            await saves_collection.insert_one(save_data)
            
            logger.info(f"✅ Saved game '{save_name}' for {game_state.player.name} (Save ID: {save_id})")
            return save_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save game for {game_state.player.id}: {e}")
            raise
    
    async def load_game(self, player_id: str, save_id: str) -> Optional[GameState]:
        """
        Load a saved game from the saves collection.
        
        Simple: Find the save and convert back to GameState.
        """
        try:
            db = await self._get_database()
            saves_collection = db[settings.MONGODB_COLLECTION_SAVES]
            
            # Find the save
            save_data = await saves_collection.find_one({
                "save_id": save_id,
                "player_id": player_id
            })
            
            if not save_data:
                logger.info(f"No save found: {save_id} for player {player_id}")
                return None
            
            # Convert save data back to GameState
            player = Player(
                id=save_data["player_id"],
                name=save_data["player_name"],
                personality_traits=save_data["personality_traits"]
            )
            
            game_state = GameState(
                player=player,
                
                current_story=Story(
                    id=save_data["current_story"]["id"],
                    title=save_data["current_story"]["title"],
                    content=save_data["current_story"]["content"],
                    location=save_data["current_story"]["location"]
                ),
                
                available_choices=[
                    Choice(
                        id=choice_data["id"],
                        text=choice_data["text"],
                        effects=choice_data["effects"]
                    )
                    for choice_data in save_data["available_choices"]
                ],
                
                memories=[
                    Memory(
                        id=memory_data["id"],
                        content=memory_data["content"],
                        memory_type=memory_data["memory_type"],
                        timestamp=memory_data["timestamp"]
                    )
                    for memory_data in save_data["memories"]
                ],
                
                progression=GameProgression(
                    current_location=save_data["progression"]["current_location"],
                    completed_events=save_data["progression"]["completed_events"],
                    relationships=save_data["progression"]["relationships"],
                    inventory=save_data["progression"]["inventory"]
                )
            )
            
            logger.info(f"✅ Loaded save '{save_data['save_name']}' for {player.name}")
            return game_state
            
        except Exception as e:
            logger.error(f"❌ Failed to load save {save_id} for player {player_id}: {e}")
            return None
    
    async def get_player_saves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all saves for a player.
        
        Simple: Find all saves and return basic info about each one.
        """
        try:
            db = await self._get_database()
            saves_collection = db[settings.MONGODB_COLLECTION_SAVES]
            
            # Find all saves for this player
            saves_cursor = saves_collection.find({"player_id": player_id})
            saves = []
            
            async for save_data in saves_cursor:
                saves.append({
                    "save_id": save_data["save_id"],
                    "save_name": save_data["save_name"],
                    "created_at": save_data["created_at"],
                    "player_name": save_data["player_name"],
                    "current_location": save_data["progression"]["current_location"]
                })
            
            # Sort by creation date (newest first)
            saves.sort(key=lambda x: x["created_at"], reverse=True)
            
            logger.info(f"✅ Found {len(saves)} saves for player {player_id}")
            return saves
            
        except Exception as e:
            logger.error(f"❌ Failed to get saves for player {player_id}: {e}")
            return []


# Simple function to get the database service
def get_simple_database_service() -> SimpleDatabaseService:
    """Get the simple database service instance."""
    return SimpleDatabaseService()


# 🎯 SIMPLE EXPLANATION:
#
# This database service does 5 main things:
# 1. save_player() - Save player info
# 2. save_game_state() - Save current game
# 3. get_game_state() - Load current game
# 4. save_game() - Create save file
# 5. load_game() - Load save file
# 6. get_player_saves() - List all saves
#
# Everything is just simple dictionaries - no complex document models! 