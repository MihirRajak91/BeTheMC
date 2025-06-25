"""
Game state management for BeTheMC.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .interfaces import PersonalityTraits, GameState

@dataclass
class GameStateImpl:
    """Implementation of game state management."""
    
    location: str
    personality: PersonalityTraits
    recent_events: List[str] = field(default_factory=list)
    relationships: Dict[str, Any] = field(default_factory=dict)
    pokemon_partners: List[str] = field(default_factory=list)
    memories: List[str] = field(default_factory=list)
    max_recent_events: int = 5
    
    def update_personality(self, effects: Dict[str, float]) -> None:
        """Update personality based on effects."""
        for trait, effect in effects.items():
            if hasattr(self.personality, trait):
                current_value = getattr(self.personality, trait)
                new_value = max(0.0, min(1.0, current_value + effect))
                setattr(self.personality, trait, new_value)
    
    def add_event(self, event: str) -> None:
        """Add an event to recent events."""
        self.recent_events.insert(0, event)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
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
        """Create state from dictionary."""
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
        """Create a default game state."""
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