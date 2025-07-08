"""
Dependency injection setup for BeTheMC API.
"""
from fastapi import Depends
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..core.interfaces import StoryGenerator, KnowledgeBase, ProgressionTracker, SaveManager, Memory
from ..ai.story_generator import StoryGenerator as ConcreteStoryGenerator
from ..data.vector_store import KantoKnowledgeBase
from ..core.progression import ProgressionManager
from ..services.game_service import GameService
from ..services.save_service import SaveService
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeBaseAdapter:
    """Adapter to make KantoKnowledgeBase implement the KnowledgeBase interface."""
    
    def __init__(self, kanto_kb: KantoKnowledgeBase):
        self.kb = kanto_kb
    
    def add_memory(self, memory: Memory) -> str:
        """Add a memory to the knowledge base."""
        memory_dict = {
            "memory_type": memory.memory_type,
            "content": memory.content,
            "location": memory.location,
            "timestamp": memory.timestamp.isoformat(),
            "metadata": memory.metadata
        }
        return self.kb.add_memory(memory_dict)
    
    def get_memories_by_type(self, memory_type: str, limit: int = 10) -> List[Memory]:
        """Get memories by type."""
        memory_dicts = self.kb.get_memories_by_type(memory_type, limit)
        memories = []
        for mem_dict in memory_dicts:
            try:
                timestamp = datetime.fromisoformat(mem_dict["metadata"]["timestamp"])
            except:
                timestamp = datetime.now()
            
            memory = Memory(
                memory_type=mem_dict["metadata"].get("memory_type", "general"),
                content=mem_dict["content"],
                location=mem_dict["metadata"].get("location", ""),
                timestamp=timestamp,
                metadata=mem_dict["metadata"]
            )
            memories.append(memory)
        return memories
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Get memories relevant to a query."""
        memory_dicts = self.kb.get_relevant_memories(query, limit)
        memories = []
        for mem_dict in memory_dicts:
            try:
                timestamp = datetime.fromisoformat(mem_dict["metadata"]["timestamp"])
            except:
                timestamp = datetime.now()
            
            memory = Memory(
                memory_type=mem_dict["metadata"].get("memory_type", "general"),
                content=mem_dict["content"],
                location=mem_dict["metadata"].get("location", ""),
                timestamp=timestamp,
                metadata=mem_dict["metadata"]
            )
            memories.append(memory)
        return memories
    
    def get_location_info(self, location: str) -> dict:
        """Get information about a location."""
        return self.kb.get_location_info(location)

class ProgressionTrackerAdapter:
    """Adapter to make ProgressionManager implement the ProgressionTracker interface."""
    
    def __init__(self, progression_manager: ProgressionManager):
        self.pm = progression_manager
    
    def add_scene(self, scene: Dict[str, Any]) -> None:
        """Add a scene to the progression."""
        self.pm.add_scene_to_history(scene)
    
    def get_compressed_context(self, location: str) -> Dict[str, Any]:
        """Get compressed context for a location."""
        return self.pm.get_comprehensive_story_context(location)
    
    def get_story_context(self) -> Dict[str, Any]:
        """Get current story context."""
        return self.pm.get_story_context()

class SaveManagerAdapter:
    """Adapter to make SaveService implement the SaveManager interface."""
    
    def __init__(self, save_service: SaveService):
        self.ss = save_service
    
    def save_game(self, session_id: str, save_name: str, data: Dict[str, Any]) -> bool:
        """Save game data."""
        try:
            # Convert the data back to a GameState object for the save service
            from ..models.core import GameState, Player, Story, Choice, Memory, GameProgression
            
            player = Player(**data["game_state"]["player"])
            current_story = Story(**data["game_state"]["current_story"])
            available_choices = [Choice(**c) for c in data["game_state"]["available_choices"]]
            memories = [Memory(**m) for m in data["game_state"]["memories"]]
            progression = GameProgression(**data["game_state"]["progression"])
            
            game_state = GameState(
                player=player,
                current_story=current_story,
                available_choices=available_choices,
                memories=memories,
                progression=progression
            )
            
            # Use the save service's async method
            import asyncio
            result = asyncio.run(self.ss.save_game(game_state, save_name))
            return True
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Load game data."""
        try:
            # This is a simplified implementation - in practice you'd need to map save_name to save_id
            # For now, we'll return None to indicate not implemented
            return None
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return None
    
    def list_saves(self) -> List[str]:
        """List available saves."""
        try:
            # This would need to be implemented to return save names
            return []
        except Exception as e:
            logger.error(f"Failed to list saves: {e}")
            return []
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file."""
        try:
            # This would need to be implemented to map save_name to save_id
            return False
        except Exception as e:
            logger.error(f"Failed to delete save: {e}")
            return False

def get_config() -> Config:
    """Get configuration instance."""
    return Config()

def get_story_generator() -> StoryGenerator:
    """Get story generator instance."""
    config = get_config()
    return ConcreteStoryGenerator(config)

def get_knowledge_base() -> KnowledgeBase:
    """Get knowledge base instance."""
    config = get_config()
    kanto_kb = KantoKnowledgeBase(config)
    return KnowledgeBaseAdapter(kanto_kb)

def get_progression_tracker() -> ProgressionTracker:
    """Get progression tracker instance."""
    config = get_config()
    progression_manager = ProgressionManager(config)
    return ProgressionTrackerAdapter(progression_manager)

def get_save_manager() -> SaveManager:
    """Get save manager instance."""
    save_service = SaveService()
    return SaveManagerAdapter(save_service)

def get_game_service() -> GameService:
    """Get game service instance."""
    return GameService()

def get_save_service() -> SaveService:
    """Get save service instance."""
    return SaveService() 