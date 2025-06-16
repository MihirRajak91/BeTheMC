"""
Simplified progression tracking system that uses LLM for narrative decisions.
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
    def __init__(self, config: dict):
        """Initialize the progression manager."""
        self.config = config
        self.knowledge_base = KantoKnowledgeBase(config)
        self.scene_history: List[dict] = []
        self.max_history_length = config["story"]["max_history_length"]
        
        # Load progression data if exists
        self._load_progression()

    def _load_progression(self):
        """Load progression data from save file."""
        save_file = self.config["save_dir"] / "progression.json"
        if save_file.exists():
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.scene_history = data.get("scene_history", [])

    def _save_progression(self):
        """Save progression data to file."""
        save_file = self.config["save_dir"] / "progression.json"
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