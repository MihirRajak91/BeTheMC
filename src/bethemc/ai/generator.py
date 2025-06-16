"""
Story generation using LLMs and vector databases.
"""
from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI
from ..data.vector_store import KantoKnowledgeBase
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..core.progression import ProgressionManager
from .prompts import get_narrator_prompt, get_choice_prompt, get_memory_extraction_prompt

logger = setup_logger(__name__)

class StoryGenerator:
    def __init__(self):
        """Initialize the story generator."""
        self.config = Config()
        self.knowledge_base = KantoKnowledgeBase()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=self.config.get("ai.model_type"),
            temperature=self.config.get("ai.temperature"),
            max_tokens=self.config.get("ai.max_tokens")
        )
        
        # Load prompts
        self.narrator_prompt = get_narrator_prompt()
        self.choice_prompt = get_choice_prompt()
        self.memory_extraction_prompt = get_memory_extraction_prompt()

    def generate_narrative(self,
                          location: str,
                          personality: Dict[str, float],
                          recent_events: List[str],
                          progression: ProgressionManager) -> Dict[str, Any]:
        """Generate a narrative segment based on current context."""
        # Get relevant Kanto knowledge
        location_info = self.knowledge_base.get_location_info(location)
        story_context = self.knowledge_base.get_story_context(
            f"Events in {location} involving {', '.join(recent_events)}"
        )
        
        # Get story memories
        story_memories = progression.get_story_context()
        
        # Generate narrative using LLM
        response = self.llm.invoke(
            self.narrator_prompt.format_messages(
                location=location,
                personality=personality,
                recent_events=recent_events,
                kanto_knowledge=story_context,
                story_memories=story_memories
            )
        )
        
        # Extract new memories from the narrative
        memory_response = self.llm.invoke(
            self.memory_extraction_prompt.format_messages(
                narrative=response.content
            )
        )
        
        # Parse and add new memories
        new_memories = self._parse_memories(memory_response.content)
        for memory in new_memories:
            progression.add_memory(
                memory_type=memory["type"],
                description=memory["description"],
                scene_id=memory["scene_id"],
                metadata=memory.get("metadata")
            )
        
        return {
            "narrative": response.content,
            "metadata": {
                "location": location,
                "personality": personality,
                "recent_events": recent_events,
                "new_memories": new_memories
            }
        }

    def generate_choices(self,
                        current_situation: str,
                        personality: Dict[str, float],
                        progression: ProgressionManager) -> List[Dict[str, Any]]:
        """Generate choices based on current situation and story context."""
        # Get relevant context
        story_context = self.knowledge_base.get_story_context(current_situation)
        story_memories = progression.get_story_context()
        
        # Generate choices using LLM
        response = self.llm.invoke(
            self.choice_prompt.format_messages(
                current_situation=current_situation,
                personality=personality,
                kanto_knowledge=story_context,
                story_memories=story_memories
            )
        )
        
        # Parse choices from LLM response
        choices = self._parse_choices(response.content)
        
        # Add any new memories from choices
        for choice in choices:
            if "new_memory" in choice:
                progression.add_memory(
                    memory_type=choice["new_memory"]["type"],
                    description=choice["new_memory"]["description"],
                    scene_id=choice["scene_id"],
                    metadata=choice["new_memory"].get("metadata")
                )
        
        return choices

    def _parse_memories(self, content: str) -> List[Dict[str, Any]]:
        """Parse memories from LLM response."""
        # This is a placeholder - in practice, you'd want to:
        # 1. Parse the JSON response from the memory extraction prompt
        # 2. Validate the memory structure
        # 3. Add any missing required fields
        return []

    def _parse_choices(self, content: str) -> List[Dict[str, Any]]:
        """Parse choices from LLM response."""
        # This is a placeholder - in practice, you'd want to:
        # 1. Parse the JSON response from the choice prompt
        # 2. Validate the choice structure
        # 3. Add any missing required fields
        return [] 