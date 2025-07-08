"""
🗄️ MongoDB Document Models for BeTheMC Complex Architecture

This module defines all MongoDB document models used in the complex architecture.
These models provide type safety, validation, and serialization for database operations.

Key Features:
- Custom ObjectId validation for MongoDB compatibility
- Pydantic models with comprehensive field validation
- Configurable serialization for JSON and MongoDB
- Support for complex nested document structures

Usage:
    from bethemc_complex.database.models import PlayerDocument, GameStateDocument
    
    # Create a player document
    player = PlayerDocument(
        player_id="uuid-123",
        name="Ash Ketchum",
        personality_traits={"courage": 7, "wisdom": 5}
    )
    
    # Save to MongoDB
    collection.insert_one(player.dict(by_alias=True))
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class ObjectIdStr(str):
    """
    🔧 Custom MongoDB ObjectId String Type
    
    A custom string type that validates and converts MongoDB ObjectId strings.
    This ensures type safety when working with MongoDB's _id fields.
    
    Features:
    - Validates ObjectId format before conversion
    - Integrates with Pydantic validation system
    - Handles MongoDB ObjectId serialization
    
    Example:
        # Valid ObjectId
        valid_id = ObjectIdStr("507f1f77bcf86cd799439011")
        
        # Invalid ObjectId (raises ValueError)
        invalid_id = ObjectIdStr("not-a-valid-id")  # ValueError: Invalid ObjectId
    """
    
    @classmethod
    def __get_validators__(cls):
        """
        🔍 Pydantic Validator Generator
        
        Yields the validation function for this custom type.
        Called by Pydantic during model validation.
        
        Returns:
            Generator yielding the validate method
        """
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        """
        ✅ Validate and Convert ObjectId String
        
        Validates that a string is a valid MongoDB ObjectId format
        and converts it to a proper ObjectId object.
        
        Args:
            v: String value to validate
            
        Returns:
            ObjectId: Valid MongoDB ObjectId object
            
        Raises:
            ValueError: If the string is not a valid ObjectId format
            
        Example:
            >>> ObjectIdStr.validate("507f1f77bcf86cd799439011")
            ObjectId('507f1f77bcf86cd799439011')
            
            >>> ObjectIdStr.validate("invalid")
            ValueError: Invalid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class PlayerDocument(BaseModel):
    """
    👤 Player Data MongoDB Document
    
    Represents a player's core data stored in MongoDB. This document
    contains all essential player information including identity, personality,
    and metadata for tracking player progress and preferences.
    
    Database Collection: players
    Index Fields: player_id (unique), name, created_at
    
    Schema:
        _id: MongoDB ObjectId (auto-generated)
        player_id: UUID string (unique identifier)
        name: Player's display name
        personality_traits: Dict of personality scores (0-10)
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
    
    Example:
        player = PlayerDocument(
            player_id="550e8400-e29b-41d4-a716-446655440000",
            name="Ash Ketchum",
            personality_traits={
                "friendship": 7,
                "courage": 8,
                "curiosity": 6,
                "wisdom": 5,
                "determination": 9
            }
        )
    """
    
    id: Optional[ObjectIdStr] = Field(
        default=None, 
        alias="_id",
        description="MongoDB ObjectId (auto-generated)"
    )
    player_id: str = Field(
        ..., 
        description="Unique UUID identifier for the player"
    )
    name: str = Field(
        ..., 
        description="Player's display name",
        min_length=1,
        max_length=50
    )
    personality_traits: Dict[str, int] = Field(
        ..., 
        description="Player's personality trait scores (0-10 scale)",
        example={
            "friendship": 7,
            "courage": 8,
            "curiosity": 6,
            "wisdom": 5,
            "determination": 9
        }
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when player account was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last player data update"
    )
    
    class Config:
        """
        🔧 Pydantic Configuration
        
        Configures how this model behaves during validation and serialization.
        
        Settings:
        - allow_population_by_field_name: Enables field aliases (_id ↔ id)
        - arbitrary_types_allowed: Allows custom ObjectIdStr type
        - json_encoders: Converts ObjectId to string for JSON serialization
        """
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class StoryDocument(BaseModel):
    """
    📖 Story Segment MongoDB Document
    
    Represents a single story segment or narrative piece in the game.
    Each story document contains the content, metadata, and location
    information needed to display story content to players.
    
    Used in: GameStateDocument, SaveDocument
    
    Schema:
        id: Unique story identifier
        title: Story segment title
        content: Full story text content
        location: Where this story takes place
    
    Example:
        story = StoryDocument(
            id="story-oak-lab-intro",
            title="Welcome to Professor Oak's Laboratory",
            content="You step into the bustling laboratory...",
            location="Oak's Laboratory"
        )
    """
    
    id: str = Field(
        ..., 
        description="Unique identifier for this story segment"
    )
    title: str = Field(
        ..., 
        description="Title of the story segment",
        min_length=1,
        max_length=200
    )
    content: str = Field(
        ..., 
        description="Full story text content",
        min_length=1
    )
    location: str = Field(
        ..., 
        description="Location where this story takes place",
        min_length=1,
        max_length=100
    )


class ChoiceDocument(BaseModel):
    """
    ⚡ Player Choice MongoDB Document
    
    Represents a choice option presented to the player during gameplay.
    Each choice has text content and effects that modify the player's
    personality traits when selected.
    
    Used in: GameStateDocument
    
    Schema:
        id: Unique choice identifier
        text: Choice text displayed to player
        effects: Dict of personality trait modifications
    
    Example:
        choice = ChoiceDocument(
            id="choice-help-pokemon",
            text="Help the injured Pokémon",
            effects={"friendship": 1, "courage": 1}
        )
    """
    
    id: str = Field(
        ..., 
        description="Unique identifier for this choice"
    )
    text: str = Field(
        ..., 
        description="Choice text displayed to the player",
        min_length=1,
        max_length=500
    )
    effects: Dict[str, int] = Field(
        default_factory=dict, 
        description="Personality trait effects when this choice is selected",
        example={"friendship": 1, "courage": 1, "wisdom": -1}
    )


class MemoryDocument(BaseModel):
    """
    🧠 Player Memory MongoDB Document
    
    Represents a memory or experience that the player has collected
    during their adventure. Memories influence story generation and
    provide context for future narrative decisions.
    
    Used in: GameStateDocument
    
    Schema:
        id: Unique memory identifier
        content: Memory description text
        memory_type: Type of memory (promise, friendship, event, etc.)
        timestamp: When the memory was created
    
    Memory Types:
        - promise: Commitments made to characters
        - friendship: Relationship developments
        - event: Significant story events
        - location: Place-specific memories
        - achievement: Accomplishments and milestones
    
    Example:
        memory = MemoryDocument(
            id="memory-oak-promise",
            content="I promised Professor Oak I would become a Pokémon Master",
            memory_type="promise",
            timestamp=datetime.utcnow()
        )
    """
    
    id: str = Field(
        ..., 
        description="Unique identifier for this memory"
    )
    content: str = Field(
        ..., 
        description="Memory content and description",
        min_length=1,
        max_length=1000
    )
    memory_type: str = Field(
        ..., 
        description="Type of memory (promise, friendship, event, location, achievement)",
        example="promise"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this memory was created"
    )


class GameProgressionDocument(BaseModel):
    """
    🎯 Game Progression MongoDB Document
    
    Tracks the player's progress through the game world, including
    current location, completed events, relationships, and inventory.
    This document provides context for story generation and save/load operations.
    
    Used in: GameStateDocument
    
    Schema:
        current_location: Player's current location
        completed_events: List of completed story events
        relationships: Dict of character relationship data
        inventory: List of items the player possesses
    
    Example:
        progression = GameProgressionDocument(
            current_location="Viridian City",
            completed_events=["Met Professor Oak", "Chose starter Pokémon"],
            relationships={"Professor Oak": "mentor", "Mom": "family"},
            inventory=["Pokédex", "5 Pokéballs", "Running Shoes"]
        )
    """
    
    current_location: str = Field(
        ..., 
        description="Player's current location in the game world",
        min_length=1,
        max_length=100
    )
    completed_events: List[str] = Field(
        default_factory=list, 
        description="List of completed story events and achievements",
        example=["Met Professor Oak", "Chose Charmander", "Won first battle"]
    )
    relationships: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Character relationships and their current status",
        example={"Professor Oak": "mentor", "Misty": "rival", "Brock": "friend"}
    )
    inventory: List[str] = Field(
        default_factory=list, 
        description="Items currently in player's inventory",
        example=["Pokédex", "10 Pokéballs", "Bicycle", "HM01"]
    )


class GameStateDocument(BaseModel):
    """
    🎮 Complete Game State MongoDB Document
    
    The primary document representing a player's complete game state.
    This document contains all current game information including
    story, choices, memories, and progression data.
    
    Database Collection: game_states
    Index Fields: player_id (unique)
    
    Schema:
        _id: MongoDB ObjectId (auto-generated)
        player_id: UUID string (links to PlayerDocument)
        current_story: Current story segment being displayed
        available_choices: Choices currently available to player
        memories: List of player's collected memories
        progression: Current game progression data
        last_updated: Timestamp of last state update
    
    Relationships:
        - Links to PlayerDocument via player_id
        - Contains StoryDocument for current story
        - Contains multiple ChoiceDocument objects
        - Contains multiple MemoryDocument objects
        - Contains GameProgressionDocument for progress
    
    Example:
        game_state = GameStateDocument(
            player_id="550e8400-e29b-41d4-a716-446655440000",
            current_story=StoryDocument(...),
            available_choices=[ChoiceDocument(...), ChoiceDocument(...)],
            memories=[MemoryDocument(...), MemoryDocument(...)],
            progression=GameProgressionDocument(...)
        )
    """
    
    id: Optional[ObjectIdStr] = Field(
        default=None, 
        alias="_id",
        description="MongoDB ObjectId (auto-generated)"
    )
    player_id: str = Field(
        ..., 
        description="UUID player identifier (links to PlayerDocument)"
    )
    current_story: StoryDocument = Field(
        ..., 
        description="Current story segment being displayed to the player"
    )
    available_choices: List[ChoiceDocument] = Field(
        ..., 
        description="Choice options currently available to the player"
    )
    memories: List[MemoryDocument] = Field(
        default_factory=list, 
        description="Player's collected memories and experiences"
    )
    progression: GameProgressionDocument = Field(
        ..., 
        description="Current game progression and location data"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last game state update"
    )
    
    class Config:
        """
        🔧 Pydantic Configuration
        
        Configures MongoDB compatibility and serialization behavior.
        
        Settings:
        - allow_population_by_field_name: Enables _id ↔ id field mapping
        - arbitrary_types_allowed: Allows custom ObjectIdStr type
        - json_encoders: Converts ObjectId to string for JSON serialization
        """
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SaveDocument(BaseModel):
    """
    💾 Game Save MongoDB Document
    
    Represents a saved game state that players can load later.
    Each save document contains a complete snapshot of the game
    state at the time of saving, allowing players to resume
    their adventure from any saved point.
    
    Database Collection: saves
    Index Fields: player_id, save_id (unique), created_at
    
    Schema:
        _id: MongoDB ObjectId (auto-generated)
        save_id: UUID string (unique save identifier)
        player_id: UUID string (links to PlayerDocument)
        save_name: User-friendly save name
        game_state: Complete GameStateDocument snapshot
        save_type: Type of save (full/summarized)
        created_at: When the save was created
        file_size_bytes: Estimated save file size
    
    Save Types:
        - full: Complete game state (larger, more detailed)
        - summarized: Compressed state (smaller, less detail)
    
    Example:
        save = SaveDocument(
            save_id="save-12345678-1234-1234-1234-123456789abc",
            player_id="550e8400-e29b-41d4-a716-446655440000",
            save_name="Before Gym Battle",
            game_state=GameStateDocument(...),
            save_type="full"
        )
    """
    
    id: Optional[ObjectIdStr] = Field(
        default=None, 
        alias="_id",
        description="MongoDB ObjectId (auto-generated)"
    )
    save_id: str = Field(
        ..., 
        description="Unique UUID identifier for this save file"
    )
    player_id: str = Field(
        ..., 
        description="UUID player identifier (links to PlayerDocument)"
    )
    save_name: str = Field(
        ..., 
        description="User-friendly name for this save file",
        min_length=1,
        max_length=100
    )
    game_state: GameStateDocument = Field(
        ..., 
        description="Complete snapshot of the game state at save time"
    )
    save_type: str = Field(
        default="full", 
        description="Type of save (full/summarized)",
        example="full"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this save was created"
    )
    file_size_bytes: Optional[int] = Field(
        default=None, 
        description="Estimated size of save data in bytes"
    )
    
    class Config:
        """
        🔧 Pydantic Configuration
        
        Configures MongoDB compatibility and serialization behavior.
        
        Settings:
        - allow_population_by_field_name: Enables _id ↔ id field mapping
        - arbitrary_types_allowed: Allows custom ObjectIdStr type
        - json_encoders: Converts ObjectId to string for JSON serialization
        """
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 