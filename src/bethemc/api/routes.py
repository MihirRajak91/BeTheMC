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
    Start a new Pokémon adventure! This endpoint creates a new game session for a player.
    
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
    """Start a new game for a player."""
    return await game_manager.start_game(request.player_name, request.personality_traits)

@router.post(
    "/game/choice", 
    response_model=ChoiceResponse,
    summary="Make a Choice",
    description="""
    Make a choice to advance your Pokémon adventure! This endpoint processes your decision and moves the story forward.
    
    **What happens:**
    - Validates the choice against available options
    - Updates your personality traits based on choice effects
    - Generates new story content based on your decision
    - Creates new choices for the next part of your adventure
    - Updates game progress and completed events
    
    **Returns:** Updated game state with new story and choices
    """,
    response_description="Choice processed successfully, story advanced",
    tags=["Game Flow"]
)
async def make_choice(
    request: ChoiceRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Process a player's choice and advance the story."""
    return await game_manager.make_choice(request.player_id, request.choice_id)

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
    summary="Load Saved Game",
    description="""
    Load a previously saved game! This restores your adventure to a previous save point.
    
    **What gets loaded:**
    - Complete game state from the save point
    - All progress, memories, and relationships
    - Story and choices from that moment
    
    **Returns:** Complete game state from the save point
    """,
    response_description="Game loaded successfully from save point",
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
    summary="Get Player Saves",
    description="""
    Get all saved games for a player! This shows all available save points you can load.
    
    **Returns:** List of all save files with names, timestamps, and brief descriptions
    """,
    response_description="List of all save files for the player",
    tags=["Save System"]
)
async def get_saves(
    player_id: str = Path(..., description="The player's unique ID", example="123e4567-e89b-12d3-a456-426614174000"),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get all saves for a player."""
    return await game_manager.get_saves(player_id)

@router.post(
    "/game/memory",
    summary="Add Memory",
    description="""
    Add a memory to your character's memory bank! Memories help shape your character's personality and future story events.
    
    **Memory Types:**
    - `general`: General memories and experiences
    - `relationship`: Memories about people or Pokémon
    - `achievement`: Memories of accomplishments
    - `lesson`: Memories of lessons learned
    
    **Returns:** Updated list of all memories
    """,
    response_description="Memory added successfully",
    tags=["Character Development"]
)
async def add_memory(
    request: MemoryRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Add a memory to the player's memory bank."""
    return await game_manager.add_memory(
        request.player_id, 
        request.memory_text, 
        request.memory_type
    )

@router.post(
    "/game/personality",
    summary="Update Personality",
    description="""
    Update your character's personality traits! This affects how the story unfolds and what choices become available.
    
    **Available Traits:**
    - `courage`: How brave and bold your character is (0-10)
    - `curiosity`: How interested in exploring and learning (0-10)
    - `wisdom`: How thoughtful and wise your character is (0-10)
    - `determination`: How persistent and focused (0-10)
    - `friendship`: How social and caring (0-10)
    
    **Returns:** Updated personality traits
    """,
    response_description="Personality trait updated successfully",
    tags=["Character Development"]
)
async def update_personality(
    request: PersonalityRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Update a player's personality trait."""
    return await game_manager.update_personality(
        request.player_id, 
        request.trait, 
        request.value
    )

@router.get(
    "/game/state/{player_id}", 
    response_model=GameResponse,
    summary="Get Current Game State",
    description="""
    Get your current game state! This shows everything about your current adventure.
    
    **What's included:**
    - Current story and location
    - Available choices
    - Personality traits
    - Memories and relationships
    - Game progress and completed events
    
    **Returns:** Complete current game state
    """,
    response_description="Current game state retrieved successfully",
    tags=["Game State"]
)
async def get_game_state(
    player_id: str = Path(..., description="The player's unique ID", example="123e4567-e89b-12d3-a456-426614174000"),
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get the current game state."""
    return await game_manager.get_game_state(player_id) 