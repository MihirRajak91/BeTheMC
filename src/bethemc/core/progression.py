"""
Simplified progression tracking system that uses LLM for narrative decisions.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from bethemc.data.vector_store import KantoKnowledgeBase

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
        
        # Enhanced tracking for relationships and character growth
        self.character_relationships: Dict[str, Dict[str, Any]] = {}
        self.character_growth: Dict[str, List[str]] = {}
        self.seasonal_memories: Dict[str, List[dict]] = {}
        
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
                self.character_relationships = data.get("character_relationships", {})
                self.character_growth = data.get("character_growth", {})
                self.seasonal_memories = data.get("seasonal_memories", {})

    def _save_progression(self):
        """Save progression data to file."""
        save_dir = self.config.get("save_dir", "data/saves")
        save_file = Path(save_dir) / "progression.json"
        # Ensure save directory exists
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scene_history": self.scene_history,
                "character_relationships": self.character_relationships,
                "character_growth": self.character_growth,
                "seasonal_memories": self.seasonal_memories
            }, f, indent=2)

    def add_memory(self, memory_type: str, content: str, metadata: dict = None) -> str:
        """Add a memory to progression tracking."""
        metadata = metadata or {}
        
        memory = StoryMemory(
            memory_type=memory_type,
            content=content,
            timestamp=datetime.now().timestamp(),
            metadata=metadata
        )
        
        # Add to knowledge base for vector search
        memory_id = self.knowledge_base.add_memory({
            "memory_type": memory.memory_type,
            "content": memory.content,
            "timestamp": memory.timestamp,
            "metadata": memory.metadata
        })
        
        # Track character-specific memories
        if 'character' in metadata:
            character_name = metadata['character']
            self._update_character_relationship(character_name, memory)
        
        # Track seasonal memories
        if 'season' in metadata:
            season = metadata['season']
            if season not in self.seasonal_memories:
                self.seasonal_memories[season] = []
            self.seasonal_memories[season].append({
                "content": content,
                "timestamp": memory.timestamp,
                "metadata": metadata
            })
        
        self._save_progression()
        return memory_id

    def get_comprehensive_story_context(self, current_location: str = None) -> Dict[str, Any]:
        """Get comprehensive story context including enhanced character data."""
        # Get recent scene history
        recent_scenes = self.scene_history[-5:] if self.scene_history else []
        
        # Get character-driven context
        character_context = self._get_enhanced_character_context(current_location)
        
        # Get seasonal context
        seasonal_context = self.knowledge_base.get_seasonal_context()
        
        # Get location context if provided
        location_context = {}
        if current_location:
            location_context = self.knowledge_base.get_enhanced_location_info(current_location)
        
        return {
            "story_summary": self._generate_story_summary(),
            "current_relationships": character_context["relationships"],
            "active_promises": self._get_active_promises(),
            "recent_discoveries": self._get_recent_discoveries(),
            "character_growth": character_context["growth"],
            "location_context": location_context,
            "seasonal_context": seasonal_context,
            "recent_scenes": recent_scenes
        }

    def update_character_relationship(self, character_name: str, relationship_change: str, strength: float = 0.1):
        """Update relationship with a character based on interactions."""
        if character_name not in self.character_relationships:
            # Initialize with character personality data
            character_info = self.knowledge_base.get_character_personality(character_name)
            self.character_relationships[character_name] = {
                "friendship_level": 0.0,
                "trust_level": 0.0,
                "respect_level": 0.0,
                "interactions": [],
                "personality": character_info.get("core_traits", []),
                "last_interaction": None
            }
        
        relationship = self.character_relationships[character_name]
        
        # Update relationship based on interaction type
        if "positive" in relationship_change.lower():
            relationship["friendship_level"] = min(1.0, relationship["friendship_level"] + strength)
            relationship["trust_level"] = min(1.0, relationship["trust_level"] + strength * 0.5)
        elif "trust" in relationship_change.lower():
            relationship["trust_level"] = min(1.0, relationship["trust_level"] + strength)
        elif "respect" in relationship_change.lower():
            relationship["respect_level"] = min(1.0, relationship["respect_level"] + strength)
        
        # Record the interaction
        relationship["interactions"].append({
            "type": relationship_change,
            "timestamp": datetime.now().timestamp(),
            "strength": strength
        })
        relationship["last_interaction"] = datetime.now().timestamp()
        
        # Add character growth if significant relationship change
        if strength > 0.3:
            self._add_character_growth(character_name, f"Developed {relationship_change} through meaningful interaction")
        
        self._save_progression()

    def track_pokemon_bond(self, pokemon_name: str, bond_type: str, strength: float = 0.1):
        """Track bonding with Pokémon using personality data."""
        pokemon_info = self.knowledge_base.get_pokemon_personality(pokemon_name)
        
        # Create memory of the bonding experience
        self.add_memory(
            memory_type="pokemon_bond",
            content=f"Developed {bond_type} with {pokemon_name}",
            metadata={
                "pokemon": pokemon_name,
                "bond_type": bond_type,
                "strength": strength,
                "pokemon_personality": pokemon_info.get("temperament", ""),
                "traits": pokemon_info.get("personality_traits", [])
            }
        )

    def add_seasonal_event_memory(self, event_name: str, location: str, participants: List[str] = None):
        """Add memory of participating in a seasonal event."""
        seasonal_context = self.knowledge_base.get_seasonal_context()
        
        self.add_memory(
            memory_type="seasonal_event",
            content=f"Participated in {event_name} at {location}",
            metadata={
                "event": event_name,
                "location": location,
                "participants": participants or [],
                "season": seasonal_context.get("season", ""),
                "atmosphere": seasonal_context.get("atmosphere", ""),
                "seasonal_effects": True
            }
        )

    def get_character_relationship_status(self, character_name: str) -> Dict[str, Any]:
        """Get detailed relationship status with a character."""
        if character_name not in self.character_relationships:
            # Initialize if not exists
            self.update_character_relationship(character_name, "first_meeting", 0.0)
        
        relationship = self.character_relationships[character_name]
        character_info = self.knowledge_base.get_character_personality(character_name)
        
        return {
            "character": character_name,
            "personality": character_info.get("core_traits", []),
            "friendship_level": relationship["friendship_level"],
            "trust_level": relationship["trust_level"],
            "respect_level": relationship["respect_level"],
            "recent_interactions": relationship["interactions"][-3:],  # Last 3 interactions
            "relationship_summary": self._generate_relationship_summary(character_name, relationship),
            "growth_potential": character_info.get("growth_potential", [])
        }

    def get_seasonal_story_elements(self) -> Dict[str, Any]:
        """Get seasonal elements for story enhancement."""
        seasonal_context = self.knowledge_base.get_seasonal_context()
        current_season = seasonal_context.get("season", "")
        
        # Get relevant seasonal memories
        seasonal_memories = self.seasonal_memories.get(current_season, [])
        
        return {
            "current_season": current_season,
            "seasonal_atmosphere": seasonal_context.get("atmosphere", ""),
            "active_events": seasonal_context.get("events", []),
            "seasonal_memories": seasonal_memories[-5:],  # Last 5 seasonal memories
            "pokemon_behavior_changes": seasonal_context.get("pokemon_behavior", {}),
            "weather_effects": seasonal_context.get("weather_effects", {})
        }

    # ====== ENHANCED HELPER METHODS ======

    def _get_enhanced_character_context(self, current_location: str = None) -> Dict[str, Any]:
        """Get enhanced character context including personalities and relationships."""
        relationships = {}
        growth = {}
        
        # Get available characters at location
        if current_location:
            available_characters = self._get_location_characters(current_location)
            
            for character_name in available_characters:
                relationships[character_name] = self.get_character_relationship_status(character_name)
                growth[character_name] = self.character_growth.get(character_name, [])
        
        # Include existing relationships
        for character_name in self.character_relationships:
            if character_name not in relationships:
                relationships[character_name] = self.get_character_relationship_status(character_name)
                growth[character_name] = self.character_growth.get(character_name, [])
        
        return {
            "relationships": relationships,
            "growth": growth
        }

    def _get_location_characters(self, location: str) -> List[str]:
        """Get characters available at a specific location."""
        # This could be enhanced to use location data
        location_characters = {
            "pewter-city": ["Brock"],
            "cerulean-city": ["Misty"],
            "vermilion-city": ["Lt. Surge"],
            "celadon-city": ["Erika"],
            "fuchsia-city": ["Koga"],
            "saffron-city": ["Sabrina"],
            "cinnabar-island": ["Blaine"],
            "viridian-city": ["Giovanni"],
            "pallet-town": ["Professor Oak"]
        }
        
        location_key = location.lower().replace(" ", "-")
        return location_characters.get(location_key, [])

    def _update_character_relationship(self, character_name: str, memory: StoryMemory):
        """Update character relationship based on memory."""
        # Initialize relationship if needed
        if character_name not in self.character_relationships:
            self.update_character_relationship(character_name, "first_meeting", 0.0)
        
        # Analyze memory content for relationship changes
        content_lower = memory.content.lower()
        
        if any(word in content_lower for word in ["helped", "assisted", "supported"]):
            self.update_character_relationship(character_name, "positive_interaction", 0.2)
        elif any(word in content_lower for word in ["trusted", "confided", "shared"]):
            self.update_character_relationship(character_name, "trust_building", 0.3)
        elif any(word in content_lower for word in ["respected", "admired", "impressed"]):
            self.update_character_relationship(character_name, "respect_building", 0.2)

    def _add_character_growth(self, character_name: str, growth_description: str):
        """Add character growth tracking."""
        if character_name not in self.character_growth:
            self.character_growth[character_name] = []
        
        self.character_growth[character_name].append({
            "description": growth_description,
            "timestamp": datetime.now().timestamp()
        })

    def _generate_relationship_summary(self, character_name: str, relationship: Dict[str, Any]) -> str:
        """Generate a summary of the relationship with a character."""
        friendship = relationship["friendship_level"]
        trust = relationship["trust_level"]
        respect = relationship["respect_level"]
        
        if friendship > 0.7:
            return f"Close friend with deep bond"
        elif trust > 0.7:
            return f"Trusted companion"
        elif respect > 0.7:
            return f"Respected ally"
        elif friendship > 0.3:
            return f"Developing friendship"
        else:
            return f"New acquaintance"

    # ====== ORIGINAL METHODS (PRESERVED) ======

    def get_story_context(self) -> str:
        """Get story context for LLM prompts."""
        if not self.scene_history:
            return "This is the beginning of the adventure."
        
        # Get last few scenes for context
        recent_scenes = self.scene_history[-3:]
        context = "Recent story context:\n"
        
        for i, scene in enumerate(recent_scenes, 1):
            context += f"Scene {i}: {scene.get('summary', 'A scene in the adventure.')}\n"
        
        return context

    def _generate_story_summary(self) -> str:
        """Generate a summary of the story so far."""
        if not self.scene_history:
            return "The adventure is just beginning."
        
        # Simple summary based on scene count and recent events
        scene_count = len(self.scene_history)
        recent_scene = self.scene_history[-1] if self.scene_history else {}
        
        return f"After {scene_count} scenes of adventure, the story continues from {recent_scene.get('location', 'an unknown location')}."

    def _get_active_promises(self) -> List[str]:
        """Get list of active promises/commitments."""
        promise_memories = self.knowledge_base.get_memories_by_type("promise", limit=5)
        return [memory["content"] for memory in promise_memories]

    def _get_recent_discoveries(self) -> List[str]:
        """Get list of recent discoveries."""
        discovery_memories = self.knowledge_base.get_memories_by_type("discovery", limit=3)
        return [memory["content"] for memory in discovery_memories] 