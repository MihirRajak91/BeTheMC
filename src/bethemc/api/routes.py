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
from ..auth.dependencies import get_current_user
from ..auth.models import UserInDB
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post(
    "/game/start", 
    response_model=GameResponse,
    summary="Start a New Game",
    description="""
    Start a new Pokémon adventure! This endpoint creates a new game session for the authenticated user.
    
    **What happens:**
    - Creates a new player with the given name
    - Initializes personality traits (all set to 5 by default)
    - Generates the opening story in Pallet Town
    - Provides initial choices to begin the adventure
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Complete game state including player info, current story, and available choices
    """,
    response_description="Game successfully started with initial story and choices",
    tags=["Game Flow"]
)
async def start_game(
    request: StartGameRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Start a new game for the authenticated user."""
    # Use the authenticated user's username as the player name if not provided
    player_name = request.player_name or current_user.username
    return await game_manager.start_game(player_name, request.personality_traits)

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
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Updated game state with new story and choices
    """,
    response_description="Updated game state with new story and choices",
    tags=["Game Flow"]
)
async def make_choice(
    request: ChoiceRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Process a player's choice and advance the story."""
    return await game_manager.make_choice(str(current_user.id), request.choice_id)

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
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Confirmation with save ID and timestamp
    """,
    response_description="Game saved successfully",
    tags=["Save System"]
)
async def save_game(
    request: SaveRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Save the current game state.
    
    Uses the authenticated user's ID as the player ID.
    """
    return await game_manager.save_game(str(current_user.id), request.save_name)

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
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Complete game state from the saved point
    """,
    response_description="Game state loaded successfully",
    tags=["Save System"]
)
async def load_game(
    request: LoadRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Load a saved game state.
    
    Uses the authenticated user's ID as the player ID.
    """
    return await game_manager.load_game(str(current_user.id), request.save_id)

@router.get(
    "/game/saves",
    summary="List Saves",
    description="""
    Get a list of all saved games for the authenticated user.
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** List of save files with metadata
    """,
    response_description="List of saved games",
    tags=["Save System"]
)
async def get_saves(
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get all saves for the authenticated user."""
    return await game_manager.get_saves(str(current_user.id))

@router.post(
    "/game/memory",
    summary="Add Memory",
    description="""
    Add a memory to your character's memory bank.
    
    **What happens:**
    - Stores the memory with the current game context
    - Can be used to influence future story events
    - Helps maintain character consistency
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Updated list of memories
    """,
    response_description="Memory added successfully",
    tags=["Memory System"]
)
async def add_memory(
    request: MemoryRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Add a memory to the player's memory bank."""
    return await game_manager.add_memory(str(current_user.id), request.memory_text, request.memory_type)

@router.post(
    "/game/personality",
    summary="Update Personality",
    description="""
    Update your character's personality traits.
    
    **What happens:**
    - Modifies the specified personality trait
    - Affects how the story unfolds and how NPCs interact with you
    - Can unlock special dialogue options
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Updated personality traits
    """,
    response_description="Personality updated successfully",
    tags=["Character Development"]
)
async def update_personality(
    request: PersonalityRequest,
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Update a player's personality trait."""
    return await game_manager.update_personality(
        str(current_user.id), 
        request.trait, 
        request.value
    )

@router.get(
    "/game/state",
    response_model=GameResponse,
    summary="Get Game State",
    description="""
    Get the current game state, including story, choices, and player stats.
    
    **Useful for:**
    - Syncing game state after page refresh
    - Debugging
    - Displaying current game information
    
    **Authentication:** Required (Bearer token)
    
    **Returns:** Complete current game state
    """,
    response_description="Current game state",
    tags=["Game State"]
)
async def get_game_state(
    current_user: UserInDB = Depends(get_current_user),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get the current game state for the authenticated user."""
    return await game_manager.get_game_state(str(current_user.id))