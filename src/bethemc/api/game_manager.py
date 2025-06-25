"""
Game manager for handling game state and API operations.
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from fastapi import HTTPException, Depends

from bethemc.core.game import GameLoop
from bethemc.core.progression import ProgressionManager
from bethemc.ai.story_generator import StoryGenerator
from bethemc.utils.config import Config
from bethemc.utils.logger import setup_logger, get_logger
from bethemc.models.core import PersonalityTraits, Choice, Memory, NarrativeSegment, GameState, Player, Story, PersonalityTrait, GameProgression
from bethemc.models.api import (
    PersonalityTraitsSchema, ChoiceSchema, NarrativeResponseSchema, GameStateSchema,
    ChoiceRequestSchema, NewGameRequestSchema, SaveGameRequestSchema, LoadGameRequestSchema,
    CompressedContextResponseSchema, MemoryRequestSchema, APIResponseSchema, GameResponse, ChoiceRequest, ChoiceResponse, SaveRequest, LoadRequest, MemoryRequest, PersonalityRequest
)
from bethemc.services.game_service import GameService
from bethemc.services.save_service import SaveService

logger = get_logger(__name__)

class GameManager:
    """Manages game state and coordinates between services."""
    
    def __init__(self, game_service: GameService, save_service: SaveService):
        self.game_service = game_service
        self.save_service = save_service
        self.active_games: Dict[str, GameState] = {}
    
    async def start_game(self, player_name: str, personality_traits: Optional[Dict[str, int]] = None) -> GameResponse:
        """Start a new game for a player."""
        try:
            game_state = await self.game_service.start_new_game(player_name, personality_traits)
            self.active_games[game_state.player.id] = game_state
            
            return GameResponse(
                player_id=game_state.player.id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")
    
    async def make_choice(self, player_id: str, choice_id: str) -> ChoiceResponse:
        """Process a player's choice and advance the story."""
        try:
            if player_id not in self.active_games:
                raise HTTPException(status_code=404, detail="Game not found")
            
            game_state = self.active_games[player_id]
            updated_state = await self.game_service.process_choice(game_state, choice_id)
            self.active_games[player_id] = updated_state
            
            return ChoiceResponse(
                player_id=updated_state.player.id,
                current_story=updated_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in updated_state.available_choices],
                memories=[memory.__dict__ for memory in updated_state.memories],
                game_progress=updated_state.progression.__dict__
            )
        except Exception as e:
            logger.error(f"Failed to process choice: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process choice: {str(e)}")
    
    async def save_game(self, player_id: str, save_name: str) -> Dict[str, Any]:
        """Save the current game state."""
        try:
            if player_id not in self.active_games:
                raise HTTPException(status_code=404, detail="Game not found")
            
            game_state = self.active_games[player_id]
            save_data = await self.save_service.save_game(game_state, save_name)
            
            return {
                "message": "Game saved successfully",
                "save_id": save_data["save_id"],
                "save_name": save_name,
                "timestamp": save_data["timestamp"]
            }
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save game: {str(e)}")
    
    async def load_game(self, player_id: str, save_id: str) -> GameResponse:
        """Load a saved game state."""
        try:
            game_state = await self.save_service.load_game(player_id, save_id)
            self.active_games[player_id] = game_state
            
            return GameResponse(
                player_id=game_state.player.id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load game: {str(e)}")
    
    async def get_saves(self, player_id: str) -> Dict[str, Any]:
        """Get all saves for a player."""
        try:
            saves = await self.save_service.get_player_saves(player_id)
            return {"saves": saves}
        except Exception as e:
            logger.error(f"Failed to get saves: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get saves: {str(e)}")
    
    async def add_memory(self, player_id: str, memory_text: str, memory_type: str = "general") -> Dict[str, Any]:
        """Add a memory to the player's memory bank."""
        try:
            if player_id not in self.active_games:
                raise HTTPException(status_code=404, detail="Game not found")
            
            game_state = self.active_games[player_id]
            updated_state = await self.game_service.add_memory(game_state, memory_text, memory_type)
            self.active_games[player_id] = updated_state
            
            return {
                "message": "Memory added successfully",
                "memories": [memory.__dict__ for memory in updated_state.memories]
            }
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")
    
    async def update_personality(self, player_id: str, trait: str, value: int) -> Dict[str, Any]:
        """Update a player's personality trait."""
        try:
            if player_id not in self.active_games:
                raise HTTPException(status_code=404, detail="Game not found")
            
            game_state = self.active_games[player_id]
            updated_state = await self.game_service.update_personality(game_state, trait, value)
            self.active_games[player_id] = updated_state
            
            return {
                "message": "Personality updated successfully",
                "personality_traits": updated_state.player.personality_traits
            }
        except Exception as e:
            logger.error(f"Failed to update personality: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update personality: {str(e)}")
    
    async def get_game_state(self, player_id: str) -> GameResponse:
        """Get the current game state."""
        try:
            if player_id not in self.active_games:
                raise HTTPException(status_code=404, detail="Game not found")
            
            game_state = self.active_games[player_id]
            
            return GameResponse(
                player_id=game_state.player.id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
        except Exception as e:
            logger.error(f"Failed to get game state: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get game state: {str(e)}")

# Dependency injection
def get_game_manager(
    game_service: GameService = Depends(),
    save_service: SaveService = Depends()
) -> GameManager:
    return GameManager(game_service, save_service) 