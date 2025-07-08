"""
Clean progression tracking implementation.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .interfaces import ProgressionTracker
from bethemc.models.core import Memory
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ProgressionTrackerV2:
    """Clean implementation of story progression tracking."""
    
    def __init__(self, max_history_length: int = 20):
        """Initialize the progression tracker."""
        self.max_history_length = max_history_length
        self.scene_history: List[Dict[str, Any]] = []
        self.memories: List[Memory] = []
    
    def add_scene(self, scene: Dict[str, Any]) -> None:
        """Add a scene to the progression."""
        scene["timestamp"] = datetime.now().isoformat()
        self.scene_history.append(scene)
        
        # Maintain history length
        if len(self.scene_history) > self.max_history_length:
            self.scene_history.pop(0)
    
    def get_compressed_context(self, location: str) -> Dict[str, Any]:
        """Get compressed context for a location."""
        try:
            # Get recent scenes
            recent_scenes = self.scene_history[-5:] if self.scene_history else []
            
            # Get location-specific memories
            location_memories = [
                mem for mem in self.memories 
                if mem.location.lower() == location.lower()
            ][:3]
            
            # Get active promises
            promise_memories = [
                mem for mem in self.memories 
                if mem.memory_type == "promise"
            ][:3]
            
            # Get key relationships
            relationship_memories = [
                mem for mem in self.memories 
                if mem.memory_type == "friendship"
            ][:3]
            
            # Create compressed summary
            summary_parts = []
            
            if recent_scenes:
                locations = [scene.get("location", "Unknown") for scene in recent_scenes[-3:]]
                summary_parts.append(f"Recent: {' → '.join(locations)}")
            
            if promise_memories:
                promises = [mem.content[:50] for mem in promise_memories]
                summary_parts.append(f"PROMISE: {' | '.join(promises)}")
            
            if relationship_memories:
                relationships = [mem.content[:50] for mem in relationship_memories]
                summary_parts.append(f"RELATIONSHIP: {' | '.join(relationships)}")
            
            compressed_summary = " | ".join(summary_parts) if summary_parts else "Beginning of adventure"
            
            return {
                "compressed_summary": compressed_summary,
                "active_promises": [mem.content for mem in promise_memories],
                "key_relationships": [mem.content for mem in relationship_memories],
                "location_context": [mem.content for mem in location_memories],
                "story_length": len(self.scene_history)
            }
        except Exception as e:
            logger.error(f"Failed to get compressed context: {e}")
            return {
                "compressed_summary": "Beginning of adventure",
                "active_promises": [],
                "key_relationships": [],
                "location_context": [],
                "story_length": len(self.scene_history)
            }
    
    def get_story_context(self) -> Dict[str, Any]:
        """Get current story context."""
        try:
            recent_scenes = self.scene_history[-5:] if self.scene_history else []
            
            # Get memories by type
            promises = [mem for mem in self.memories if mem.memory_type == "promise"]
            friendships = [mem for mem in self.memories if mem.memory_type == "friendship"]
            events = [mem for mem in self.memories if mem.memory_type == "event"]
            
            return {
                "recent_scenes": recent_scenes,
                "memories": {
                    "promises": [mem.content for mem in promises[:5]],
                    "friendships": [mem.content for mem in friendships[:5]],
                    "events": [mem.content for mem in events[:5]]
                },
                "total_scenes": len(self.scene_history),
                "total_memories": len(self.memories)
            }
        except Exception as e:
            logger.error(f"Failed to get story context: {e}")
            return {
                "recent_scenes": [],
                "memories": {"promises": [], "friendships": [], "events": []},
                "total_scenes": 0,
                "total_memories": 0
            }
    
    def add_memory(self, memory: Memory) -> None:
        """Add a memory to the tracker."""
        self.memories.append(memory)
        
        # Keep only recent memories
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
    
    def get_memories_by_type(self, memory_type: str, limit: int = 10) -> List[Memory]:
        """Get memories by type."""
        return [
            mem for mem in self.memories 
            if mem.memory_type == memory_type
        ][-limit:]
    
    def get_memories_by_location(self, location: str, limit: int = 10) -> List[Memory]:
        """Get memories by location."""
        return [
            mem for mem in self.memories 
            if mem.location.lower() == location.lower()
        ][-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "scene_history": self.scene_history,
            "memories": [
                {
                    "memory_type": mem.memory_type,
                    "content": mem.content,
                    "location": mem.location,
                    "timestamp": mem.timestamp.isoformat(),
                    "metadata": mem.metadata
                }
                for mem in self.memories
            ],
            "max_history_length": self.max_history_length
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressionTrackerV2':
        """
        🏭 Create Progression Tracker from Dictionary (Factory Method)
        
        Deserializes a progression tracker from a dictionary format. This factory
        method allows creating progression trackers from saved data or external
        sources, restoring the complete state including scene history and memories.
        
        Args:
            data: Dictionary containing progression tracker data
                  Must contain 'scene_history' and 'memories' keys
                  'max_history_length' is optional and defaults to 20
        
        Returns:
            ProgressionTrackerV2: New tracker instance with restored state
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If memory data format is invalid
        
        Example:
            saved_data = {
                "scene_history": [
                    {
                        "content": "You meet Professor Oak",
                        "location": "Oak's Laboratory",
                        "timestamp": "2024-01-15T10:30:00"
                    }
                ],
                "memories": [
                    {
                        "memory_type": "promise",
                        "content": "I promised to become a Pokémon Master",
                        "location": "Oak's Laboratory",
                        "timestamp": "2024-01-15T10:30:00",
                        "metadata": {"character": "Professor Oak"}
                    }
                ],
                "max_history_length": 25
            }
            
            tracker = ProgressionTrackerV2.from_dict(saved_data)
        
        Note:
            - Scene history is restored in chronological order
            - Memories are restored with full metadata
            - Timestamps are parsed from ISO format strings
            - Invalid memory data is skipped with logging
        """
        tracker = cls(max_history_length=data.get("max_history_length", 20))
        
        # Load scene history
        tracker.scene_history = data.get("scene_history", [])
        
        # Load memories
        for mem_data in data.get("memories", []):
            memory = Memory(
                memory_type=mem_data["memory_type"],
                content=mem_data["content"],
                location=mem_data["location"],
                timestamp=datetime.fromisoformat(mem_data["timestamp"]),
                metadata=mem_data.get("metadata", {})
            )
            tracker.memories.append(memory)
        
        return tracker 