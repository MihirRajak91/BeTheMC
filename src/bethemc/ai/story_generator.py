"""
Dynamic story generator using LLM to create personalized Pokémon adventures.
"""
from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from bethemc.data.vector_store import KantoKnowledgeBase
from bethemc.core.progression import ProgressionManager
from bethemc.utils.config import Config
from bethemc.utils.logger import setup_logger
from bethemc.ai.providers import get_llm_provider

logger = setup_logger(__name__)

class StoryGenerator:
    def __init__(self, config=None):
        """Initialize the story generator."""
        self.config = config or Config()
        self.knowledge_base = KantoKnowledgeBase()
        self.progression = ProgressionManager(self.config)
        llm_config = self.config.get("ai.llm")
        self.llm = get_llm_provider(llm_config["provider"]).get_llm(llm_config)
        self._setup_prompts()

    def _setup_prompts(self):
        """Set up the prompt templates for different story aspects."""
        self.narrator_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a master storyteller in the Pokémon world, specifically in the Kanto region.
            Your role is to create an immersive, personalized story for the player based on their choices and personality.
            Use the provided Kanto knowledge to maintain consistency with the Pokémon world while creating unique narratives.
            Focus on creating emotional connections and meaningful choices that reflect the player's personality.
            
            For long stories, focus on the most important elements: active promises, key relationships, and recent events.
            Keep the narrative flowing naturally while honoring past commitments and character bonds."""),
            HumanMessage(content="""Create a narrative segment based on the following context:
            
            Current Location: {location}
            Player's Personality: {personality}
            Story Context: {story_context}
            Available Knowledge: {kanto_knowledge}
            
            Generate a vivid description of the current situation and present the player with meaningful choices that reflect their personality.""")
        ])

        self.choice_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a choice designer for a Pokémon adventure.
            Create meaningful choices that reflect the player's personality and impact the story.
            Each choice should have clear consequences and align with the player's traits.
            Consider active promises and relationships when designing choices."""),
            HumanMessage(content="""Design choices for the following situation:
            
            Current Situation: {current_situation}
            Player's Personality: {personality}
            Active Promises: {active_promises}
            Key Relationships: {key_relationships}
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
        
        # Use compressed context for long stories
        if len(self.progression.scene_history) > 10:  # Threshold for "long" stories
            compressed_context = self.progression.get_compressed_context(location)
            story_context_text = compressed_context["compressed_summary"]
            active_promises = compressed_context["active_promises"]
            key_relationships = compressed_context["key_relationships"]
        else:
            # Use full context for shorter stories
            story_context_text = " | ".join(recent_events)
            active_promises = []
            key_relationships = []
        
        # Combine knowledge
        kanto_knowledge = {
            "location": location_info,
            "context": story_context[:max_knowledge_items]
        }
        
        # Generate narrative
        response = self.llm.invoke(
            self.narrator_prompt.format_messages(
                location=location,
                personality=personality,
                story_context=story_context_text,
                kanto_knowledge=kanto_knowledge
            )
        )
        
        return {
            "narrative": response.content,
            "context": kanto_knowledge,
            "active_promises": active_promises,
            "key_relationships": key_relationships
        }

    def generate_choices(self,
                        current_situation: str,
                        personality: Dict[str, float],
                        active_promises: List[str] = None,
                        key_relationships: List[str] = None,
                        max_knowledge_items: int = 3) -> List[Dict[str, Any]]:
        """Generate meaningful choices for the current situation."""
        # Get relevant context
        story_context = self.knowledge_base.get_story_context(current_situation)
        
        # Prepare context for choices
        active_promises_text = " | ".join(active_promises) if active_promises else "None"
        key_relationships_text = " | ".join(key_relationships) if key_relationships else "None"
        
        # Generate choices
        response = self.llm.invoke(
            self.choice_prompt.format_messages(
                current_situation=current_situation,
                personality=personality,
                active_promises=active_promises_text,
                key_relationships=key_relationships_text,
                kanto_knowledge=story_context[:max_knowledge_items]
            )
        )
        
        # Parse choices from response
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
        # Enhanced choice effect estimation
        effects = {}
        
        # Check for personality trait keywords
        trait_keywords = {
            "friendship": ["friend", "help", "care", "support", "kind", "loyal"],
            "courage": ["brave", "fight", "protect", "stand", "face", "challenge"],
            "curiosity": ["explore", "investigate", "learn", "discover", "ask", "find"],
            "wisdom": ["think", "plan", "strategy", "consider", "analyze", "smart"],
            "determination": ["persist", "never give up", "try again", "keep going", "endure"]
        }
        
        choice_lower = choice_text.lower()
        for trait, keywords in trait_keywords.items():
            for keyword in keywords:
                if keyword in choice_lower:
                    effects[trait] = effects.get(trait, 0) + 0.1
        
        # Check for promise-related choices
        if any(word in choice_lower for word in ["promise", "vow", "swear", "commit"]):
            effects["promise"] = 0.2
        
        # Check for relationship-building choices
        if any(word in choice_lower for word in ["bond", "trust", "relationship", "connection"]):
            effects["friendship"] = effects.get("friendship", 0) + 0.15
        
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