"""
FastAPI routes for the BeTheMC game API.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from .game_manager import GameManager, get_game_manager
from ..models.api import (
    GameResponse, ChoiceRequest, ChoiceResponse, SaveRequest, 
    LoadRequest, MemoryRequest, PersonalityRequest
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/game/start", response_model=GameResponse)
async def start_game(
    player_name: str,
    personality_traits: Dict[str, int] = None,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Start a new game for a player."""
    return await game_manager.start_game(player_name, personality_traits)

@router.post("/game/choice", response_model=ChoiceResponse)
async def make_choice(
    request: ChoiceRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Process a player's choice and advance the story."""
    return await game_manager.make_choice(request.player_id, request.choice_id)

@router.post("/game/save")
async def save_game(
    request: SaveRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Save the current game state."""
    return await game_manager.save_game(request.player_id, request.save_name)

@router.post("/game/load", response_model=GameResponse)
async def load_game(
    request: LoadRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Load a saved game state."""
    return await game_manager.load_game(request.player_id, request.save_id)

@router.get("/game/saves/{player_id}")
async def get_saves(
    player_id: str,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get all saves for a player."""
    return await game_manager.get_saves(player_id)

@router.post("/game/memory")
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

@router.post("/game/personality")
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

@router.get("/game/state/{player_id}", response_model=GameResponse)
async def get_game_state(
    player_id: str,
    game_manager: GameManager = Depends(get_game_manager)
):
    """Get the current game state."""
    return await game_manager.get_game_state(player_id) 