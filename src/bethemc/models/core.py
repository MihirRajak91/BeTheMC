"""
Core Models - The fundamental game data structures.

This file contains the core models that represent the actual game data:
- Player: Information about the player
- Story: Story segments and content
- Choice: Player choices and their effects
- Memory: Player memories and experiences
- GameProgression: Player's progress through the game
- GameState: Complete game state

These models are used throughout the application for game logic and data storage.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


class Player(BaseModel):
    """
    Represents a player in the game.
    
    What this contains:
    - id: Unique identifier for the player
    - name: The player's chosen name
    - personality_traits: How the player behaves (friendship, courage, etc.)
    
    Example:
    Player(
        id="123-456-789",
        name="Ash",
        personality_traits={"friendship": 7, "courage": 8, "curiosity": 6}
    )
    """
    id: str = Field(..., description="Unique player ID")
    name: str = Field(..., description="Player's name")
    personality_traits: Dict[str, int] = Field(
        default_factory=lambda: {
            "friendship": 5,
            "courage": 5, 
            "curiosity": 5,
            "wisdom": 5,
            "determination": 5
        },
        description="Personality traits (0-10 scale)"
    )


class Story(BaseModel):
    """
    Represents a story segment in the game.
    
    What this contains:
    - id: Unique identifier for this story part
    - title: A short title for this story segment
    - content: The actual story text the player sees
    - location: Where this story takes place
    
    Example:
    Story(
        id="story-123",
        title="Welcome to Pallet Town",
        content="You wake up in your bedroom...",
        location="Pallet Town"
    )
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique story ID")
    title: str = Field(..., description="Story segment title")
    content: str = Field(..., description="Story text content")
    location: str = Field(..., description="Where this story takes place")


class Choice(BaseModel):
    """
    Represents a choice the player can make.
    
    What this contains:
    - id: Unique identifier for this choice
    - text: What the choice says (what the player sees)
    - effects: How this choice affects personality traits
    
    Example:
    Choice(
        id="choice-123",
        text="Help the injured Pokémon",
        effects={"friendship": 1, "wisdom": 1}
    )
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique choice ID")
    text: str = Field(..., description="Choice text displayed to player")
    effects: Dict[str, int] = Field(
        default_factory=dict,
        description="How this choice affects personality traits"
    )


class Memory(BaseModel):
    """
    Represents a memory the player has collected.
    
    What this contains:
    - id: Unique identifier for this memory
    - content: What the memory is about
    - memory_type: What kind of memory (promise, relationship, etc.)
    - timestamp: When this memory was created
    - location: Where this memory happened
    - metadata: Extra information about the memory
    
    Example:
    Memory(
        id="memory-123",
        content="I promised Professor Oak I would take care of Pikachu",
        memory_type="promise",
        timestamp=datetime.now(),
        location="Oak's Laboratory"
    )
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique memory ID")
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(default="general", description="Type of memory")
    timestamp: datetime = Field(default_factory=datetime.now, description="When memory was created")
    location: str = Field(default="", description="Where memory happened")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra memory data")


class GameProgression(BaseModel):
    """
    Tracks the player's progress through the game.
    
    What this contains:
    - current_location: Where the player is right now
    - completed_events: List of things the player has done
    - relationships: How the player relates to NPCs
    - inventory: Items the player has collected
    
    Example:
    GameProgression(
        current_location="Pallet Town",
        completed_events=["Met Professor Oak", "Chose starter Pokémon"],
        relationships={"Professor Oak": "friendly"},
        inventory=["Pokédex", "5 Pokéballs"]
    )
    """
    current_location: str = Field(..., description="Player's current location")
    completed_events: List[str] = Field(default_factory=list, description="Events player has completed")
    relationships: Dict[str, Any] = Field(default_factory=dict, description="NPC relationships")
    inventory: List[str] = Field(default_factory=list, description="Player's items")


class GameState(BaseModel):
    """
    The complete state of a player's game.
    
    This is the BIG MODEL that contains everything about a player's current game:
    - player: The player info (name, personality, etc.)
    - current_story: The story segment they're currently reading
    - available_choices: What choices they can make right now
    - memories: All the memories they've collected
    - progression: Their progress through the game
    
    This is what gets saved to the database and loaded when continuing a game.
    
    Example:
    GameState(
        player=Player(...),
        current_story=Story(...),
        available_choices=[Choice(...), Choice(...)],
        memories=[Memory(...), Memory(...)],
        progression=GameProgression(...)
    )
    """
    player: Player = Field(..., description="Player information")
    current_story: Story = Field(..., description="Current story segment")
    available_choices: List[Choice] = Field(..., description="Available choices")
    memories: List[Memory] = Field(default_factory=list, description="Player memories")
    progression: GameProgression = Field(..., description="Game progression") 