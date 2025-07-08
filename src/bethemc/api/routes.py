"""
Simple Routes - Easy to understand API endpoints!

This file contains all the API routes in a simple, clear way.
Each route does ONE thing and is easy to understand.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from .game_manager import SimpleGameManager, get_simple_game_manager
from ..models.models import (
    StartGameRequest, GameResponse, 
    ChoiceRequest, ChoiceResponse,
    SaveRequest, LoadRequest
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Create the router for our API endpoints
router = APIRouter()


@router.post(
    "/game/start",
    response_model=GameResponse,
    summary="🎮 Start New Game",
    description="Start a brand new Pokémon adventure! Just provide your name.",
    tags=["Game"]
)
async def start_game(
    request: StartGameRequest,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> GameResponse:
    """
    Start a new game!
    
    What this does:
    1. Creates a new player with your name
    2. Starts you in Pallet Town with Professor Oak
    3. Gives you your first choices to make
    4. Returns everything you need to play
    """
    logger.info(f"🎮 Starting new game for: {request.player_name}")
    return await game_manager.start_new_game(request.player_name)


@router.post(
    "/game/choice",
    response_model=ChoiceResponse,
    summary="⚡ Make Choice",
    description="Make a choice to advance your adventure!",
    tags=["Game"]
)
async def make_choice(
    request: ChoiceRequest,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> ChoiceResponse:
    """
    Make a choice in your game!
    
    What this does:
    1. Takes your choice from the available options
    2. Updates your personality based on the choice
    3. Generates new story content
    4. Gives you new choices to make
    5. Saves your progress
    """
    logger.info(f"⚡ Player {request.player_id} making choice: {request.choice_id}")
    return await game_manager.make_choice(request.player_id, request.choice_id)


@router.get(
    "/game/state/{player_id}",
    response_model=GameResponse,
    summary="📋 Get Current Game",
    description="Get your current game state - story, choices, stats, etc.",
    tags=["Game"]
)
async def get_game_state(
    player_id: str,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> GameResponse:
    """
    Get your current game state!
    
    What this does:
    1. Looks up your current game in the database
    2. Returns your story, choices, personality, and progress
    
    Useful for:
    - Refreshing the game after closing your browser
    - Checking your current stats
    - Seeing what choices you have available
    """
    logger.info(f"📋 Getting game state for player: {player_id}")
    return await game_manager.get_current_game(player_id)


@router.post(
    "/game/save",
    summary="💾 Save Game",
    description="Save your current progress with a custom name",
    tags=["Save System"]
)
async def save_game(
    request: SaveRequest,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> Dict[str, Any]:
    """
    Save your game!
    
    What this does:
    1. Takes your current game state
    2. Saves it with the name you choose
    3. Returns confirmation with save details
    
    You can have multiple saves with different names!
    """
    logger.info(f"💾 Saving game for player {request.player_id} as '{request.save_name}'")
    return await game_manager.save_game(request.player_id, request.save_name)


@router.post(
    "/game/load",
    response_model=GameResponse,
    summary="📂 Load Game",
    description="Load a previously saved game",
    tags=["Save System"]
)
async def load_game(
    request: LoadRequest,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> GameResponse:
    """
    Load a saved game!
    
    What this does:
    1. Finds your saved game by ID
    2. Makes it your current game
    3. Returns the loaded game state
    
    You can continue right where you left off!
    """
    logger.info(f"📂 Loading save {request.save_id} for player {request.player_id}")
    return await game_manager.load_game(request.player_id, request.save_id)


@router.get(
    "/game/saves/{player_id}",
    summary="📁 List Saves",
    description="Get all your saved games",
    tags=["Save System"]
)
async def list_saves(
    player_id: str,
    game_manager: SimpleGameManager = Depends(get_simple_game_manager)
) -> Dict[str, Any]:
    """
    Get all your saved games!
    
    What this does:
    1. Looks up all saves for your player ID
    2. Returns a list with save names, dates, etc.
    
    Useful for seeing all your save files before loading one.
    """
    logger.info(f"📁 Listing saves for player: {player_id}")
    
    # Use the database service directly for this simple operation
    saves = await game_manager.db.get_player_saves(player_id)
    
    return {
        "player_id": player_id,
        "saves": saves,
        "total_saves": len(saves)
    }


# 🎯 SIMPLE EXPLANATION OF ALL ENDPOINTS:
#
# 1. POST /game/start - Start new adventure
# 2. POST /game/choice - Make a choice to continue
# 3. GET /game/state/{player_id} - See current game
# 4. POST /game/save - Save current progress  
# 5. POST /game/load - Load saved progress
# 6. GET /game/saves/{player_id} - List all saves
#
# That's it! Just 6 simple endpoints for the whole game. 