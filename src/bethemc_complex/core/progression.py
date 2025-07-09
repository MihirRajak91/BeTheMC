"""
Progression and quest management for BeTheMC game.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from ..data.vector_store import KantoKnowledgeBase

@dataclass
class StoryMemory:
    """A simple memory entry that stores narrative elements."""
    memory_type: str  # 'promise', 'event', 'relationship', 'location'
    content: str      # The actual memory content
    timestamp: float  # When the memory was created
    metadata: dict    # Additional context (e.g., character names, locations)

class ProgressionManager:
    def __init__(self, config):
        """Initialize the progression manager."""
        self.config = config
        self.knowledge_base = KantoKnowledgeBase(config)
        self.scene_history: List[dict] = []
        self.max_history_length = config.get("story.max_history_length", 20)
        
        # Load progression data if exists
        self._load_progression()

    def _load_progression(self):
        """Load progression data from save file."""
        save_dir = self.config.get("save_dir", "data/saves")
        save_file = Path(save_dir) / "progression.json"
        if save_file.exists():
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.scene_history = data.get("scene_history", [])

    def _save_progression(self):
        """Save progression data to file."""
        save_dir = self.config.get("save_dir", "data/saves")
        save_file = Path(save_dir) / "progression.json"
        # Ensure save directory exists
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scene_history": self.scene_history
            }, f, indent=2)

    def add_memory(self, memory_type: str, content: str, metadata: dict = None) -> str:
        """Add a new memory to the vector store."""
        memory = {
            "memory_type": memory_type,
            "content": content,
            "timestamp": datetime.now().timestamp(),
            "metadata": metadata or {}
        }
        
        return self.knowledge_base.add_memory(memory)

    def get_story_memories(self) -> dict:
        """Get all relevant memories for story context."""
        # Get recent scenes
        recent_scenes = self.scene_history[-self.max_history_length:]
        
        # Get memories by type
        promises = self.knowledge_base.get_memories_by_type("promise")
        events = self.knowledge_base.get_memories_by_type("event")
        relationships = self.knowledge_base.get_memories_by_type("relationship")
        locations = self.knowledge_base.get_memories_by_type("location")
        
        return {
            "memories": {
                "promises": promises,
                "events": events,
                "relationships": relationships,
                "locations": locations
            },
            "total_memories": len(promises) + len(events) + len(relationships) + len(locations),
            "recent_scenes": recent_scenes
        }

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[dict]:
        """Get memories relevant to the current context."""
        return self.knowledge_base.get_relevant_memories(query, limit)

    def get_character_memories(self, character: str, limit: int = 10) -> List[dict]:
        """Get memories related to a specific character."""
        return self.knowledge_base.get_memories_by_character(character, limit)

    def get_location_memories(self, location: str, limit: int = 10) -> List[dict]:
        """Get memories related to a specific location."""
        return self.knowledge_base.get_memories_by_location(location, limit)

    def add_scene_to_history(self, scene: dict):
        """Add a scene to the history."""
        self.scene_history.append(scene)
        if len(self.scene_history) > self.max_history_length:
            self.scene_history.pop(0)
        self._save_progression()

    def save_progression(self, filepath: str):
        """Save progression data to disk."""
        data = {
            "scene_history": self.scene_history
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_progression(self, filepath: str):
        """Load progression data from disk."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.scene_history = data["scene_history"]

    def get_story_context(self) -> Dict[str, Any]:
        """Get the current story context for the LLM."""
        return {
            "memories": [
                {
                    "type": m["memory_type"],
                    "description": m["content"],
                    "scene_id": m["memory_type"],
                    "metadata": m["metadata"]
                }
                for m in self.scene_history[-10:]  # Last 10 memories
            ],
            "recent_scenes": self.scene_history[-5:],  # Last 5 scenes
            "total_memories": len(self.scene_history),
            "total_scenes": len(self.scene_history)
        }

    def get_comprehensive_story_context(self, current_location: str = None, limit: int = 15) -> Dict[str, Any]:
        """Get comprehensive story context optimized for LLM consumption."""
        
        # Get recent scenes (last 5)
        recent_scenes = self.scene_history[-5:] if self.scene_history else []
        
        # Get semantically relevant memories using vector search
        if current_location:
            location_memories = self.get_location_memories(current_location, limit=5)
        else:
            location_memories = []
        
        # Get character relationships and promises (most important for continuity)
        character_memories = self.knowledge_base.get_memories_by_type("friendship")[:5]
        promise_memories = self.knowledge_base.get_memories_by_type("promise")[:5]
        
        # Get recent discoveries and growth moments
        discovery_memories = self.knowledge_base.get_memories_by_type("discovery")[:3]
        growth_memories = self.knowledge_base.get_memories_by_type("growth")[:3]
        
        # Create a story summary
        story_summary = self._create_story_summary(recent_scenes, character_memories, promise_memories)
        
        return {
            "story_summary": story_summary,
            "current_relationships": self._format_relationships(character_memories),
            "active_promises": self._format_promises(promise_memories),
            "recent_discoveries": self._format_discoveries(discovery_memories),
            "character_growth": self._format_growth(growth_memories),
            "location_context": self._format_location_context(location_memories),
            "total_scenes": len(self.scene_history),
            "total_memories": len(character_memories) + len(promise_memories) + len(discovery_memories) + len(growth_memories)
        }
    
    def _create_story_summary(self, recent_scenes: List[dict], character_memories: List[dict], 
                             promise_memories: List[dict]) -> str:
        """Create a concise story summary for the LLM."""
        summary_parts = []
        
        # Add recent story progression
        if recent_scenes:
            summary_parts.append("Recent Story: " + " → ".join([
                scene.get("location", "Unknown") for scene in recent_scenes[-3:]
            ]))
        
        # Add key relationships
        if character_memories:
            relationships = [mem.get("content", "")[:100] for mem in character_memories[:3]]
            summary_parts.append("Key Relationships: " + "; ".join(relationships))
        
        # Add active promises
        if promise_memories:
            promises = [mem.get("content", "")[:100] for mem in promise_memories[:2]]
            summary_parts.append("Active Promises: " + "; ".join(promises))
        
        return " | ".join(summary_parts) if summary_parts else "Beginning of adventure"
    
    def _format_relationships(self, memories: List[dict]) -> List[str]:
        """Format relationship memories for LLM context."""
        return [f"{mem.get('content', '')}" for mem in memories]
    
    def _format_promises(self, memories: List[dict]) -> List[str]:
        """Format promise memories for LLM context."""
        return [f"{mem.get('content', '')}" for mem in memories]
    
    def _format_discoveries(self, memories: List[dict]) -> List[str]:
        """Format discovery memories for LLM context."""
        return [f"{mem.get('content', '')}" for mem in memories]
    
    def _format_growth(self, memories: List[dict]) -> List[str]:
        """Format growth memories for LLM context."""
        return [f"{mem.get('content', '')}" for mem in memories]
    
    def _format_location_context(self, memories: List[dict]) -> List[str]:
        """Format location-specific memories for LLM context."""
        return [f"{mem.get('content', '')}" for mem in memories]

    def get_compressed_context(self, current_location: str = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """Get compressed context for very long stories, prioritizing the most important elements."""
        
        # Always include the most recent scene
        recent_scene = self.scene_history[-1] if self.scene_history else {}
        
        # Get the most impactful memories (promises and relationships are highest priority)
        high_priority_memories = []
        
        # Add active promises (these drive story arcs)
        promises = self.knowledge_base.get_memories_by_type("promise")[:3]
        high_priority_memories.extend([f"PROMISE: {mem.get('content', '')}" for mem in promises])
        
        # Add key relationships (these define character dynamics)
        relationships = self.knowledge_base.get_memories_by_type("friendship")[:2]
        high_priority_memories.extend([f"RELATIONSHIP: {mem.get('content', '')}" for mem in relationships])
        
        # Add location-specific context if available
        if current_location:
            location_memories = self.get_location_memories(current_location, limit=2)
            high_priority_memories.extend([f"LOCATION: {mem.get('content', '')}" for mem in location_memories])
        
        # Create a very concise summary
        compressed_summary = f"Recent: {recent_scene.get('location', 'Unknown')} | " + \
                           " | ".join(high_priority_memories[:3])  # Top 3 most important
        
        return {
            "compressed_summary": compressed_summary,
            "active_promises": [mem.get('content', '') for mem in promises],
            "key_relationships": [mem.get('content', '') for mem in relationships],
            "location_context": [mem.get('content', '') for mem in location_memories] if current_location else [],
            "story_length": len(self.scene_history)
        } 