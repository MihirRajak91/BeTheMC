"""
FastAPI routes for the BeTheMC game API.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from .game_manager import GameManager, get_game_manager
from ..models.api import (
    GameResponse, ChoiceRequest, ChoiceResponse, SaveRequest, 
    LoadRequest, MemoryRequest, PersonalityRequest, StartGameRequest
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post(
    "/game/start", 
    response_model=GameResponse,
    summary="Start a New Game",
    description="""
    Start a new Pokémon adventure! This endpoint creates a new game session.
    
    **What happens:**
    - Creates a new player with the given name
    - Initializes personality traits (all set to 5 by default)
    - Generates the opening story in Pallet Town
    - Provides initial choices to begin the adventure
    
    **Returns:** Complete game state including player info, current story, and available choices
    """,
    response_description="Game successfully started with initial story and choices",
    tags=["Game Flow"]
)
async def start_game(
    request: StartGameRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Start a new game."""
    return await game_manager.start_game(request.player_name, request.personality_traits)

@router.post(
    "/game/choice", 
    response_model=ChoiceResponse,
    summary="Make a Choice",
    description="""
    Make a choice to advance your Pokémon adventure! This endpoint processes your decision and moves the story forward.
    
    **What happens:**
    - Validates the choice against available options
    - Updates the game state based on your choice
    - Generates new story content and choices
    - Updates your character's personality based on choices
    
    **Returns:** Updated game state with new story and choices
    """,
    response_description="Updated game state with new story and choices",
    tags=["Game Flow"]
)
async def make_choice(
    request: ChoiceRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Process a player's choice and advance the story."""
    try:
        logger.info(f"Processing choice for player ID: {request.player_id}, choice ID: {request.choice_id}")
        
        # Make the choice with the provided player ID
        return await game_manager.make_choice(request.player_id, request.choice_id)
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP error in make_choice: {str(he.detail)}")
        raise he
    except Exception as e:
        logger.error(f"Error in make_choice: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing choice: {str(e)}")

@router.post(
    "/game/save",
    summary="Save Game",
    description="""
    Save your current game progress! This creates a save point you can return to later.
    
    **What gets saved:**
    - Current story and location
    - Player personality traits
    - Game progress and completed events
    - Memories and relationships
    - Available choices
    
    **Returns:** Confirmation with save ID and timestamp
    """,
    response_description="Game saved successfully",
    tags=["Save System"]
)
async def save_game(
    request: SaveRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Save the current game state."""
    return await game_manager.save_game(request.player_id, request.save_name)

@router.post(
    "/game/load",
    response_model=GameResponse,
    summary="Load Game",
    description="""
    Load a previously saved game state to continue your adventure.
    
    **What gets loaded:**
    - Saved story progress
    - Player stats and inventory
    - Game world state
    - Unlocked achievements
    
    **Returns:** Complete game state from the saved point
    """,
    response_description="Game state loaded successfully",
    tags=["Save System"]
)
async def load_game(
    request: LoadRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Load a saved game state."""
    return await game_manager.load_game(request.player_id, request.save_id)

@router.get(
    "/game/saves/{player_id}",
    summary="List Saves",
    description="""
    Get a list of all saved games for a specific player.
    
    **Returns:** List of save files with metadata
    """,
    response_description="List of saved games",
    tags=["Save System"]
)
async def get_saves(
    player_id: str = Path(..., description="Player ID to get saves for"),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get all saves for a player."""
    return await game_manager.get_saves(player_id)

@router.post(
    "/game/memory",
    summary="Add Memory",
    description="""
    Add a memory to your character's memory bank.
    
    **What happens:**
    - Stores the memory with the current game context
    - Can be used to influence future story events
    - Helps maintain character consistency
    
    **Returns:** Updated list of memories
    """,
    response_description="Memory added successfully",
    tags=["Memory System"]
)
async def add_memory(
    request: MemoryRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Add a memory to the player's memory bank."""
    return await game_manager.add_memory(request.player_id, request.memory_text, request.memory_type)

@router.post(
    "/game/personality",
    summary="Update Personality",
    description="""
    Update your character's personality traits.
    
    **What happens:**
    - Modifies the specified personality trait
    - Affects how the story unfolds and how NPCs interact with you
    - Can unlock special dialogue options
    
    **Returns:** Updated personality traits
    """,
    response_description="Personality updated successfully",
    tags=["Character Development"]
)
async def update_personality(
    request: PersonalityRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Update a player's personality trait."""
    return await game_manager.update_personality(request.player_id, request.trait, request.value)

@router.get(
    "/game/state/{player_id}",
    response_model=GameResponse,
    summary="Get Game State",
    description="""
    Get the current game state, including story, choices, and player stats.
    
    **Useful for:**
    - Syncing game state after page refresh
    - Debugging
    - Displaying current game information
    
    **Returns:** Complete current game state
    """,
    response_description="Current game state",
    tags=["Game State"]
)
async def get_game_state(
    player_id: str = Path(..., description="Player ID to get state for"),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get the current game state for a player."""
    return await game_manager.get_game_state_response(player_id)