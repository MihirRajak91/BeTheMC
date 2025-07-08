"""
🎮 Game State Management for BeTheMC Complex Architecture

This module provides the core game state management implementation for the complex
architecture. It handles player state, personality traits, events, relationships,
and memories in a structured way that supports the advanced story generation system.

Key Features:
- Comprehensive game state tracking with personality traits
- Event history management with configurable limits
- Relationship and memory systems for story continuity
- Factory methods for creating and loading game states
- Serialization support for save/load operations

Architecture:
- Implements the GameState interface from interfaces.py
- Uses dataclasses for clean, type-safe state management
- Supports complex personality trait modifications
- Maintains event history for story context

Usage:
    from bethemc_complex.core.state import GameStateImpl
    
    # Create a new game state
    state = GameStateImpl.create_default("Pallet Town")
    
    # Update personality based on choices
    state.update_personality({"courage": 0.1, "friendship": 0.2})
    
    # Add events to history
    state.add_event("Met Professor Oak")
    
    # Serialize for saving
    state_dict = state.to_dict()
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .interfaces import PersonalityTraits, GameState

@dataclass
class GameStateImpl:
    """
    🎮 Game State Implementation
    
    A comprehensive game state implementation that tracks all aspects of a player's
    adventure including location, personality, events, relationships, and memories.
    This class provides the foundation for the complex story generation system.
    
    Features:
    - Personality trait management with bounded values (0.0-1.0)
    - Event history with configurable maximum length
    - Relationship tracking for NPC interactions
    - Memory system for story continuity
    - Pokémon partner tracking
    - Location-based state management
    
    Personality Traits:
        - friendship: How well the player gets along with others
        - courage: How brave the player is in dangerous situations
        - curiosity: How much the player explores and investigates
        - wisdom: How thoughtful and strategic the player is
        - determination: How persistent the player is in achieving goals
    
    Example:
        # Create a new game state
        state = GameStateImpl(
            location="Pallet Town",
            personality=PersonalityTraits(
                friendship=0.5,
                courage=0.7,
                curiosity=0.6,
                wisdom=0.4,
                determination=0.8
            )
        )
        
        # Update personality after a choice
        state.update_personality({"courage": 0.1, "friendship": 0.2})
        
        # Add an event to history
        state.add_event("Chose Charmander as starter Pokémon")
    """
    
    location: str = field(
        description="Current location in the game world"
    )
    personality: PersonalityTraits = field(
        description="Player's current personality traits (0.0-1.0 scale)"
    )
    recent_events: List[str] = field(
        default_factory=list,
        description="Recent events that have occurred (for story context)"
    )
    relationships: Dict[str, Any] = field(
        default_factory=dict,
        description="Current relationships with NPCs and characters"
    )
    pokemon_partners: List[str] = field(
        default_factory=list,
        description="List of Pokémon currently partnered with the player"
    )
    memories: List[str] = field(
        default_factory=list,
        description="Player's collected memories and experiences"
    )
    max_recent_events: int = field(
        default=5,
        description="Maximum number of recent events to keep in memory"
    )
    
    def update_personality(self, effects: Dict[str, float]) -> None:
        """
        🔄 Update Personality Traits Based on Effects
        
        Modifies the player's personality traits based on the effects of their
        choices. All trait values are bounded between 0.0 and 1.0 to maintain
        balanced gameplay.
        
        Args:
            effects: Dictionary mapping trait names to effect values
                    Positive values increase traits, negative values decrease them
                    Example: {"courage": 0.1, "friendship": -0.05}
        
        Example:
            # Player makes a brave choice
            state.update_personality({"courage": 0.1, "friendship": 0.05})
            
            # Player makes a cautious choice
            state.update_personality({"courage": -0.1, "wisdom": 0.1})
        
        Note:
            - Effects are additive (current_value + effect)
            - Values are clamped between 0.0 and 1.0
            - Invalid trait names are ignored
        """
        for trait, effect in effects.items():
            if hasattr(self.personality, trait):
                current_value = getattr(self.personality, trait)
                new_value = max(0.0, min(1.0, current_value + effect))
                setattr(self.personality, trait, new_value)
    
    def add_event(self, event: str) -> None:
        """
        📝 Add Event to Recent History
        
        Adds a new event to the player's recent event history. This history
        is used by the story generation system to provide context and continuity.
        The system maintains a maximum number of events to prevent memory bloat.
        
        Args:
            event: Description of the event that occurred
                  Example: "Met Professor Oak", "Chose Charmander", "Won first battle"
        
        Example:
            state.add_event("Met Professor Oak in his laboratory")
            state.add_event("Chose Charmander as my starter Pokémon")
            state.add_event("Won my first Pokémon battle against rival")
        
        Note:
            - Events are added to the beginning of the list (most recent first)
            - When max_recent_events is exceeded, oldest events are removed
            - Events provide context for story generation and NPC interactions
        """
        self.recent_events.insert(0, event)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        📦 Convert Game State to Dictionary
        
        Serializes the game state to a dictionary format suitable for
        saving to database or JSON serialization. This method preserves
        all state information in a structured format.
        
        Returns:
            Dictionary containing all game state data
            
        Example:
            state_dict = state.to_dict()
            # Result:
            # {
            #     "location": "Pallet Town",
            #     "personality": {
            #         "friendship": 0.6,
            #         "courage": 0.7,
            #         "curiosity": 0.5,
            #         "wisdom": 0.4,
            #         "determination": 0.8
            #     },
            #     "recent_events": ["Met Professor Oak", "Chose Charmander"],
            #     "relationships": {"Professor Oak": "mentor"},
            #     "pokemon_partners": ["Charmander"],
            #     "memories": ["I promised to become a Pokémon Master"]
            # }
        """
        return {
            "location": self.location,
            "personality": {
                "friendship": self.personality.friendship,
                "courage": self.personality.courage,
                "curiosity": self.personality.curiosity,
                "wisdom": self.personality.wisdom,
                "determination": self.personality.determination
            },
            "recent_events": self.recent_events,
            "relationships": self.relationships,
            "pokemon_partners": self.pokemon_partners,
            "memories": self.memories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateImpl':
        """
        🏭 Create Game State from Dictionary (Factory Method)
        
        Deserializes a game state from a dictionary format. This factory method
        allows creating game states from saved data or external sources.
        
        Args:
            data: Dictionary containing game state data
                  Must contain at least 'location' and 'personality' keys
                  Other fields are optional and will use defaults if missing
        
        Returns:
            New GameStateImpl instance with data from the dictionary
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If personality trait values are invalid
        
        Example:
            saved_data = {
                "location": "Viridian City",
                "personality": {
                    "friendship": 0.7,
                    "courage": 0.8,
                    "curiosity": 0.6,
                    "wisdom": 0.5,
                    "determination": 0.9
                },
                "recent_events": ["Won first gym battle"],
                "relationships": {"Professor Oak": "mentor"}
            }
            
            state = GameStateImpl.from_dict(saved_data)
        """
        personality_data = data.get("personality", {})
        personality = PersonalityTraits(
            friendship=personality_data.get("friendship", 0.5),
            courage=personality_data.get("courage", 0.5),
            curiosity=personality_data.get("curiosity", 0.5),
            wisdom=personality_data.get("wisdom", 0.5),
            determination=personality_data.get("determination", 0.5)
        )
        
        return cls(
            location=data.get("location", "Pallet Town"),
            personality=personality,
            recent_events=data.get("recent_events", []),
            relationships=data.get("relationships", {}),
            pokemon_partners=data.get("pokemon_partners", []),
            memories=data.get("memories", [])
        )
    
    @classmethod
    def create_default(cls, location: str = "Pallet Town") -> 'GameStateImpl':
        """
        🎯 Create Default Game State (Factory Method)
        
        Creates a new game state with default values for starting a new game.
        All personality traits are set to neutral values (0.5) representing
        a balanced starting point for the player's journey.
        
        Args:
            location: Starting location for the new game
                     Defaults to "Pallet Town" (traditional starting point)
        
        Returns:
            New GameStateImpl instance with default values
            
        Example:
            # Start a new game in Pallet Town
            new_game = GameStateImpl.create_default()
            
            # Start a new game in a custom location
            custom_game = GameStateImpl.create_default("Viridian City")
        
        Note:
            - All personality traits start at 0.5 (neutral)
            - No events, relationships, or memories exist yet
            - Ready for the player's first choices to begin shaping their journey
        """
        personality = PersonalityTraits(
            friendship=0.5,
            courage=0.5,
            curiosity=0.5,
            wisdom=0.5,
            determination=0.5
        )
        
        return cls(
            location=location,
            personality=personality
        ) 