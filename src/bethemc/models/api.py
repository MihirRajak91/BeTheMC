"""
Pydantic API schemas for BeTheMC.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PersonalityTraitsSchema(BaseModel):
    friendship: float = Field(ge=0.0, le=1.0)
    courage: float = Field(ge=0.0, le=1.0)
    curiosity: float = Field(ge=0.0, le=1.0)
    wisdom: float = Field(ge=0.0, le=1.0)
    determination: float = Field(ge=0.0, le=1.0)

class ChoiceSchema(BaseModel):
    text: str
    effects: Dict[str, float] = Field(default_factory=dict)

class NarrativeResponseSchema(BaseModel):
    narrative: str
    choices: List[ChoiceSchema]
    location: str
    personality: PersonalityTraitsSchema
    active_promises: List[str] = Field(default_factory=list)
    key_relationships: List[str] = Field(default_factory=list)
    story_context: Dict[str, Any] = Field(default_factory=dict)

class GameStateSchema(BaseModel):
    location: str
    personality: PersonalityTraitsSchema
    recent_events: List[str] = Field(default_factory=list)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    pokemon_partners: List[str] = Field(default_factory=list)
    memories: List[str] = Field(default_factory=list)

class ChoiceRequestSchema(BaseModel):
    choice_index: int = Field(ge=0)

class NewGameRequestSchema(BaseModel):
    starting_location: str = Field(default="Pallet Town")
    personality: Optional[PersonalityTraitsSchema] = Field(default=None)

class SaveGameRequestSchema(BaseModel):
    save_name: str

class LoadGameRequestSchema(BaseModel):
    save_name: str

class CompressedContextResponseSchema(BaseModel):
    compressed_summary: str
    active_promises: List[str]
    key_relationships: List[str]
    location_context: List[str]
    story_length: int

class MemoryRequestSchema(BaseModel):
    memory_type: str
    content: str
    location: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class APIResponseSchema(BaseModel):
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
    """Request model for making a choice in the game."""
    
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
    
    save_name: str = Field(
        description="Name for the save file",
        example="My Adventure - Pallet Town",
        min_length=1,
        max_length=100
    )

class LoadRequest(BaseModel):
    """Request model for loading a saved game."""
    
    save_id: str = Field(
        description="Unique identifier for the save file to load",
        example="save-123"
    )

class MemoryRequest(BaseModel):
    """Request model for adding a memory."""
    
    memory_text: str = Field(
        description="The memory content to add",
        example="I remember meeting Professor Oak for the first time",
        min_length=1,
        max_length=500
    )
    memory_type: str = Field(
        description="Type of memory (affects how it influences the story)",
        example="relationship",
        default="general"
    )

class PersonalityRequest(BaseModel):
    """Request model for updating personality traits."""
    
    trait: str = Field(
        description="Personality trait to update",
        example="courage",
        pattern="^(courage|curiosity|wisdom|determination|friendship)$"
    )
    value: int = Field(
        description="New value for the trait (0-10)",
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