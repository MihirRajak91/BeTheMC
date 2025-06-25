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
    player_id: str
    player_name: str
    current_story: Dict[str, Any]
    available_choices: List[Dict[str, Any]]
    personality_traits: Dict[str, int]
    memories: List[Dict[str, Any]]
    game_progress: Dict[str, Any]

class ChoiceRequest(BaseModel):
    player_id: str
    choice_id: str

class ChoiceResponse(BaseModel):
    player_id: str
    current_story: Dict[str, Any]
    available_choices: List[Dict[str, Any]]
    memories: List[Dict[str, Any]]
    game_progress: Dict[str, Any]

class SaveRequest(BaseModel):
    player_id: str
    save_name: str

class LoadRequest(BaseModel):
    player_id: str
    save_id: str

class MemoryRequest(BaseModel):
    player_id: str
    memory_text: str
    memory_type: str = "general"

class PersonalityRequest(BaseModel):
    player_id: str
    trait: str
    value: int 