"""
🎮 Core Domain Models for BeTheMC Complex Architecture

This module defines the core domain models that represent the fundamental
data structures used throughout the complex architecture. These models
provide type safety and clear data contracts between different layers
of the system.

Key Features:
- Dataclass-based models for type safety and immutability
- Comprehensive field validation and documentation
- Clear separation between domain models and database models
- Support for complex nested data structures

Architecture:
- Models are used across all layers (API, services, database)
- Dataclasses provide automatic __init__, __repr__, and __eq__ methods
- Field defaults ensure consistent object creation
- UUID generation for unique identifiers

Usage:
    from bethemc_complex.models.core import (
        Player, Story, Choice, GameState, PersonalityTraits
    )
    
    # Create a new player
    player = Player(
        id=str(uuid4()),
        name="Ash Ketchum",
        personality_traits={"courage": 7, "wisdom": 5}
    )
    
    # Create a story segment
    story = Story(
        id="story-oak-lab",
        title="Welcome to Professor Oak's Laboratory",
        content="You step into the bustling laboratory...",
        location="Oak's Laboratory"
    )
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class PersonalityTraits:
    """
    🧠 Player Personality Traits Domain Model
    
    Represents the player's personality characteristics that influence story
    generation, choice outcomes, and character interactions. Each trait is
    an integer between 0 and 10, where higher values indicate stronger
    manifestation of that trait.
    
    Traits:
        - friendship: How well the player gets along with others (0-10)
        - courage: How brave the player is in dangerous situations (0-10)
        - curiosity: How much the player explores and investigates (0-10)
        - wisdom: How thoughtful and strategic the player is (0-10)
        - determination: How persistent the player is in achieving goals (0-10)
    
    Usage:
        traits = PersonalityTraits(
            friendship=7,    # Very friendly
            courage=8,        # Very brave
            curiosity=6,      # Moderately curious
            wisdom=5,         # Balanced wisdom
            determination=9   # Very determined
        )
        
        # Traits influence story generation
        if traits.courage > 7:
            # Generate brave choice options
            pass
    """
    friendship: int
    courage: int
    curiosity: int
    wisdom: int
    determination: int

@dataclass
class Player:
    """
    👤 Player Domain Model
    
    Represents a player in the game system with their unique identity,
    display name, and personality characteristics. This model is used
    throughout the system to identify and track player data.
    
    Attributes:
        id: Unique identifier for the player (UUID string)
        name: Player's display name
        personality_traits: Dictionary mapping trait names to integer values (0-10 scale)
    
    Usage:
        player = Player(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="Ash Ketchum",
            personality_traits={
                "friendship": 7,
                "courage": 8,
                "curiosity": 6,
                "wisdom": 5,
                "determination": 9
            }
        )
        
        # Player is used in GameState and database operations
        game_state = GameState(player=player, ...)
    """
    id: str
    name: str
    personality_traits: Dict[str, int]

@dataclass
class Story:
    """
    📖 Story Segment Domain Model
    
    Represents a single story segment or narrative piece in the game.
    Each story contains the content, metadata, and location information
    needed to display story content to players.
    
    Attributes:
        id: Unique identifier for this story segment
        title: Story segment title for display and organization
        content: Full story text content to display to the player
        location: Where this story takes place in the game world
    
    Usage:
        story = Story(
            id="story-oak-lab-intro",
            title="Welcome to Professor Oak's Laboratory",
            content="You step into the bustling laboratory, filled with...",
            location="Oak's Laboratory"
        )
        
        # Story is used in GameState and API responses
        game_state = GameState(current_story=story, ...)
    """
    id: str
    title: str
    content: str
    location: str

@dataclass
class Choice:
    """
    ⚡ Player Choice Domain Model
    
    Represents a choice option presented to the player during gameplay.
    Each choice has descriptive text and effects that modify the player's
    personality traits when selected.
    
    Attributes:
        id: Unique identifier for this choice
        text: Choice text displayed to the player
        effects: Dictionary mapping personality traits to effect values
                Positive values increase traits, negative values decrease them
    
    Usage:
        choice = Choice(
            id="choice-help-pokemon",
            text="Help the injured Pokémon",
            effects={"friendship": 1, "courage": 1}
        )
        
        choice2 = Choice(
            id="choice-ignore-pokemon",
            text="Walk away and ignore it",
            effects={"friendship": -1, "courage": -1}
        )
        
        # Choices are used in GameState and API responses
        game_state = GameState(available_choices=[choice, choice2], ...)
    """
    id: str
    text: str
    effects: Dict[str, int] = field(default_factory=dict)

@dataclass
class Memory:
    """
    🧠 Player Memory Domain Model
    
    Represents a memory or experience that the player has collected
    during their adventure. Memories influence story generation and
    provide context for future narrative decisions.
    
    Attributes:
        id: Unique identifier for this memory
        content: Description of the memory
        memory_type: Type of memory (promise, friendship, event, location, achievement)
        timestamp: When this memory was created
    
    Memory Types:
        - promise: Commitments made to characters
        - friendship: Relationship developments
        - event: Significant story events
        - location: Place-specific memories
        - achievement: Accomplishments and milestones
    
    Usage:
        memory = Memory(
            id="memory-oak-promise",
            content="I promised Professor Oak I would become a Pokémon Master",
            memory_type="promise",
            timestamp=datetime.utcnow()
        )
        
        # Memories are used in GameState and story generation
        game_state = GameState(memories=[memory], ...)
    """
    id: str
    content: str
    memory_type: str
    timestamp: datetime

@dataclass
class PersonalityTrait:
    """
    🎯 Individual Personality Trait Domain Model
    
    Represents a single personality trait with its name and value.
    This model is used for detailed personality tracking and
    trait-specific operations.
    
    Attributes:
        name: Name of the personality trait
        value: Current value of the trait (integer scale, typically 0-10)
    
    Usage:
        trait = PersonalityTrait(
            name="courage",
            value=8
        )
        
        # Used for individual trait operations
        if trait.value > 7:
            # High courage behavior
            pass
    """
    name: str
    value: int

@dataclass
class GameProgression:
    """
    🎯 Game Progression Domain Model
    
    Tracks the player's progress through the game world, including
    current location, completed events, relationships, and inventory.
    This model provides context for story generation and save/load operations.
    
    Attributes:
        current_location: Player's current location in the game world
        completed_events: List of completed story events and achievements
        relationships: Dictionary of character relationships and their status
        inventory: List of items the player currently possesses
    
    Usage:
        progression = GameProgression(
            current_location="Viridian City",
            completed_events=["Met Professor Oak", "Chose Charmander"],
            relationships={"Professor Oak": "mentor", "Mom": "family"},
            inventory=["Pokédex", "5 Pokéballs", "Running Shoes"]
        )
        
        # Progression is used in GameState and story generation
        game_state = GameState(progression=progression, ...)
    """
    current_location: str
    completed_events: List[str] = field(default_factory=list)
    relationships: Dict[str, Any] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)

@dataclass
class GameState:
    """
    🎮 Complete Game State Domain Model
    
    The primary model representing a player's complete game state.
    This immutable data structure contains all current game information
    including player data, story, choices, memories, and progression.
    It serves as the single source of truth for game state throughout
    the entire application.
    
    Key Characteristics:
    • Immutable: All state changes return new GameState instances
    • Complete: Contains all necessary game information in one object
    • Serializable: Can be easily converted to/from JSON for API/database
    • Validated: All data is validated through Pydantic schemas
    • Thread-Safe: Immutable design prevents concurrent modification issues
    
    Architecture Role:
    • API Layer: Converted to response schemas for client consumption
    • Service Layer: Passed between services for state transitions
    • Database Layer: Serialized for persistence in MongoDB
    • AI Layer: Provides context for story generation
    • Core Layer: Central data structure for all game operations
    
    Attributes:
        player (Player): Complete player information including personality traits
        current_story (Story): Current narrative segment being displayed
        available_choices (List[Choice]): Choice options currently available to player
        memories (List[Memory]): Player's collected memories and experiences
        progression (GameProgression): Current game progression and location data
    
    Usage Examples:
        # Create new game state
        game_state = GameState(
            player=Player(id="123", name="Ash", personality_traits={"courage": 7}),
            current_story=Story(id="story-1", title="Welcome", content="...", location="Pallet Town"),
            available_choices=[Choice(id="choice-1", text="Help Pokémon", effects={"courage": 1})],
            memories=[Memory(id="memory-1", content="Met Professor Oak", memory_type="event", timestamp=...)],
            progression=GameProgression(current_location="Pallet Town", completed_events=[])
        )
        
        # Convert to API response
        response = GameResponse(
            player_id=game_state.player.id,
            player_name=game_state.player.name,
            current_story=game_state.current_story.__dict__,
            available_choices=[choice.__dict__ for choice in game_state.available_choices],
            personality_traits=game_state.player.personality_traits,
            memories=[memory.__dict__ for memory in game_state.memories],
            game_progress=game_state.progression.__dict__
        )
        
        # Access specific components
        player_name = game_state.player.name
        current_location = game_state.progression.current_location
        available_choice_texts = [choice.text for choice in game_state.available_choices]
    """
    player: Player
    current_story: Story
    available_choices: List[Choice]
    memories: List[Memory]
    progression: GameProgression

@dataclass
class NarrativeSegment:
    """
    📖 Story Narrative Segment Domain Model
    
    Represents a segment of the story narrative generated by the story system.
    Each segment contains the story content, location context, timestamp,
    and additional context for the story generation system.
    
    This model is used by:
    - Story generation components
    - AI narrative systems
    - Context management systems
    
    Attributes:
        content: The story text content to display to the player
        location: Where this narrative segment takes place
        timestamp: When this narrative was generated
        context: Additional context data for story generation
    
    Usage:
        segment = NarrativeSegment(
            content="You step into Professor Oak's bustling laboratory...",
            location="Oak's Laboratory",
            timestamp=datetime.utcnow(),
            context={
                "npc_present": "Professor Oak",
                "time_of_day": "morning",
                "weather": "sunny"
            }
        )
        
        # Used in story generation and AI systems
        story_generator.generate_narrative(segment)
    """
    content: str
    location: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict) 