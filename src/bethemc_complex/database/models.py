"""
MongoDB document models for BeTheMC.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class ObjectIdStr(str):
    """Custom ObjectId type for MongoDB."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class PlayerDocument(BaseModel):
    """MongoDB document for player data."""
    
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    player_id: str = Field(..., description="UUID player identifier")
    name: str = Field(..., description="Player name")
    personality_traits: Dict[str, int] = Field(..., description="Player personality traits")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class StoryDocument(BaseModel):
    """Story segment document."""
    
    id: str = Field(..., description="Story ID")
    title: str = Field(..., description="Story title")
    content: str = Field(..., description="Story content")
    location: str = Field(..., description="Story location")


class ChoiceDocument(BaseModel):
    """Choice document."""
    
    id: str = Field(..., description="Choice ID")
    text: str = Field(..., description="Choice text")
    effects: Dict[str, int] = Field(default_factory=dict, description="Choice effects")


class MemoryDocument(BaseModel):
    """Memory document."""
    
    id: str = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(..., description="Memory type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GameProgressionDocument(BaseModel):
    """Game progression document."""
    
    current_location: str = Field(..., description="Current location")
    completed_events: List[str] = Field(default_factory=list, description="Completed events")
    relationships: Dict[str, Any] = Field(default_factory=dict, description="Character relationships")
    inventory: List[str] = Field(default_factory=list, description="Player inventory")


class GameStateDocument(BaseModel):
    """MongoDB document for game state."""
    
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    player_id: str = Field(..., description="UUID player identifier")
    current_story: StoryDocument = Field(..., description="Current story")
    available_choices: List[ChoiceDocument] = Field(..., description="Available choices")
    memories: List[MemoryDocument] = Field(default_factory=list, description="Player memories")
    progression: GameProgressionDocument = Field(..., description="Game progression")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SaveDocument(BaseModel):
    """MongoDB document for save data."""
    
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    save_id: str = Field(..., description="UUID save identifier")
    player_id: str = Field(..., description="UUID player identifier")
    save_name: str = Field(..., description="Save name")
    game_state: GameStateDocument = Field(..., description="Saved game state")
    save_type: str = Field(default="full", description="Save type (full/summarized)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_size_bytes: Optional[int] = Field(default=None, description="Estimated file size")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 