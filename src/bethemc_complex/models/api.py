"""
🚀 Pydantic API Schemas for BeTheMC Complex Architecture

This module defines Pydantic models for API request/response validation
and serialization in the complex architecture. These schemas ensure
type safety, data validation, and clear API contracts between
the frontend and backend systems.

Key Features:
- Pydantic BaseModel for automatic validation and serialization
- Field constraints and validation rules
- Comprehensive examples for API documentation
- Clear separation between request and response models
- Type hints for IDE support and documentation

Architecture:
- Request models validate incoming API data
- Response models structure outgoing API data
- Field validation ensures data integrity
- Examples help with API testing and documentation

Usage:
    from bethemc_complex.models.api import (
        GameResponse, ChoiceRequest, StartGameRequest
    )
    
    # Validate incoming request
    request = ChoiceRequest(
        player_id="123e4567-e89b-12d3-a456-426614174000",
        choice_id="choice-1"
    )
    
    # Structure API response
    response = GameResponse(
        player_id="123e4567-e89b-12d3-a456-426614174000",
        player_name="Ash Ketchum",
        current_story={"id": "story-1", "title": "Welcome", "content": "..."},
        available_choices=[{"id": "choice-1", "text": "Help Pokémon"}],
        personality_traits={"courage": 7, "wisdom": 5},
        memories=[],
        game_progress={"current_location": "Pallet Town"}
    )
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PersonalityTraitsSchema(BaseModel):
    """
    🧠 Personality Traits API Schema
    
    Pydantic model for validating and serializing personality traits
    in API requests and responses. Each trait is an integer between 0
    and 10, representing the strength of that personality characteristic.
    
    Used in:
    - Game state responses
    - Personality update requests
    - Story generation context
    
    Validation:
    - All traits must be between 0 and 10
    - Automatic type conversion from JSON
    - Field-level validation with clear error messages
    """
    friendship: int = Field(ge=0, le=10)
    courage: int = Field(ge=0, le=10)
    curiosity: int = Field(ge=0, le=10)
    wisdom: int = Field(ge=0, le=10)
    determination: int = Field(ge=0, le=10)

class ChoiceSchema(BaseModel):
    """
    ⚡ Choice Option API Schema
    
    Pydantic model for representing choice options in API responses.
    Each choice has descriptive text and effects that modify the
    player's personality traits when selected.
    
    Used in:
    - Game state responses
    - Story generation responses
    - Choice processing
    
    Effects:
    - Positive values increase traits
    - Negative values decrease traits
    - Empty dict means no personality effects
    """
    text: str
    effects: Dict[str, float] = Field(default_factory=dict)

class NarrativeResponseSchema(BaseModel):
    """
    📖 Narrative Response API Schema
    
    Pydantic model for story generation responses that include
    narrative content, available choices, location context,
    and personality information for the AI story system.
    
    Used by:
    - Story generation API endpoints
    - AI narrative systems
    - Context management systems
    
    Components:
    - narrative: Generated story text
    - choices: Available player choices
    - location: Current story location
    - personality: Current player personality
    - active_promises: Unfulfilled commitments
    - key_relationships: Important character relationships
    - story_context: Additional story metadata
    """
    narrative: str
    choices: List[ChoiceSchema]
    location: str
    personality: PersonalityTraitsSchema
    active_promises: List[str] = Field(default_factory=list)
    key_relationships: List[str] = Field(default_factory=list)
    story_context: Dict[str, Any] = Field(default_factory=dict)

class GameStateSchema(BaseModel):
    """
    🎮 Game State API Schema
    
    Pydantic model for representing the complete game state
    in API responses. This schema provides a comprehensive
    view of the player's current situation and progress.
    
    Used in:
    - Game state retrieval endpoints
    - Save/load operations
    - Progress tracking
    
    Components:
    - location: Current game location
    - personality: Player personality traits
    - recent_events: Latest story developments
    - relationships: Character relationship status
    - pokemon_partners: Current Pokémon team
    - memories: Player's collected memories
    """
    location: str
    personality: PersonalityTraitsSchema
    recent_events: List[str] = Field(default_factory=list)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    pokemon_partners: List[str] = Field(default_factory=list)
    memories: List[str] = Field(default_factory=list)

class ChoiceRequestSchema(BaseModel):
    """
    🎯 Choice Request API Schema
    
    Pydantic model for validating choice selection requests.
    The choice_index represents the position of the selected
    choice in the available choices list.
    
    Used in:
    - Choice processing endpoints
    - Story advancement requests
    
    Validation:
    - choice_index must be non-negative
    - Represents array index of selected choice
    """
    choice_index: int = Field(ge=0)

class NewGameRequestSchema(BaseModel):
    """
    🆕 New Game Request API Schema
    
    Pydantic model for starting a new game session.
    Allows customization of starting location and
    optional personality traits.
    
    Used in:
    - Game initialization endpoints
    - New player registration
    
    Defaults:
    - starting_location: "Pallet Town"
    - personality: None (uses default balanced traits)
    """
    starting_location: str = Field(default="Pallet Town")
    personality: Optional[PersonalityTraitsSchema] = Field(default=None)

class SaveGameRequestSchema(BaseModel):
    """
    💾 Save Game Request API Schema
    
    Pydantic model for game save requests. The save_name
    is used to identify and retrieve the saved game later.
    
    Used in:
    - Game save endpoints
    - Save management operations
    
    Validation:
    - save_name must be provided
    - Used as unique identifier for save file
    """
    save_name: str

class LoadGameRequestSchema(BaseModel):
    """
    📂 Load Game Request API Schema
    
    Pydantic model for loading saved games. The save_name
    identifies which saved game to restore.
    
    Used in:
    - Game load endpoints
    - Save file management
    
    Validation:
    - save_name must match existing save file
    - Triggers game state restoration
    """
    save_name: str

class CompressedContextResponseSchema(BaseModel):
    """
    🗜️ Compressed Context Response API Schema
    
    Pydantic model for AI context compression responses.
    This schema provides a condensed summary of the game
    state for efficient AI processing and memory management.
    
    Used by:
    - AI story generation systems
    - Context optimization
    - Memory management
    
    Components:
    - compressed_summary: Condensed game state description
    - active_promises: Current unfulfilled commitments
    - key_relationships: Important character relationships
    - location_context: Current location and surroundings
    - story_length: Number of story segments generated
    """
    compressed_summary: str
    active_promises: List[str]
    key_relationships: List[str]
    location_context: List[str]
    story_length: int

class MemoryRequestSchema(BaseModel):
    """
    🧠 Memory Request API Schema
    
    Pydantic model for adding new memories to the player's
    memory bank. Memories influence story generation and
    provide context for future narrative decisions.
    
    Used in:
    - Memory addition endpoints
    - Story context building
    
    Components:
    - memory_type: Type of memory (promise, event, etc.)
    - content: Memory description
    - location: Where memory occurred
    - metadata: Additional context information
    """
    memory_type: str
    content: str
    location: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class APIResponseSchema(BaseModel):
    """
    📡 Generic API Response Schema
    
    Pydantic model for standardized API responses across
    all endpoints. Provides consistent success/error handling
    and optional data payload.
    
    Used in:
    - All API endpoints
    - Error handling
    - Success responses
    
    Components:
    - success: Boolean indicating operation success
    - message: Human-readable response message
    - data: Optional response payload
    """
    success: bool
    message: str
    data: Optional[Any] = None

class GameResponse(BaseModel):
    """Response model for game state information."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    player_name: str = Field(
        description="The player's name",
        example="Ash Ketchum"
    )
    current_story: Dict[str, Any] = Field(
        description="Current story segment with title, content, and location",
        example={
            "id": "story-123",
            "title": "Welcome to Kanto",
            "content": "You wake up in your room in Pallet Town, ready to begin your Pokémon adventure!",
            "location": "Pallet Town"
        }
    )
    available_choices: List[Dict[str, Any]] = Field(
        description="List of choices the player can make",
        example=[
            {
                "id": "choice-1",
                "text": "Visit Professor Oak's lab",
                "effects": {"curiosity": 1}
            },
            {
                "id": "choice-2", 
                "text": "Explore Pallet Town first",
                "effects": {"courage": 1}
            }
        ]
    )
    personality_traits: Dict[str, int] = Field(
        description="Player's current personality traits (0-10 scale)",
        example={"friendship": 5, "courage": 5, "curiosity": 5, "wisdom": 5, "determination": 5}
    )
    memories: List[Dict[str, Any]] = Field(
        description="Player's memories that influence the story",
        example=[]
    )
    game_progress: Dict[str, Any] = Field(
        description="Current game progress including location and completed events",
        example={
            "current_location": "Pallet Town",
            "completed_events": [],
            "relationships": {},
            "inventory": []
        }
    )

class ChoiceRequest(BaseModel):
    """Request model for making a choice in the game.
    This model is used to validate the request body for the choice endpoint.
    """
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    choice_id: str = Field(
        description="Unique identifier for the chosen option",
        example="choice-1"
    )

class ChoiceResponse(BaseModel):
    """Response model after making a choice."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    current_story: Dict[str, Any] = Field(
        description="Updated story after the choice",
        example={
            "id": "story-456",
            "title": "Story Continues",
            "content": "You chose: Visit Professor Oak's lab. The adventure continues...",
            "location": "Pallet Town"
        }
    )
    available_choices: List[Dict[str, Any]] = Field(
        description="New choices available after the decision",
        example=[
            {
                "id": "choice-3",
                "text": "Continue exploring",
                "effects": {"curiosity": 1}
            },
            {
                "id": "choice-4",
                "text": "Take a moment to reflect", 
                "effects": {"wisdom": 1}
            }
        ]
    )
    memories: List[Dict[str, Any]] = Field(
        description="Updated list of player memories",
        example=[]
    )
    game_progress: Dict[str, Any] = Field(
        description="Updated game progress including new completed events",
        example={
            "current_location": "Pallet Town",
            "completed_events": ["Visit Professor Oak's lab"],
            "relationships": {},
            "inventory": []
        }
    )

class SaveRequest(BaseModel):
    """Request model for saving a game."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    save_name: str = Field(
        description="Name for the save file",
        example="My Adventure - Pallet Town",
        min_length=1,
        max_length=100
    )

class LoadRequest(BaseModel):
    """Request model for loading a saved game."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    save_id: str = Field(
        description="Unique identifier for the save file to load",
        example="save-123"
    )

class MemoryRequest(BaseModel):
    """Request model for adding a memory."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    memory_text: str = Field(
        description="The memory content to add",
        example="I remember meeting Professor Oak for the first time",
        min_length=1,
        max_length=500
    )
    memory_type: str = Field(
        description="Type of memory (e.g., 'general', 'promise', 'relationship')",
        example="general",
        default="general"
    )

class PersonalityRequest(BaseModel):
    """Request model for updating personality traits."""
    
    player_id: str = Field(
        description="Unique identifier for the player",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    trait: str = Field(
        description="Personality trait to update",
        example="courage",
        pattern="^(courage|curiosity|wisdom|determination|friendship)$"
    )
    value: int = Field(
        description="New value for the trait (0-10 scale)",
        example=7,
        ge=0,
        le=10
    )

class StartGameRequest(BaseModel):
    """Request model for starting a new game."""
    
    player_name: str = Field(
        description="The name of the player starting the adventure",
        example="Ash Ketchum",
        min_length=1,
        max_length=50
    )
    personality_traits: Optional[Dict[str, int]] = Field(
        None,
        description="Optional custom personality traits (values 0-10). If not provided, all traits default to 5.",
        example={"courage": 7, "curiosity": 8, "wisdom": 6, "determination": 9, "friendship": 5}
    )   