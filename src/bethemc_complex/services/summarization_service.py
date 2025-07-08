"""
Summarization service for optimizing large save states and game contexts.
"""
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
from dataclasses import asdict
import hashlib

from ..models.core import GameState, Player, Story, Choice, Memory, GameProgression
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SummarizationService:
    """Service for summarizing and compressing game states and contexts."""
    
    def __init__(self, max_memories: int = 50, max_choices: int = 10, max_summary_length: int = 500):
        """Initialize the summarization service."""
        self.max_memories = max_memories
        self.max_choices = max_choices
        self.max_summary_length = max_summary_length
    
    def summarize_game_state(self, game_state: GameState) -> Dict[str, Any]:
        """Create a summarized version of the game state for efficient storage."""
        try:
            # Summarize memories by importance and recency
            summarized_memories = self._summarize_memories(game_state.memories)
            
            # Create a story summary
            story_summary = self._create_story_summary(game_state)
            
            # Compress progression data
            compressed_progression = self._compress_progression(game_state.progression)
            
            # Create a compact save structure
            summarized_state = {
                "player_id": game_state.player.id,
                "player_name": game_state.player.name,
                "personality_traits": game_state.player.personality_traits,
                "current_location": game_state.progression.current_location,
                "story_summary": story_summary,
                "current_story": {
                    "title": game_state.current_story.title,
                    "content": game_state.current_story.content[:200] + "..." if len(game_state.current_story.content) > 200 else game_state.current_story.content,
                    "location": game_state.current_story.location
                },
                "available_choices": [
                    {
                        "id": choice.id,
                        "text": choice.text,
                        "effects": choice.effects
                    }
                    for choice in game_state.available_choices[:self.max_choices]
                ],
                "key_memories": summarized_memories,
                "compressed_progression": compressed_progression,
                "summary_hash": self._generate_summary_hash(game_state),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Summarized game state for player {game_state.player.name}")
            return summarized_state
            
        except Exception as e:
            logger.error(f"Failed to summarize game state: {e}")
            raise
    
    def _summarize_memories(self, memories: List[Memory]) -> List[Dict[str, Any]]:
        """Summarize memories by importance and recency."""
        if not memories:
            return []
        
        # Sort memories by importance (promises > relationships > events > general)
        importance_order = {"promise": 4, "relationship": 3, "achievement": 2, "lesson": 2, "general": 1}
        
        def memory_importance(memory: Memory) -> Tuple[int, datetime]:
            importance = importance_order.get(memory.memory_type, 1)
            return (importance, memory.timestamp)
        
        # Sort by importance (descending) then by timestamp (descending)
        sorted_memories = sorted(memories, key=memory_importance, reverse=True)
        
        # Take the most important memories
        key_memories = sorted_memories[:self.max_memories]
        
        # Create summarized memory entries
        summarized = []
        for memory in key_memories:
            summarized.append({
                "type": memory.memory_type,
                "content": memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                "location": memory.location,
                "timestamp": memory.timestamp.isoformat(),
                "importance": importance_order.get(memory.memory_type, 1)
            })
        
        return summarized
    
    def _create_story_summary(self, game_state: GameState) -> str:
        """Create a concise story summary."""
        summary_parts = []
        
        # Add current location
        summary_parts.append(f"Location: {game_state.progression.current_location}")
        
        # Add completed events (last 5)
        completed_events = game_state.progression.completed_events[-5:]
        if completed_events:
            summary_parts.append(f"Recent: {' → '.join(completed_events)}")
        
        # Add key memories by type
        memories_by_type = {}
        for memory in game_state.memories:
            if memory.memory_type not in memories_by_type:
                memories_by_type[memory.memory_type] = []
            memories_by_type[memory.memory_type].append(memory)
        
        # Add promises (most important)
        if "promise" in memories_by_type:
            promises = [m.content[:50] for m in memories_by_type["promise"][:2]]
            summary_parts.append(f"Promises: {'; '.join(promises)}")
        
        # Add relationships
        if "relationship" in memories_by_type:
            relationships = [m.content[:50] for m in memories_by_type["relationship"][:2]]
            summary_parts.append(f"Relationships: {'; '.join(relationships)}")
        
        summary = " | ".join(summary_parts)
        return summary[:self.max_summary_length]
    
    def _compress_progression(self, progression: GameProgression) -> Dict[str, Any]:
        """Compress progression data to essential information."""
        return {
            "current_location": progression.current_location,
            "completed_events_count": len(progression.completed_events),
            "recent_events": progression.completed_events[-5:],  # Last 5 events
            "relationships_count": len(progression.relationships),
            "inventory_count": len(progression.inventory),
            "total_progress": len(progression.completed_events)
        }
    
    def _generate_summary_hash(self, game_state: GameState) -> str:
        """Generate a hash for the summarized state for change detection."""
        key_data = {
            "player_id": game_state.player.id,
            "location": game_state.progression.current_location,
            "completed_events": game_state.progression.completed_events,
            "memory_count": len(game_state.memories),
            "story_id": game_state.current_story.id
        }
        
        data_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def expand_summarized_state(self, summarized_state: Dict[str, Any]) -> GameState:
        """Expand a summarized state back to a full GameState (with limitations)."""
        try:
            # Reconstruct player
            player = Player(
                id=summarized_state["player_id"],
                name=summarized_state["player_name"],
                personality_traits=summarized_state["personality_traits"]
            )
            
            # Reconstruct current story
            current_story = Story(
                id=f"story-{summarized_state['player_id']}",
                title=summarized_state["current_story"]["title"],
                content=summarized_state["current_story"]["content"],
                location=summarized_state["current_story"]["location"]
            )
            
            # Reconstruct choices
            available_choices = [
                Choice(
                    id=choice["id"],
                    text=choice["text"],
                    effects=choice["effects"]
                )
                for choice in summarized_state["available_choices"]
            ]
            
            # Reconstruct memories (limited)
            memories = []
            for mem_data in summarized_state["key_memories"]:
                memory = Memory(
                    memory_type=mem_data["type"],
                    content=mem_data["content"],
                    location=mem_data["location"],
                    timestamp=datetime.fromisoformat(mem_data["timestamp"])
                )
                memories.append(memory)
            
            # Reconstruct progression (with limited data)
            progression = GameProgression(
                current_location=summarized_state["current_location"],
                completed_events=summarized_state["compressed_progression"]["recent_events"],
                relationships={},  # Lost in compression
                inventory=[]  # Lost in compression
            )
            
            game_state = GameState(
                player=player,
                current_story=current_story,
                available_choices=available_choices,
                memories=memories,
                progression=progression
            )
            
            logger.info(f"Expanded summarized state for player {player.name}")
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to expand summarized state: {e}")
            raise
    
    def create_context_summary(self, game_state: GameState, max_tokens: int = 1000) -> Dict[str, Any]:
        """Create a context summary optimized for LLM consumption."""
        try:
            # Get the most important memories
            important_memories = self._get_important_memories(game_state.memories, max_count=10)
            
            # Create a focused context
            context = {
                "current_situation": {
                    "location": game_state.progression.current_location,
                    "story_title": game_state.current_story.title,
                    "story_preview": game_state.current_story.content[:150] + "..." if len(game_state.current_story.content) > 150 else game_state.current_story.content
                },
                "player_context": {
                    "name": game_state.player.name,
                    "personality": game_state.player.personality_traits,
                    "progress": len(game_state.progression.completed_events)
                },
                "active_context": {
                    "promises": [m.content for m in important_memories if m.memory_type == "promise"][:3],
                    "relationships": [m.content for m in important_memories if m.memory_type == "relationship"][:3],
                    "recent_events": game_state.progression.completed_events[-3:],
                    "available_choices": [
                        {
                            "text": choice.text,
                            "effects": choice.effects
                        }
                        for choice in game_state.available_choices
                    ]
                },
                "story_summary": self._create_story_summary(game_state)
            }
            
            # Estimate token count and truncate if necessary
            estimated_tokens = len(json.dumps(context)) // 4  # Rough estimation
            if estimated_tokens > max_tokens:
                context = self._truncate_context(context, max_tokens)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create context summary: {e}")
            raise
    
    def _get_important_memories(self, memories: List[Memory], max_count: int = 10) -> List[Memory]:
        """Get the most important memories based on type and recency."""
        if not memories:
            return []
        
        # Priority order: promise > relationship > achievement > lesson > general
        priority_order = {"promise": 5, "relationship": 4, "achievement": 3, "lesson": 2, "general": 1}
        
        def memory_score(memory: Memory) -> Tuple[int, datetime]:
            priority = priority_order.get(memory.memory_type, 1)
            return (priority, memory.timestamp)
        
        # Sort by priority then by timestamp
        sorted_memories = sorted(memories, key=memory_score, reverse=True)
        return sorted_memories[:max_count]
    
    def _truncate_context(self, context: Dict[str, Any], max_tokens: int) -> Dict[str, Any]:
        """Truncate context to fit within token limit."""
        # Start with essential information
        truncated = {
            "current_situation": context["current_situation"],
            "player_context": context["player_context"],
            "story_summary": context["story_summary"][:200]  # Limit summary length
        }
        
        # Add active context with limits
        active_context = context["active_context"]
        truncated["active_context"] = {
            "promises": active_context["promises"][:2],  # Limit to 2 promises
            "relationships": active_context["relationships"][:2],  # Limit to 2 relationships
            "recent_events": active_context["recent_events"][:2],  # Limit to 2 events
            "available_choices": active_context["available_choices"][:3]  # Limit to 3 choices
        }
        
        return truncated
    
    def get_save_size_estimate(self, game_state: GameState) -> Dict[str, Any]:
        """Estimate the size of a save file and provide optimization suggestions."""
        try:
            # Calculate component sizes
            player_size = len(json.dumps(asdict(game_state.player)))
            story_size = len(json.dumps(asdict(game_state.current_story)))
            choices_size = len(json.dumps([asdict(c) for c in game_state.available_choices]))
            memories_size = len(json.dumps([asdict(m) for m in game_state.memories]))
            progression_size = len(json.dumps(asdict(game_state.progression)))
            
            total_size = player_size + story_size + choices_size + memories_size + progression_size
            
            # Create optimization suggestions
            suggestions = []
            if memories_size > 50000:  # 50KB
                suggestions.append("Consider limiting memories to 50 most important")
            if total_size > 100000:  # 100KB
                suggestions.append("Consider using summarization for storage")
            if len(game_state.memories) > 100:
                suggestions.append("Memory count is high - consider cleanup")
            
            return {
                "total_size_bytes": total_size,
                "total_size_kb": total_size / 1024,
                "components": {
                    "player": player_size,
                    "story": story_size,
                    "choices": choices_size,
                    "memories": memories_size,
                    "progression": progression_size
                },
                "memory_count": len(game_state.memories),
                "choice_count": len(game_state.available_choices),
                "completed_events": len(game_state.progression.completed_events),
                "optimization_suggestions": suggestions,
                "should_summarize": total_size > 100000
            }
            
        except Exception as e:
            logger.error(f"Failed to estimate save size: {e}")
            raise 