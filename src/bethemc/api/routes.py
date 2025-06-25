"""
FastAPI routes for the BeTheMC game API.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import uuid

from .models import (
    NewGameRequest, ChoiceRequest, SaveGameRequest, LoadGameRequest,
    MemoryRequest, NarrativeResponse, GameState, CompressedContextResponse,
    APIResponse, PersonalityTraits
)
from .game_manager import GameManager

# Create router
router = APIRouter(prefix="/api/v1", tags=["game"])

# Global game manager instance
game_manager = GameManager()

def get_session_id() -> str:
    """Get or create a session ID for the current request."""
    # In a real application, you'd get this from authentication/session
    # For now, we'll use a simple approach with query parameters
    return str(uuid.uuid4())

@router.post("/game/new", response_model=APIResponse)
async def create_new_game(request: NewGameRequest):
    """Create a new game session."""
    try:
        session_id = get_session_id()
        session = game_manager.create_new_game(
            session_id=session_id,
            starting_location=request.starting_location,
            personality=request.personality
        )
        
        return APIResponse(
            success=True,
            message="New game created successfully",
            data={
                "session_id": session_id,
                "game_state": session.get_current_state().dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create new game: {str(e)}")

@router.get("/game/{session_id}/state", response_model=NarrativeResponse)
async def get_game_state(session_id: str):
    """Get the current state of a game session."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return session.get_current_state()

@router.post("/game/{session_id}/choice", response_model=NarrativeResponse)
async def make_choice(session_id: str, request: ChoiceRequest):
    """Make a choice in the game."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    result = session.make_choice(request.choice_index)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid choice index")
    
    return result

@router.post("/game/{session_id}/save", response_model=APIResponse)
async def save_game(session_id: str, request: SaveGameRequest):
    """Save a game session."""
    success = game_manager.save_game(session_id, request.save_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save game")
    
    return APIResponse(
        success=True,
        message=f"Game saved as {request.save_name}",
        data={"save_name": request.save_name}
    )

@router.post("/game/{session_id}/load", response_model=APIResponse)
async def load_game(session_id: str, request: LoadGameRequest):
    """Load a game session."""
    session = game_manager.load_game(session_id, request.save_name)
    if not session:
        raise HTTPException(status_code=404, detail="Save file not found")
    
    return APIResponse(
        success=True,
        message=f"Game loaded from {request.save_name}",
        data={
            "session_id": session_id,
            "game_state": session.get_current_state().dict()
        }
    )

@router.get("/saves", response_model=APIResponse)
async def list_saves():
    """List available save files."""
    saves = game_manager.list_saves()
    return APIResponse(
        success=True,
        message="Save files retrieved successfully",
        data={"saves": saves}
    )

@router.delete("/saves/{save_name}", response_model=APIResponse)
async def delete_save(save_name: str):
    """Delete a save file."""
    success = game_manager.delete_save(save_name)
    if not success:
        raise HTTPException(status_code=404, detail="Save file not found")
    
    return APIResponse(
        success=True,
        message=f"Save file {save_name} deleted successfully"
    )

@router.post("/game/{session_id}/memory", response_model=APIResponse)
async def add_memory(session_id: str, request: MemoryRequest):
    """Add a memory to the game session."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    success = session.add_memory(
        memory_type=request.memory_type,
        content=request.content,
        location=request.location,
        metadata=request.metadata
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add memory")
    
    return APIResponse(
        success=True,
        message="Memory added successfully"
    )

@router.get("/game/{session_id}/context", response_model=CompressedContextResponse)
async def get_compressed_context(session_id: str):
    """Get compressed context for the current location."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    context = session.get_compressed_context()
    return CompressedContextResponse(**context)

@router.get("/game/{session_id}/personality", response_model=PersonalityTraits)
async def get_personality(session_id: str):
    """Get the current personality traits."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return session.personality

@router.put("/game/{session_id}/personality", response_model=APIResponse)
async def update_personality(session_id: str, personality: PersonalityTraits):
    """Update the personality traits."""
    session = game_manager.get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session.personality = personality
    
    return APIResponse(
        success=True,
        message="Personality updated successfully",
        data={"personality": personality.dict()}
    )

@router.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint."""
    return APIResponse(
        success=True,
        message="BeTheMC API is running",
        data={
            "version": "1.0.0",
            "status": "healthy"
        }
    )

@router.get("/info", response_model=APIResponse)
async def get_api_info():
    """Get API information."""
    return APIResponse(
        success=True,
        message="BeTheMC API Information",
        data={
            "name": "BeTheMC",
            "description": "AI-powered Pokémon adventure game",
            "version": "1.0.0",
            "features": [
                "Dynamic story generation",
                "Personality-driven choices",
                "Compressed context for long stories",
                "Save/load functionality",
                "Memory system"
            ]
        }
    ) 