"""
Core interfaces for the BeTheMC game system.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PersonalityTraits:
    """Player personality traits."""
    friendship: float
    courage: float
    curiosity: float
    wisdom: float
    determination: float

@dataclass
class Choice:
    """A choice option for the player."""
    text: str
    effects: Dict[str, float]

@dataclass
class NarrativeSegment:
    """A segment of the story narrative."""
    content: str
    location: str
    timestamp: datetime
    context: Dict[str, Any]

@dataclass
class Memory:
    """A memory entry."""
    memory_type: str
    content: str
    location: str
    timestamp: datetime
    metadata: Dict[str, Any]

class StoryGenerator(Protocol):
    """Interface for story generation components."""
    
    def generate_narrative(self, 
                          location: str,
                          personality: PersonalityTraits,
                          recent_events: List[str],
                          context: Dict[str, Any]) -> NarrativeSegment:
        """Generate a narrative segment."""
        ...
    
    def generate_choices(self,
                        situation: str,
                        personality: PersonalityTraits,
                        context: Dict[str, Any]) -> List[Choice]:
        """Generate choices for a situation."""
        ...

class KnowledgeBase(Protocol):
    """Interface for knowledge storage and retrieval."""
    
    def add_memory(self, memory: Memory) -> str:
        """Add a memory to the knowledge base."""
        ...
    
    def get_memories_by_type(self, memory_type: str, limit: int = 10) -> List[Memory]:
        """Get memories by type."""
        ...
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Get memories relevant to a query."""
        ...
    
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get information about a location."""
        ...

class ProgressionTracker(Protocol):
    """Interface for tracking story progression."""
    
    def add_scene(self, scene: Dict[str, Any]) -> None:
        """Add a scene to the progression."""
        ...
    
    def get_compressed_context(self, location: str) -> Dict[str, Any]:
        """Get compressed context for a location."""
        ...
    
    def get_story_context(self) -> Dict[str, Any]:
        """Get current story context."""
        ...

class GameState(Protocol):
    """Interface for game state management."""
    
    @property
    def location(self) -> str:
        """Current location."""
        ...
    
    @property
    def personality(self) -> PersonalityTraits:
        """Current personality."""
        ...
    
    @property
    def recent_events(self) -> List[str]:
        """Recent events."""
        ...
    
    def update_personality(self, effects: Dict[str, float]) -> None:
        """Update personality based on effects."""
        ...
    
    def add_event(self, event: str) -> None:
        """Add an event to recent events."""
        ...

class SaveManager(Protocol):
    """Interface for save/load operations."""
    
    def save_game(self, session_id: str, save_name: str, data: Dict[str, Any]) -> bool:
        """Save game data."""
        ...
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Load game data."""
        ...
    
    def list_saves(self) -> List[str]:
        """List available saves."""
        ...
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file."""
        ...

class ConfigProvider(Protocol):
    """Interface for configuration management."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        ...
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        ... 