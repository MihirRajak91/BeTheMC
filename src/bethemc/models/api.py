"""
API Models - Request and Response models for the BeTheMC API.

This file contains all the models used for API communication:
- Request models (what the frontend sends to the API)
- Response models (what the API sends back to the frontend)

These are separate from the core game models to keep API concerns separate.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class StartGameRequest(BaseModel):
    """
    Request to start a new game.
    
    What the frontend sends:
    - player_name: What the player wants to be called
    - personality_traits: Optional starting personality (uses defaults if not provided)
    
    Example:
    {"player_name": "Ash", "personality_traits": {"courage": 7}}
    """
    player_name: str = Field(..., description="Player's chosen name")
    personality_traits: Optional[Dict[str, int]] = Field(
        default=None,
        description="Optional starting personality traits (0-10 scale)"
    )


class ChoiceRequest(BaseModel):
    """
    Request to make a choice in the game.
    
    What the frontend sends:
    - player_id: Which player is making the choice
    - choice_id: Which choice they selected
    
    Example:
    {"player_id": "123-456", "choice_id": "choice-789"}
    """
    player_id: str = Field(..., description="Player making the choice")
    choice_id: str = Field(..., description="ID of chosen choice")


class SaveRequest(BaseModel):
    """
    Request to save the current game.
    
    What the frontend sends:
    - player_id: Which player's game to save
    - save_name: What to call this save file
    
    Example:
    {"player_id": "123-456", "save_name": "Before choosing starter"}
    """
    player_id: str = Field(..., description="Player whose game to save")
    save_name: str = Field(..., description="Name for this save file")


class LoadRequest(BaseModel):
    """
    Request to load a saved game.
    
    What the frontend sends:
    - player_id: Which player is loading
    - save_id: Which save file to load
    
    Example:
    {"player_id": "123-456", "save_id": "save-789"}
    """
    player_id: str = Field(..., description="Player loading the game")
    save_id: str = Field(..., description="ID of save file to load")


class MemoryRequest(BaseModel):
    """
    Request to add a memory to the player's memory bank.
    
    What the frontend sends:
    - player_id: Which player to add memory for
    - memory_text: The memory content
    - memory_type: Type of memory (optional)
    
    Example:
    {"player_id": "123-456", "memory_text": "I promised to help Professor Oak", "memory_type": "promise"}
    """
    player_id: str = Field(..., description="Player to add memory for")
    memory_text: str = Field(..., description="Memory content")
    memory_type: str = Field(default="general", description="Type of memory")


class PersonalityRequest(BaseModel):
    """
    Request to update a player's personality trait.
    
    What the frontend sends:
    - player_id: Which player to update
    - trait: Which personality trait to change
    - value: New value for the trait (0-10)
    
    Example:
    {"player_id": "123-456", "trait": "courage", "value": 8}
    """
    player_id: str = Field(..., description="Player to update")
    trait: str = Field(..., description="Personality trait to update")
    value: int = Field(..., ge=0, le=10, description="New trait value (0-10)")


class GameResponse(BaseModel):
    """
    Complete game state response.
    
    What we send back to the frontend with everything they need:
    - player_id: The player's unique ID
    - player_name: The player's name
    - current_story: The story they're currently seeing
    - available_choices: What choices they can make
    - personality_traits: Their current personality
    - memories: Their collected memories
    - game_progress: Their progress through the game
    
    This is what the frontend uses to display the game to the player.
    """
    player_id: str = Field(..., description="Player's unique ID")
    player_name: str = Field(..., description="Player's name")
    current_story: Dict[str, Any] = Field(..., description="Current story segment")
    available_choices: List[Dict[str, Any]] = Field(..., description="Available choices")
    personality_traits: Dict[str, int] = Field(..., description="Player's personality")
    memories: List[Dict[str, Any]] = Field(..., description="Player's memories")
    game_progress: Dict[str, Any] = Field(..., description="Game progression")


class ChoiceResponse(BaseModel):
    """
    Response after making a choice.
    
    What we send back after a player makes a choice:
    - player_id: The player's ID
    - current_story: The NEW story after their choice
    - available_choices: The NEW choices they can make
    - memories: Updated memories (if any new ones)
    - game_progress: Updated progress
    
    This lets the frontend update the game display with the new story and choices.
    """
    player_id: str = Field(..., description="Player's unique ID")
    current_story: Dict[str, Any] = Field(..., description="Updated story segment")
    available_choices: List[Dict[str, Any]] = Field(..., description="New available choices")
    memories: List[Dict[str, Any]] = Field(..., description="Updated memories")
    game_progress: Dict[str, Any] = Field(..., description="Updated progression") 