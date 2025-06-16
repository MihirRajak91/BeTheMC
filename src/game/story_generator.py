"""
Dynamic story generator using LLM to create personalized Pokémon adventures.
"""
from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from ..database.vector_store import KantoKnowledgeBase
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class StoryGenerator:
    def __init__(self):
        """Initialize the story generator."""
        self.config = Config()
        self.knowledge_base = KantoKnowledgeBase()
        self.llm = ChatOpenAI(
            model_name=self.config.get("ai.model_type"),
            temperature=self.config.get("ai.temperature"),
            max_tokens=self.config.get("ai.max_tokens")
        )
        self._setup_prompts()

    def _setup_prompts(self):
        """Set up the prompt templates for different story aspects."""
        self.narrator_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a master storyteller in the Pokémon world, specifically in the Kanto region.
            Your role is to create an immersive, personalized story for the player based on their choices and personality.
            Use the provided Kanto knowledge to maintain consistency with the Pokémon world while creating unique narratives.
            Focus on creating emotional connections and meaningful choices that reflect the player's personality."""),
            HumanMessage(content="""Create a narrative segment based on the following context:
            
            Current Location: {location}
            Player's Personality: {personality}
            Recent Events: {recent_events}
            Available Knowledge: {kanto_knowledge}
            
            Generate a vivid description of the current situation and present the player with meaningful choices that reflect their personality.""")
        ])

        self.choice_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a choice designer for a Pokémon adventure.
            Create meaningful choices that reflect the player's personality and impact the story.
            Each choice should have clear consequences and align with the player's traits."""),
            HumanMessage(content="""Design choices for the following situation:
            
            Current Situation: {current_situation}
            Player's Personality: {personality}
            Available Knowledge: {kanto_knowledge}
            
            Generate 3-4 meaningful choices that the player can make, each with potential consequences.""")
        ])

    def generate_narrative(self, 
                          location: str,
                          personality: Dict[str, float],
                          recent_events: List[str],
                          max_knowledge_items: int = 5) -> Dict[str, Any]:
        """Generate a narrative segment based on the current context."""
        # Get relevant Kanto knowledge
        location_info = self.knowledge_base.get_location_info(location)
        story_context = self.knowledge_base.get_story_context(
            f"Events in {location} involving {', '.join(recent_events)}"
        )
        
        # Combine knowledge
        kanto_knowledge = {
            "location": location_info[:max_knowledge_items],
            "context": story_context[:max_knowledge_items]
        }
        
        # Generate narrative
        response = self.llm.invoke(
            self.narrator_prompt.format_messages(
                location=location,
                personality=personality,
                recent_events=recent_events,
                kanto_knowledge=kanto_knowledge
            )
        )
        
        return {
            "narrative": response.content,
            "context": kanto_knowledge
        }

    def generate_choices(self,
                        current_situation: str,
                        personality: Dict[str, float],
                        max_knowledge_items: int = 3) -> List[Dict[str, Any]]:
        """Generate meaningful choices for the current situation."""
        # Get relevant context
        story_context = self.knowledge_base.get_story_context(current_situation)
        
        # Generate choices
        response = self.llm.invoke(
            self.choice_prompt.format_messages(
                current_situation=current_situation,
                personality=personality,
                kanto_knowledge=story_context[:max_knowledge_items]
            )
        )
        
        # Parse choices from response
        # Note: In a real implementation, you'd want to parse this more carefully
        choices = []
        for line in response.content.split('\n'):
            if line.strip().startswith(('-', '*', '•')):
                choice_text = line.strip()[1:].strip()
                choices.append({
                    "text": choice_text,
                    "effects": self._estimate_choice_effects(choice_text, personality)
                })
        
        return choices

    def _estimate_choice_effects(self, 
                               choice_text: str,
                               personality: Dict[str, float]) -> Dict[str, float]:
        """Estimate the effects of a choice on story variables."""
        # This is a simplified version - in a real implementation,
        # you'd want to use the LLM to analyze the choice more carefully
        effects = {}
        for trait in personality.keys():
            # Simple heuristic: if trait name appears in choice, it's affected
            if trait.lower() in choice_text.lower():
                effects[trait] = 0.1  # Small positive effect
        return effects

    def process_player_choice(self,
                            choice: str,
                            current_context: Dict[str, Any],
                            personality: Dict[str, float]) -> Dict[str, Any]:
        """Process a player's choice and generate the next story segment."""
        # Update personality based on choice effects
        for trait, effect in current_context.get("choice_effects", {}).items():
            personality[trait] = min(1.0, max(0.0, personality[trait] + effect))
        
        # Generate next narrative segment
        return self.generate_narrative(
            location=current_context["location"],
            personality=personality,
            recent_events=[choice] + current_context.get("recent_events", [])[:2]
        ) 