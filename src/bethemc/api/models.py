"""
Pydantic models for API requests and responses.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PersonalityTraits(BaseModel):
    """Player personality traits."""
    friendship: float = Field(ge=0.0, le=1.0, description="Ability to form bonds")
    courage: float = Field(ge=0.0, le=1.0, description="Willingness to face challenges")
    curiosity: float = Field(ge=0.0, le=1.0, description="Desire to explore and learn")
    wisdom: float = Field(ge=0.0, le=1.0, description="Ability to make good decisions")
    determination: float = Field(ge=0.0, le=1.0, description="Persistence in achieving goals")

class Choice(BaseModel):
    """A choice option for the player."""
    text: str = Field(description="The choice text")
    effects: Dict[str, float] = Field(default_factory=dict, description="Effects on personality traits")

class NarrativeResponse(BaseModel):
    """Response containing narrative and choices."""
    narrative: str = Field(description="The story narrative")
    choices: List[Choice] = Field(description="Available choices for the player")
    location: str = Field(description="Current location")
    personality: PersonalityTraits = Field(description="Current personality state")
    active_promises: List[str] = Field(default_factory=list, description="Active promises")
    key_relationships: List[str] = Field(default_factory=list, description="Key relationships")
    story_context: Dict[str, Any] = Field(default_factory=dict, description="Story context")

class GameState(BaseModel):
    """Current game state."""
    location: str = Field(description="Current location")
    personality: PersonalityTraits = Field(description="Player personality")
    recent_events: List[str] = Field(default_factory=list, description="Recent events")
    relationships: Dict[str, Any] = Field(default_factory=dict, description="Character relationships")
    pokemon_partners: List[str] = Field(default_factory=list, description="Pokémon companions")
    memories: List[str] = Field(default_factory=list, description="Important moments")

class ChoiceRequest(BaseModel):
    """Request to make a choice."""
    choice_index: int = Field(ge=0, description="Index of the chosen option")

class NewGameRequest(BaseModel):
    """Request to start a new game."""
    starting_location: str = Field(default="Pallet Town", description="Starting location")
    personality: Optional[PersonalityTraits] = Field(default=None, description="Initial personality")

class SaveGameRequest(BaseModel):
    """Request to save the game."""
    save_name: str = Field(description="Name for the save file")

class LoadGameRequest(BaseModel):
    """Request to load a game."""
    save_name: str = Field(description="Name of the save file to load")

class CompressedContextResponse(BaseModel):
    """Response containing compressed story context."""
    compressed_summary: str = Field(description="Compressed story summary")
    active_promises: List[str] = Field(description="Active promises")
    key_relationships: List[str] = Field(description="Key relationships")
    location_context: List[str] = Field(description="Location-specific context")
    story_length: int = Field(description="Number of scenes in story")

class MemoryRequest(BaseModel):
    """Request to add a memory."""
    memory_type: str = Field(description="Type of memory (promise, friendship, etc.)")
    content: str = Field(description="Memory content")
    location: str = Field(description="Location where memory occurred")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data") 