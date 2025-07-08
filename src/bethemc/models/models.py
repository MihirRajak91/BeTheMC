"""
Simple Models - All game data structures in one place!

This file contains ALL the data models for the BeTheMC game.
Everything is in one place and clearly explained!

🎯 WHAT'S IN THIS FILE:
1. Core Game Models (Player, Story, Choice, etc.)
2. API Request/Response Models  
3. Clear explanations of what each model does

No complex inheritance or confusing abstractions - just simple, clear data structures!
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


# =============================================================================
# 🎮 CORE GAME MODELS
# These represent the actual game data (players, stories, choices, etc.)
# =============================================================================

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


# =============================================================================
# 🌐 API REQUEST/RESPONSE MODELS
# These are for communicating with the web frontend
# =============================================================================

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
        description="Optional starting personality traits"
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


# =============================================================================
# 🎯 SIMPLE EXPLANATION OF ALL MODELS
# =============================================================================

"""
📋 CORE GAME MODELS (the actual game data):
1. Player - Who is playing (name, personality)
2. Story - A piece of the story (title, content, location)
3. Choice - Something the player can choose to do
4. Memory - Something the player remembers
5. GameProgression - How far the player has gotten
6. GameState - Everything about the player's current game

🌐 API MODELS (for talking to the frontend):
1. StartGameRequest - "I want to start a new game"
2. ChoiceRequest - "I want to make this choice"
3. SaveRequest - "I want to save my game"
4. LoadRequest - "I want to load this save"
5. GameResponse - "Here's your complete game state"
6. ChoiceResponse - "Here's what happened after your choice"

That's it! Just 12 simple models that handle everything in the game.
No complex inheritance, no confusing abstractions - just clear, simple data structures!
""" 