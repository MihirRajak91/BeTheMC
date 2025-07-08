"""
Clean story generator implementation.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from bethemc.models.core import PersonalityTraits, Choice, NarrativeSegment
from ..ai.providers import get_llm_provider
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class StoryGeneratorV2:
    """Clean implementation of story generation."""
    
    def __init__(self, config: Config):
        """Initialize the story generator."""
        self.config = config
        llm_config = config.get("ai.llm")
        self.llm = get_llm_provider(llm_config["provider"]).get_llm(llm_config)
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Set up prompt templates."""
        self.narrator_prompt = """You are a master storyteller in the Pokémon world, specifically in the Kanto region.
Your role is to create an immersive, personalized story for the player based on their choices and personality.
Use the provided context to maintain consistency while creating unique narratives.
Focus on creating emotional connections and meaningful choices that reflect the player's personality.

Create a narrative segment based on the following context:

Current Location: {location}
Player's Personality: {personality}
Recent Events: {recent_events}
Story Context: {context}

Generate a vivid description of the current situation and present the player with meaningful choices that reflect their personality."""

        self.choice_prompt = """You are a choice designer for a Pokémon adventure.
Create meaningful choices that reflect the player's personality and impact the story.
Each choice should have clear consequences and align with the player's traits.

Design choices for the following situation:

Current Situation: {situation}
Player's Personality: {personality}
Story Context: {context}

Generate 3-4 meaningful choices that the player can make, each with potential consequences.
Format each choice as: "Choice X: [description] (effects: [trait: value, ...])" """

    def generate_narrative(self, 
                          location: str,
                          personality: PersonalityTraits,
                          recent_events: List[str],
                          context: Dict[str, Any]) -> NarrativeSegment:
        """Generate a narrative segment."""
        try:
            # Format personality for prompt
            personality_text = f"Friendship: {personality.friendship}, Courage: {personality.courage}, Curiosity: {personality.curiosity}, Wisdom: {personality.wisdom}, Determination: {personality.determination}"
            
            # Format context
            context_text = self._format_context(context)
            
            # Generate narrative
            prompt = self.narrator_prompt.format(
                location=location,
                personality=personality_text,
                recent_events=" | ".join(recent_events),
                context=context_text
            )
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            narrative_content = response.content if hasattr(response, 'content') else str(response)
            
            return NarrativeSegment(
                content=narrative_content,
                location=location,
                timestamp=datetime.now(),
                context=context
            )
        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            return NarrativeSegment(
                content=f"Welcome to {location}! Your adventure begins here.",
                location=location,
                timestamp=datetime.now(),
                context=context
            )
    
    def generate_choices(self,
                        situation: str,
                        personality: PersonalityTraits,
                        context: Dict[str, Any]) -> List[Choice]:
        """Generate choices for a situation."""
        try:
            # Format personality for prompt
            personality_text = f"Friendship: {personality.friendship}, Courage: {personality.courage}, Curiosity: {personality.curiosity}, Wisdom: {personality.wisdom}, Determination: {personality.determination}"
            
            # Format context
            context_text = self._format_context(context)
            
            # Generate choices
            prompt = self.choice_prompt.format(
                situation=situation,
                personality=personality_text,
                context=context_text
            )
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse choices
            choices = self._parse_choices(response_text)
            
            return choices
        except Exception as e:
            logger.error(f"Failed to generate choices: {e}")
            return [
                Choice(text="Continue your journey", effects={}),
                Choice(text="Explore the area", effects={"curiosity": 0.1}),
                Choice(text="Rest and reflect", effects={"wisdom": 0.1})
            ]
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompts."""
        if not context:
            return "Beginning of adventure"
        
        parts = []
        
        if "story_summary" in context:
            parts.append(f"Story: {context['story_summary']}")
        
        if "active_promises" in context:
            promises = context["active_promises"]
            if promises:
                parts.append(f"Active Promises: {'; '.join(promises)}")
        
        if "key_relationships" in context:
            relationships = context["key_relationships"]
            if relationships:
                parts.append(f"Key Relationships: {'; '.join(relationships)}")
        
        return " | ".join(parts) if parts else "Beginning of adventure"
    
    def _parse_choices(self, response_text: str) -> List[Choice]:
        """Parse choices from LLM response."""
        choices = []
        
        # Simple parsing - look for lines starting with "Choice"
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.lower().startswith('choice'):
                # Extract choice text and effects
                choice_text = line.split(':', 1)[1].split('(')[0].strip()
                effects = {}
                
                # Look for effects in parentheses
                if '(' in line and ')' in line:
                    effects_part = line.split('(')[1].split(')')[0]
                    if 'effects:' in effects_part.lower():
                        effects_text = effects_part.split('effects:')[1].strip()
                        effects = self._parse_effects(effects_text)
                
                choices.append(Choice(text=choice_text, effects=effects))
        
        # If no choices found, create defaults
        if not choices:
            choices = [
                Choice(text="Continue your journey", effects={}),
                Choice(text="Explore the area", effects={"curiosity": 0.1}),
                Choice(text="Rest and reflect", effects={"wisdom": 0.1})
            ]
        
        return choices
    
    def _parse_effects(self, effects_text: str) -> Dict[str, float]:
        """Parse effects from text."""
        effects = {}
        
        # Look for trait: value patterns
        import re
        pattern = r'(\w+):\s*([0-9.]+)'
        matches = re.findall(pattern, effects_text)
        
        for trait, value in matches:
            try:
                effects[trait.lower()] = float(value)
            except ValueError:
                continue
        
        return effects 