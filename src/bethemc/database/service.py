"""
🗄️ Simple Database Service for BeTheMC

This file handles ALL database operations in a simple, easy-to-understand way.
No complex patterns - just straightforward MongoDB operations!

What this service does:
- Save and load players
- Save and load game states  
- Handle save files
- Manage memories and personality updates

All with clear step-by-step comments!
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import get_database
from ..utils.logger import get_logger
from ..models.models import (
    Player, GameState, Story, Choice, Memory, GameProgression
)

logger = get_logger(__name__)


class SimpleDatabaseService:
    """
    🗄️ SIMPLE DATABASE SERVICE
    
    This class handles ALL database operations for the game.
    Everything is here in one place - no complex patterns!
    """
    
    def __init__(self):
        """Initialize the database service."""
        self.db = None
        self.players_collection: Optional[AsyncIOMotorCollection] = None
        self.games_collection: Optional[AsyncIOMotorCollection] = None
        self.saves_collection: Optional[AsyncIOMotorCollection] = None
        
        logger.info("🗄️ SimpleDatabaseService initialized")
    
    async def initialize(self):
        """
        🚀 INITIALIZE DATABASE COLLECTIONS
        
        Step 1: Get the database connection
        Step 2: Get references to our collections
        Step 3: Log that we're ready
        """
        try:
            self.db = get_database()
            self.players_collection = self.db.players
            self.games_collection = self.db.games  
            self.saves_collection = self.db.saves
            
            logger.info("✅ Database collections initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    # 👤 PLAYER OPERATIONS
    
    async def create_player(self, player: Player) -> str:
        """
        👤 CREATE A NEW PLAYER
        
        Step 1: Convert player to dictionary
        Step 2: Add creation timestamp
        Step 3: Insert into database
        Step 4: Return the player ID
        """
        try:
            logger.info(f"Creating new player: {player.name}")
            
            # Convert to dictionary and add metadata
            player_data = {
                "player_id": player.player_id,
                "name": player.name,
                "personality_traits": player.personality_traits,
                "created_at": datetime.utcnow(),
                "last_played": datetime.utcnow()
            }
            
            # Insert into database
            result = await self.players_collection.insert_one(player_data)
            
            if result.inserted_id:
                logger.info(f"✅ Player created successfully: {player.player_id}")
                return player.player_id
            else:
                raise Exception("Failed to insert player")
                
        except Exception as e:
            logger.error(f"❌ Error creating player: {e}")
            raise
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """
        👤 GET A PLAYER BY ID
        
        Step 1: Search database for player
        Step 2: If found, convert to Player object
        Step 3: Return player or None
        """
        try:
            logger.info(f"Fetching player: {player_id}")
            
            # Find player in database
            player_data = await self.players_collection.find_one({"player_id": player_id})
            
            if player_data:
                # Convert to Player object
                player = Player(
                    player_id=player_data["player_id"],
                    name=player_data["name"],
                    personality_traits=player_data["personality_traits"]
                )
                logger.info(f"✅ Player found: {player.name}")
                return player
            else:
                logger.info(f"❌ Player not found: {player_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching player: {e}")
            raise
    
    async def update_player_personality(self, player_id: str, trait: str, value: int) -> bool:
        """
        👤 UPDATE A PLAYER'S PERSONALITY TRAIT
        
        Step 1: Update the specific trait in database
        Step 2: Update last_played timestamp
        Step 3: Return success status
        """
        try:
            logger.info(f"Updating personality for {player_id}: {trait} = {value}")
            
            # Update personality trait
            result = await self.players_collection.update_one(
                {"player_id": player_id},
                {
                    "$set": {
                        f"personality_traits.{trait}": value,
                        "last_played": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Personality updated successfully")
                return True
            else:
                logger.warning(f"⚠️ No personality update made (player may not exist)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating personality: {e}")
            raise
    
    # 🎮 GAME STATE OPERATIONS
    
    async def save_game_state(self, game_state: GameState) -> bool:
        """
        🎮 SAVE A GAME STATE
        
        Step 1: Convert game state to dictionary
        Step 2: Add timestamps
        Step 3: Upsert (insert or update) in database
        Step 4: Return success status
        """
        try:
            logger.info(f"Saving game state for player: {game_state.player_id}")
            
            # Convert to dictionary
            game_data = {
                "player_id": game_state.player_id,
                "current_story": {
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
                        "text": memory.text,
                        "memory_type": memory.memory_type,
                        "timestamp": memory.timestamp
                    }
                    for memory in game_state.memories
                ],
                "game_progress": {
                    "current_location": game_state.game_progress.current_location,
                    "completed_events": game_state.game_progress.completed_events,
                    "relationships": game_state.game_progress.relationships,
                    "inventory": game_state.game_progress.inventory
                },
                "updated_at": datetime.utcnow()
            }
            
            # Upsert the game state
            result = await self.games_collection.replace_one(
                {"player_id": game_state.player_id},
                game_data,
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"✅ Game state saved successfully")
                return True
            else:
                logger.warning(f"⚠️ No game state changes made")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving game state: {e}")
            raise
    
    async def get_game_state(self, player_id: str) -> Optional[GameState]:
        """
        🎮 GET A GAME STATE BY PLAYER ID
        
        Step 1: Find game state in database
        Step 2: Convert to GameState object
        Step 3: Return game state or None
        """
        try:
            logger.info(f"Fetching game state for player: {player_id}")
            
            # Find game state
            game_data = await self.games_collection.find_one({"player_id": player_id})
            
            if game_data:
                # Convert to GameState object
                current_story = Story(
                    title=game_data["current_story"]["title"],
                    content=game_data["current_story"]["content"],
                    location=game_data["current_story"]["location"]
                )
                
                available_choices = [
                    Choice(
                        id=choice_data["id"],
                        text=choice_data["text"],
                        effects=choice_data["effects"]
                    )
                    for choice_data in game_data["available_choices"]
                ]
                
                memories = [
                    Memory(
                        id=memory_data["id"],
                        text=memory_data["text"],
                        memory_type=memory_data["memory_type"],
                        timestamp=memory_data["timestamp"]
                    )
                    for memory_data in game_data["memories"]
                ]
                
                game_progress = GameProgression(
                    current_location=game_data["game_progress"]["current_location"],
                    completed_events=game_data["game_progress"]["completed_events"],
                    relationships=game_data["game_progress"]["relationships"],
                    inventory=game_data["game_progress"]["inventory"]
                )
                
                game_state = GameState(
                    player_id=game_data["player_id"],
                    current_story=current_story,
                    available_choices=available_choices,
                    memories=memories,
                    game_progress=game_progress
                )
                
                logger.info(f"✅ Game state found and loaded")
                return game_state
            else:
                logger.info(f"❌ No game state found for player: {player_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching game state: {e}")
            raise
    
    # 💾 SAVE FILE OPERATIONS
    
    async def create_save_file(self, player_id: str, save_name: str, game_state: GameState) -> str:
        """
        💾 CREATE A SAVE FILE
        
        Step 1: Generate unique save ID
        Step 2: Convert game state to dictionary
        Step 3: Add save metadata
        Step 4: Insert into saves collection
        Step 5: Return save ID
        """
        try:
            logger.info(f"Creating save file '{save_name}' for player: {player_id}")
            
            # Generate unique save ID
            save_id = f"save-{uuid.uuid4().hex[:8]}"
            
            # Create save data
            save_data = {
                "save_id": save_id,
                "player_id": player_id,
                "save_name": save_name,
                "created_at": datetime.utcnow(),
                
                # Copy entire game state
                "current_story": {
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
                        "text": memory.text,
                        "memory_type": memory.memory_type,
                        "timestamp": memory.timestamp
                    }
                    for memory in game_state.memories
                ],
                "game_progress": {
                    "current_location": game_state.game_progress.current_location,
                    "completed_events": game_state.game_progress.completed_events,
                    "relationships": game_state.game_progress.relationships,
                    "inventory": game_state.game_progress.inventory
                }
            }
            
            # Insert save file
            result = await self.saves_collection.insert_one(save_data)
            
            if result.inserted_id:
                logger.info(f"✅ Save file created: {save_id}")
                return save_id
            else:
                raise Exception("Failed to create save file")
                
        except Exception as e:
            logger.error(f"❌ Error creating save file: {e}")
            raise
    
    async def load_save_file(self, player_id: str, save_id: str) -> Optional[GameState]:
        """
        💾 LOAD A SAVE FILE
        
        Step 1: Find save file in database
        Step 2: Verify it belongs to the player
        Step 3: Convert to GameState object
        Step 4: Return game state
        """
        try:
            logger.info(f"Loading save file {save_id} for player: {player_id}")
            
            # Find save file
            save_data = await self.saves_collection.find_one({
                "save_id": save_id,
                "player_id": player_id
            })
            
            if save_data:
                # Convert to GameState (same logic as get_game_state)
                current_story = Story(
                    title=save_data["current_story"]["title"],
                    content=save_data["current_story"]["content"],
                    location=save_data["current_story"]["location"]
                )
                
                available_choices = [
                    Choice(
                        id=choice_data["id"],
                        text=choice_data["text"],
                        effects=choice_data["effects"]
                    )
                    for choice_data in save_data["available_choices"]
                ]
                
                memories = [
                    Memory(
                        id=memory_data["id"],
                        text=memory_data["text"],
                        memory_type=memory_data["memory_type"],
                        timestamp=memory_data["timestamp"]
                    )
                    for memory_data in save_data["memories"]
                ]
                
                game_progress = GameProgression(
                    current_location=save_data["game_progress"]["current_location"],
                    completed_events=save_data["game_progress"]["completed_events"],
                    relationships=save_data["game_progress"]["relationships"],
                    inventory=save_data["game_progress"]["inventory"]
                )
                
                game_state = GameState(
                    player_id=save_data["player_id"],
                    current_story=current_story,
                    available_choices=available_choices,
                    memories=memories,
                    game_progress=game_progress
                )
                
                logger.info(f"✅ Save file loaded successfully")
                return game_state
            else:
                logger.info(f"❌ Save file not found: {save_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading save file: {e}")
            raise
    
    async def get_save_files(self, player_id: str) -> List[Dict[str, Any]]:
        """
        💾 GET ALL SAVE FILES FOR A PLAYER
        
        Step 1: Find all saves for the player
        Step 2: Return list of save metadata
        """
        try:
            logger.info(f"Fetching save files for player: {player_id}")
            
            # Find all saves for player
            cursor = self.saves_collection.find(
                {"player_id": player_id},
                {
                    "save_id": 1,
                    "save_name": 1,
                    "created_at": 1,
                    "_id": 0
                }
            ).sort("created_at", -1)  # Newest first
            
            saves = await cursor.to_list(length=None)
            
            logger.info(f"✅ Found {len(saves)} save files")
            return saves
            
        except Exception as e:
            logger.error(f"❌ Error fetching save files: {e}")
            raise
    
    # 🧠 MEMORY OPERATIONS
    
    async def add_memory(self, player_id: str, memory: Memory) -> bool:
        """
        🧠 ADD A MEMORY TO PLAYER'S GAME STATE
        
        Step 1: Find current game state
        Step 2: Add the new memory
        Step 3: Update in database
        Step 4: Return success status
        """
        try:
            logger.info(f"Adding memory for player {player_id}: {memory.text[:50]}...")
            
            # Add memory to the memories array
            result = await self.games_collection.update_one(
                {"player_id": player_id},
                {
                    "$push": {
                        "memories": {
                            "id": memory.id,
                            "text": memory.text,
                            "memory_type": memory.memory_type,
                            "timestamp": memory.timestamp
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Memory added successfully")
                return True
            else:
                logger.warning(f"⚠️ No memory added (game state may not exist)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding memory: {e}")
            raise


# 🎯 SIMPLE EXPLANATION:
#
# This service does everything related to the database:
# 1. Players - create, get, update personality
# 2. Game states - save, load current game 
# 3. Save files - create, load, list saves
# 4. Memories - add memories to game state
#
# Everything uses simple dictionary operations with MongoDB.
# No complex ORM or document models - just straightforward code!


async def get_database_service() -> SimpleDatabaseService:
    """
    🏭 DEPENDENCY INJECTION FUNCTION
    
    This creates and initializes a database service.
    Used by FastAPI dependency injection.
    """
    service = SimpleDatabaseService()
    await service.initialize()
    return service 