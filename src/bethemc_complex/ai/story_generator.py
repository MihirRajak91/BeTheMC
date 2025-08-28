"""
AI-powered story generation for BeTheMC game.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from ..data.vector_store import KantoKnowledgeBase
from ..core.progression import ProgressionManager
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..ai.providers import get_llm_provider

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
            SystemMessage(content="""You are a master storyteller creating immersive Pokémon adventures in the Kanto region. 
            Your task is to write engaging, vivid narrative segments that advance the player's story.
            
            IMPORTANT: Write actual story content, not templates or instructions. Create vivid descriptions, 
            emotional moments, and compelling situations that the player experiences.
            
            CRITICAL: The story must take place in the SPECIFIED LOCATION. Do not change locations or 
            mention other locations unless they are directly connected to the current story.
            
            Style Guidelines:
            - Write in present tense, as if the player is experiencing events right now
            - Use vivid, descriptive language that brings the Pokémon world to life
            - Include sensory details (sounds, sights, smells, feelings)
            - Create emotional connections and meaningful moments
            - Keep the narrative flowing naturally and engaging
            - Focus on the player's personality traits and how they influence the story
            - Include Pokémon elements naturally in the narrative
            - STAY IN THE SPECIFIED LOCATION - do not jump to other locations
            
            DO NOT ask for information or create templates. Write the actual story content."""),
            HumanMessage(content="""Write a vivid narrative segment for a Pokémon adventure that takes place in {location}.

Location: {location} (STORY MUST TAKE PLACE IN THIS LOCATION)
Player's Personality: {personality}
Recent Events: {story_context}
Available Knowledge: {kanto_knowledge}

Write an engaging story segment that describes what happens next in {location}. 
Make it immersive, emotional, and true to the Pokémon world. Focus on the player's experience 
in {location} and how their personality influences the situation. The story must stay in {location}.""")
        ])

        self.choice_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are creating meaningful choices for a Pokémon adventure game.
            Your task is to generate 3-4 compelling choices that the player can make.
            
            IMPORTANT: Write actual choice text, not templates or instructions. Each choice should be 
            a complete, actionable option that the player can select.
            
            Choice Guidelines:
            - Make choices feel impactful and meaningful
            - Align with the player's personality traits
            - Include clear consequences or implications
            - Make choices diverse and interesting
            - Keep them relevant to the current situation
            - Write in a natural, engaging style
            - Each choice should be a complete sentence describing what the player wants to do
            
            DO NOT ask for information or create templates. Write the actual choice options.
            DO NOT include analysis or explanations - just the choice text."""),
            HumanMessage(content="""Create 3-4 meaningful choices for this situation:
            
            Current Situation: {current_situation}
            Player's Personality: {personality}
            Active Promises: {active_promises}
            Key Relationships: {key_relationships}
            Available Knowledge: {kanto_knowledge}
            
            Write 3-4 compelling choice options that the player can select. Each choice should be 
            a complete sentence describing what the player wants to do. Format each choice on a new line 
            starting with a number and period (1., 2., 3., etc.).""")
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
        
        # Generate narrative with explicit location focus
        response = self.llm.invoke(
            self.narrator_prompt.format_messages(
                location=location,
                personality=personality,
                story_context=story_context_text,
                kanto_knowledge=kanto_knowledge
            )
        )
        
        # Validate that the generated story is about the correct location
        narrative_content = response.content
        if location.lower() not in narrative_content.lower() and "lavender town" in narrative_content.lower():
            # If AI generated story about wrong location, regenerate with stronger location focus
            logger.warning(f"AI generated story about wrong location. Expected: {location}, got Lavender Town. Regenerating...")
            
            # Create a more explicit prompt
            explicit_prompt = f"""Write a vivid narrative segment for a Pokémon adventure that takes place specifically in {location}.

Location: {location} (IMPORTANT: The story must take place in {location}, not any other location)
Player's Personality: {personality}
Recent Events: {story_context_text}
Available Knowledge: {kanto_knowledge}

Write an engaging story segment that describes what happens next in {location}. 
Make it immersive, emotional, and true to the Pokémon world. Focus on the player's experience 
in {location} and how their personality influences the situation. DO NOT mention any other locations."""
            
            response = self.llm.invoke([HumanMessage(content=explicit_prompt)])
            narrative_content = response.content
        
        return {
            "narrative": narrative_content,
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
        
        # Extract location from current situation for better context
        location = "Pallet Town"  # default
        if "pallet town" in current_situation.lower():
            location = "Pallet Town"
        elif "route 1" in current_situation.lower():
            location = "Route 1"
        elif "viridian city" in current_situation.lower():
            location = "Viridian City"
        
        # Generate choices with explicit location focus
        response = self.llm.invoke(
            self.choice_prompt.format_messages(
                current_situation=f"Player is in {location}. {current_situation}",
                personality=personality,
                active_promises=active_promises_text,
                key_relationships=key_relationships_text,
                kanto_knowledge=story_context[:max_knowledge_items]
            )
        )
        
        # Parse choices from response with improved logic
        choices = []
        lines = response.content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try different patterns to extract choice text
            choice_text = None
            
            # Pattern 1: "1. Choice text"
            if line[0].isdigit() and '. ' in line:
                choice_text = line.split('. ', 1)[1].strip()
            
            # Pattern 2: "- Choice text" or "* Choice text" or "• Choice text"
            elif line.startswith(('-', '*', '•')):
                choice_text = line[1:].strip()
            
            # Pattern 3: Just clean text (fallback)
            elif len(line) > 10 and not line.startswith('*') and not ':' in line:
                choice_text = line
            
            if choice_text and len(choice_text) > 10:
                # Validate that it's not template text and is location-appropriate
                if not any(keyword in choice_text.lower() for keyword in [
                    'current situation', 'personality', 'active promises', 
                    'key relationships', 'available knowledge', 'template'
                ]):
                    # Check if choice mentions wrong location
                    wrong_locations = ['lavender town', 'pokémon tower', 'celadon city']
                    if not any(wrong_loc in choice_text.lower() for wrong_loc in wrong_locations):
                        choices.append({
                            "text": choice_text,
                            "effects": self._estimate_choice_effects(choice_text, personality)
                        })
        
        # If AI generated poor choices, use fallback
        if len(choices) < 2:
            logger.warning("AI generated poor choices, using fallback choices")
            return self._generate_fallback_choices(current_situation, personality)
        
        # Check if choices are location-appropriate
        wrong_location_keywords = ['lavender town', 'pokémon tower', 'celadon city', 'team rocket', 'officer jenny']
        inappropriate_choices = []
        
        for choice in choices:
            choice_text = choice.get("text", "").lower()
            if any(keyword in choice_text for keyword in wrong_location_keywords):
                inappropriate_choices.append(choice)
        
        # If too many inappropriate choices, use fallback
        if len(inappropriate_choices) > len(choices) / 2:
            logger.warning("AI generated location-inappropriate choices, using fallback choices")
            return self._generate_fallback_choices(current_situation, personality)
        
        # Filter out inappropriate choices
        valid_choices = [choice for choice in choices if choice not in inappropriate_choices]
        
        # If we don't have enough valid choices, use fallback
        if len(valid_choices) < 2:
            logger.warning("Not enough valid choices after filtering, using fallback choices")
            return self._generate_fallback_choices(current_situation, personality)
        
        return valid_choices

    def _generate_fallback_choices(self, current_situation: str, personality: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate fallback choices when AI generation fails."""
        # Get personality traits
        friendship = personality.get("friendship", 5)
        courage = personality.get("courage", 5)
        curiosity = personality.get("curiosity", 5)
        wisdom = personality.get("wisdom", 5)
        determination = personality.get("determination", 5)
        
        # Location-specific fallback choices
        location_choices = {
            "pallet town": [
                {
                    "text": "Visit Professor Oak's laboratory to get your first Pokémon",
                    "effects": {"curiosity": 1, "determination": 1}
                },
                {
                    "text": "Explore Pallet Town and meet the neighbors",
                    "effects": {"friendship": 1, "curiosity": 1}
                },
                {
                    "text": "Talk to your mom before leaving on your journey",
                    "effects": {"friendship": 1, "wisdom": 1}
                },
                {
                    "text": "Check out the local Pokémon Center to learn about healing",
                    "effects": {"curiosity": 1, "wisdom": 1}
                }
            ],
            "route 1": [
                {
                    "text": "Train with wild Pokémon to gain experience",
                    "effects": {"courage": 1, "determination": 1}
                },
                {
                    "text": "Help a fellow trainer who seems to be in trouble",
                    "effects": {"friendship": 1, "courage": 1}
                },
                {
                    "text": "Explore the tall grass to find rare Pokémon",
                    "effects": {"curiosity": 1, "courage": 1}
                },
                {
                    "text": "Take a moment to rest and plan your next move",
                    "effects": {"wisdom": 1, "determination": 1}
                }
            ],
            "viridian city": [
                {
                    "text": "Challenge the Viridian Gym to test your skills",
                    "effects": {"courage": 1, "determination": 1}
                },
                {
                    "text": "Visit the Pokémon Center to heal your team",
                    "effects": {"friendship": 1, "wisdom": 1}
                },
                {
                    "text": "Explore the city and meet other trainers",
                    "effects": {"friendship": 1, "curiosity": 1}
                },
                {
                    "text": "Stock up on supplies at the PokéMart",
                    "effects": {"wisdom": 1, "determination": 1}
                }
            ]
        }
        
        # Determine location from current situation
        location = "pallet town"  # default
        for loc in location_choices.keys():
            if loc in current_situation.lower():
                location = loc
                break
        
        # Return location-specific choices or generic ones
        return location_choices.get(location, [
            {
                "text": "Continue exploring the area",
                "effects": {"curiosity": 1}
            },
            {
                "text": "Interact with the local people",
                "effects": {"friendship": 1}
            },
            {
                "text": "Face any challenges that come your way",
                "effects": {"courage": 1}
            },
            {
                "text": "Take time to think and plan",
                "effects": {"wisdom": 1}
            }
        ])

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