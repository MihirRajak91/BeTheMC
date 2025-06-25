"""
Story generation using LLMs and vector databases.
"""
from typing import Dict, Any, List
from ..data.vector_store import KantoKnowledgeBase
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..core.progression import ProgressionManager
from .prompts import get_narrator_prompt, get_choice_prompt, get_memory_extraction_prompt
from .providers import get_llm_provider, get_embedder_provider
import json

logger = setup_logger(__name__)

class StoryGenerator:
    def __init__(self):
        """Initialize the story generator."""
        self.config = Config()
        self.knowledge_base = KantoKnowledgeBase()
        
        # Initialize LLM
        llm_config = self.config.get("ai.llm")
        self.llm = get_llm_provider(llm_config["provider"]).get_llm(llm_config)
        
        # Initialize embedder
        embedder_config = self.config.get("ai.embedder")
        self.embedder = get_embedder_provider(embedder_config["provider"]).get_embedder(embedder_config)
        
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
        
        # Get comprehensive story context (optimized for LLM)
        comprehensive_context = progression.get_comprehensive_story_context(location)
        
        # Generate narrative using LLM
        response = self.llm.invoke(
            self.narrator_prompt.format_messages(
                location=location,
                personality=personality,
                recent_events=recent_events,
                kanto_knowledge=story_context,
                story_summary=comprehensive_context["story_summary"],
                current_relationships=comprehensive_context["current_relationships"],
                active_promises=comprehensive_context["active_promises"],
                recent_discoveries=comprehensive_context["recent_discoveries"],
                character_growth=comprehensive_context["character_growth"],
                location_context=comprehensive_context["location_context"]
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
                content=memory["description"],
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
            if choice.get("new_memory") is not None:
                progression.add_memory(
                    memory_type=choice["new_memory"]["type"],
                    content=choice["new_memory"]["description"],
                    metadata=choice["new_memory"].get("metadata")
                )
        
        return choices

    def _parse_memories(self, content: str) -> List[Dict[str, Any]]:
        """Parse memories from LLM response."""
        memories = []
        
        # Look for memory tags in the format [Memory: type] ... [End Memory]
        import re
        memory_pattern = r'\[Memory:\s*(\w+)\]\s*(.*?)\s*\[End Memory\]'
        matches = re.findall(memory_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for memory_type, description in matches:
            memory = {
                "type": memory_type.strip().lower(),
                "description": description.strip(),
                "metadata": {}
            }
            memories.append(memory)
        
        # If no structured memories found, try to extract from general text
        if not memories:
            # Look for potential memory indicators
            memory_indicators = [
                "promise", "promised", "commitment", "vow",
                "relationship", "friendship", "rivalry",
                "event", "happened", "occurred", "discovered",
                "location", "place", "area", "town", "city"
            ]
            
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(indicator in sentence.lower() for indicator in memory_indicators):
                    # Determine memory type based on content
                    memory_type = "event"  # default
                    if any(word in sentence.lower() for word in ["promise", "promised", "commitment"]):
                        memory_type = "promise"
                    elif any(word in sentence.lower() for word in ["relationship", "friendship", "rivalry"]):
                        memory_type = "relationship"
                    elif any(word in sentence.lower() for word in ["location", "place", "area", "town", "city"]):
                        memory_type = "location"
                    
                    memory = {
                        "type": memory_type,
                        "description": sentence,
                        "metadata": {}
                    }
                    memories.append(memory)
        
        return memories

    def _parse_choices(self, content: str) -> List[Dict[str, Any]]:
        """Parse choices from LLM response."""
        choices = []
        
        # Try to parse structured JSON first
        try:
            # Look for JSON-like structure in the response
            import re
            json_pattern = r'\{[^{}]*"text"[^{}]*\}'
            json_matches = re.findall(json_pattern, content)
            
            for json_str in json_matches:
                try:
                    choice_data = json.loads(json_str)
                    if "text" in choice_data:
                        choice = {
                            "text": choice_data["text"],
                            "effects": choice_data.get("effects", {}),
                            "new_memory": choice_data.get("new_memory")
                        }
                        choices.append(choice)
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
        
        # If no structured choices found, parse from text
        if not choices:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # Look for choice indicators
                if (line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.')) and 
                    len(line) > 3 and not line.startswith('---')):
                    
                    # Extract choice text
                    choice_text = line
                    for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ']:
                        if choice_text.startswith(prefix):
                            choice_text = choice_text[len(prefix):]
                            break
                    
                    if choice_text:
                        # Estimate effects based on choice content
                        effects = self._estimate_choice_effects(choice_text, {})
                        
                        choice = {
                            "text": choice_text,
                            "effects": effects,
                            "new_memory": None
                        }
                        choices.append(choice)
        
        return choices

    def _estimate_choice_effects(self, choice_text: str, personality: Dict[str, float]) -> Dict[str, float]:
        """Estimate the effects of a choice on anime-style personality traits."""
        effects = {}
        
        # Define keywords for each anime-style personality trait
        trait_keywords = {
            "compassion": ["help", "care", "comfort", "protect", "save", "understand", "empathize", "kind", "gentle"],
            "courage": ["brave", "courage", "bold", "dare", "risk", "challenge", "face", "confront", "stand up"],
            "curiosity": ["curious", "explore", "investigate", "discover", "learn", "study", "examine", "search", "wonder"],
            "friendship": ["friend", "bond", "trust", "support", "together", "teamwork", "loyal", "faithful", "care"],
            "determination": ["determined", "persist", "never give up", "continue", "keep going", "endure", "overcome", "try"]
        }
        
        choice_lower = choice_text.lower()
        
        for trait, keywords in trait_keywords.items():
            # Count how many keywords appear in the choice
            keyword_count = sum(1 for keyword in keywords if keyword in choice_lower)
            
            if keyword_count > 0:
                # Base effect is 0.1 per keyword, capped at 0.3
                effect = min(0.3, keyword_count * 0.1)
                effects[trait] = effect
        
        # Anime-style context-based effects
        import random
        
        # Compassionate choices that help others
        if any(word in choice_lower for word in ["help", "save", "protect", "comfort", "understand"]):
            effects["compassion"] = effects.get("compassion", 0) + 0.2
            effects["friendship"] = effects.get("friendship", 0) + 0.1
        
        # Courageous choices that face challenges
        if any(word in choice_lower for word in ["face", "challenge", "confront", "stand up", "brave"]):
            effects["courage"] = effects.get("courage", 0) + 0.2
            effects["determination"] = effects.get("determination", 0) + 0.1
        
        # Curious choices that explore and learn
        if any(word in choice_lower for word in ["explore", "investigate", "discover", "learn", "search"]):
            effects["curiosity"] = effects.get("curiosity", 0) + 0.2
        
        # Friendship-focused choices
        if any(word in choice_lower for word in ["friend", "bond", "together", "teamwork", "trust"]):
            effects["friendship"] = effects.get("friendship", 0) + 0.2
            effects["compassion"] = effects.get("compassion", 0) + 0.1
        
        # Determined choices that persist
        if any(word in choice_lower for word in ["try", "continue", "persist", "never give up", "keep going"]):
            effects["determination"] = effects.get("determination", 0) + 0.2
            effects["courage"] = effects.get("courage", 0) + 0.1
        
        # Ensure effects are within bounds
        for trait in effects:
            effects[trait] = max(-0.1, min(0.3, effects[trait]))
        
        return effects 