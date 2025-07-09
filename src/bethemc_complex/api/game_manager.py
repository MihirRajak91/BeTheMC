"""
Game manager for handling game state and API operations.
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from fastapi import HTTPException, Depends

from ..core.game import GameLoop
from ..core.progression import ProgressionManager
from ..ai.story_generator import StoryGenerator
from ..utils.config import Config
from ..utils.logger import setup_logger, get_logger
from ..models.core import PersonalityTraits, Choice, Memory, NarrativeSegment, GameState, Player, Story, PersonalityTrait, GameProgression
from ..models.api import (
    PersonalityTraitsSchema, ChoiceSchema, NarrativeResponseSchema, GameStateSchema,
    ChoiceRequestSchema, NewGameRequestSchema, SaveGameRequestSchema, LoadGameRequestSchema,
    CompressedContextResponseSchema, MemoryRequestSchema, APIResponseSchema, GameResponse, ChoiceRequest, ChoiceResponse, SaveRequest, LoadRequest, MemoryRequest, PersonalityRequest
)
from ..services.game_service import GameService
from ..services.save_service import SaveService
from ..database.service import DatabaseService
from .dependencies import get_game_service, get_save_service

logger = get_logger(__name__)

class GameManager:
    """
    🎮 Game Manager - API Layer Orchestrator
    
    This class acts as the primary coordinator between the API layer and
    the underlying services. It handles all game-related API operations,
    manages database persistence, and ensures proper error handling and
    response formatting for the FastAPI endpoints.
    
    Key Responsibilities:
    • API Request Processing: Handle incoming API requests and validate inputs
    • Service Coordination: Orchestrate calls between GameService, SaveService, and DatabaseService
    • Response Formatting: Convert internal models to API response schemas
    • Error Handling: Provide consistent error responses and logging
    • Database Persistence: Manage game state storage and retrieval
    • State Validation: Ensure game states are valid before processing
    
    Architecture Role:
    • Receives requests from FastAPI routes
    • Coordinates with multiple services (GameService, SaveService, DatabaseService)
    • Returns properly formatted API responses
    • Handles all database persistence operations
    
    Dependencies:
    • GameService: Core game logic and state management
    • SaveService: Game save/load operations
    • DatabaseService: MongoDB persistence operations
    
    Usage:
        game_manager = GameManager(game_service, save_service)
        response = await game_manager.start_game("Ash Ketchum")
    """
    
    def __init__(self, game_service: GameService, save_service: SaveService):
        """
        Initialize the Game Manager with required services.
        
        Args:
            game_service (GameService): Service for core game logic
            save_service (SaveService): Service for save/load operations
        """
        self.game_service = game_service
        self.save_service = save_service
        self.db_service = DatabaseService()
    
    async def start_game(self, player_name: str, personality_traits: Optional[Dict[str, int]] = None) -> GameResponse:
        """
        🆕 Start a new game session for a player.
        
        Creates a complete new game state with initial story, choices,
        and player data. The game state is immediately persisted to the
        database and a formatted API response is returned.
        
        Args:
            player_name (str): The name of the player starting the adventure
            personality_traits (Optional[Dict[str, int]]): Custom personality traits (0-10 scale).
                If None, uses balanced defaults (all traits = 5)
        
        Returns:
            GameResponse: Complete game state formatted for API response
        
        Raises:
            HTTPException: If game creation fails or database operations fail
        
        Example:
            response = await game_manager.start_game(
                "Ash Ketchum",
                personality_traits={"courage": 7, "curiosity": 8}
            )
        """
        try:
            game_state = await self.game_service.start_new_game(player_name, personality_traits)
            
            # Store the game state in MongoDB
            player_id = str(game_state.player.id)
            await self.db_service.save_game_state(game_state)
            
            logger.info(f"Started new game for player ID: {player_id}, name: {player_name}")
            
            return GameResponse(
                player_id=player_id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
        except Exception as e:
            logger.error(f"Failed to start game: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")
    
    async def make_choice(self, player_id: str, choice_id: str) -> ChoiceResponse:
        """
        🎯 Process a player's choice and advance the story.
        
        Takes a player's choice, validates it against available options,
        processes the choice through the game service, updates the database,
        and returns the updated game state. This is the primary method
        for story progression in the game.
        
        Args:
            player_id (str): Unique identifier for the player
            choice_id (str): ID of the choice the player selected
        
        Returns:
            ChoiceResponse: Updated game state after choice processing
        
        Raises:
            HTTPException: If choice is invalid, player not found, or processing fails
        
        Example:
            response = await game_manager.make_choice(
                "player-123", "choice-visit-oak-lab"
            )
        """
        try:
            logger.info(f"Processing choice {choice_id} for player {player_id}")
            
            if not player_id:
                raise ValueError("Player ID is required")
                
            if not choice_id:
                raise ValueError("Choice ID is required")
            
            # Get the current game state
            game_state = await self.get_game_state(player_id)
            logger.info(f"Found game state for player: {game_state.player.name}")
            
            # Log available choices for debugging
            available_choice_ids = [str(choice.id) for choice in game_state.available_choices]
            logger.info(f"Available choice IDs: {available_choice_ids}")
            
            # Check if the choice is valid
            if choice_id not in available_choice_ids:
                error_msg = f"Invalid choice ID: {choice_id}. Available choices: {available_choice_ids}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Process the choice
            logger.info(f"Processing choice {choice_id} for player {player_id}")
            updated_state = await self.game_service.process_choice(game_state, choice_id)
            
            # Update the game state in MongoDB
            await self.db_service.save_game_state(updated_state)
            logger.info(f"Successfully processed choice {choice_id} for player {player_id}")
            
            return ChoiceResponse(
                player_id=updated_state.player.id,
                current_story=updated_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in updated_state.available_choices],
                memories=[memory.__dict__ for memory in updated_state.memories],
                game_progress=updated_state.progression.__dict__
            )
            
        except HTTPException as he:
            # Re-raise HTTP exceptions as they are
            logger.error(f"HTTP error in make_choice: {str(he.detail)}")
            raise he
            
        except ValueError as ve:
            # Handle validation errors
            logger.error(f"Validation error in make_choice: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
            
        except Exception as e:
            # Log the full exception for debugging
            logger.error(f"Unexpected error in make_choice: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while processing your choice: {str(e)}"
            )
    
    async def get_game_state(self, player_id: str) -> GameState:
        """
        📊 Retrieve the current game state for a player.
        
        Fetches the complete game state from the database, including
        player information, current story, available choices, memories,
        and progression data. This is used internally by other methods
        and can be called directly for state inspection.
        
        Args:
            player_id (str): Unique identifier for the player
        
        Returns:
            GameState: Complete current game state from database
        
        Raises:
            HTTPException: If player not found (404) or database error (500)
        
        Example:
            game_state = await game_manager.get_game_state("player-123")
        """
        try:
            if not player_id:
                raise ValueError("Player ID is required")
                
            logger.info(f"Getting game state for player ID: {player_id}")
            
            # Get game state from MongoDB
            game_state = await self.db_service.get_game_state(player_id)
            
            if not game_state:
                error_msg = f"No game found for player ID: {player_id}"
                logger.warning(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            
            logger.info(f"Found game state for player ID: {player_id}")
            return game_state
            
        except HTTPException as he:
            # Re-raise HTTP exceptions
            logger.error(f"HTTP error in get_game_state: {str(he.detail)}")
            raise he
        except Exception as e:
            error_msg = f"Error getting game state for player {player_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)
    
    async def save_game(self, player_id: str, save_name: str) -> Dict[str, Any]:
        """Save the current game state."""
        try:
            # Get current game state from MongoDB
            game_state = await self.db_service.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="Game not found")
            
            # Save game to saves collection
            save_id = await self.db_service.save_game(game_state, save_name)
            
            return {
                "message": "Game saved successfully",
                "save_id": save_id,
                "save_name": save_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save game: {str(e)}")
    
    async def load_game(self, player_id: str, save_id: str) -> GameResponse:
        """Load a saved game state."""
        try:
            # Load game from saves collection
            game_state = await self.db_service.load_game(player_id, save_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="Save not found")
            
            # Update current game state in MongoDB
            await self.db_service.save_game_state(game_state)
            
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
            saves = await self.db_service.get_player_saves(player_id)
            return {"saves": saves}
        except Exception as e:
            logger.error(f"Failed to get saves: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get saves: {str(e)}")
    
    async def add_memory(self, player_id: str, memory_text: str, memory_type: str = "general") -> Dict[str, Any]:
        """Add a memory to the player's memory bank."""
        try:
            # Get current game state from MongoDB
            game_state = await self.db_service.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="Game not found")
            
            # Add memory to game state
            updated_state = await self.game_service.add_memory(game_state, memory_text, memory_type)
            
            # Save updated game state to MongoDB
            await self.db_service.save_game_state(updated_state)
            
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
            # Get current game state from MongoDB
            game_state = await self.db_service.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="Game not found")
            
            # Update personality trait
            updated_state = await self.game_service.update_personality(game_state, trait, value)
            
            # Save updated game state to MongoDB
            await self.db_service.save_game_state(updated_state)
            
            return {
                "message": "Personality updated successfully",
                "personality_traits": updated_state.player.personality_traits
            }
        except Exception as e:
            logger.error(f"Failed to update personality: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update personality: {str(e)}")
    
    async def get_game_state_response(self, player_id: str) -> GameResponse:
        """Get the current game state as a GameResponse."""
        try:
            game_state = await self.get_game_state(player_id)
            
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
            logger.error(f"Failed to get game state response: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get game state response: {str(e)}")

# Dependency injection
def get_game_manager(
    game_service: GameService = Depends(get_game_service),
    save_service: SaveService = Depends(get_save_service)
) -> GameManager:
    return GameManager(game_service, save_service) 