"""
Game manager for handling game state and API operations.
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from bethemc.core.game import GameLoop
from bethemc.core.progression import ProgressionManager
from bethemc.ai.story_generator import StoryGenerator
from bethemc.utils.config import Config
from bethemc.utils.logger import setup_logger
from .models import PersonalityTraits, GameState, NarrativeResponse, Choice

logger = setup_logger(__name__)

class GameManager:
    """Manages game state and provides API operations."""
    
    def __init__(self):
        """Initialize the game manager."""
        self.config = Config()
        self.active_games: Dict[str, GameSession] = {}
        self.save_dir = Path(self.config.get("save_dir", "data/saves"))
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def create_new_game(self, session_id: str, starting_location: str = "Pallet Town", 
                       personality: Optional[PersonalityTraits] = None) -> 'GameSession':
        """Create a new game session."""
        if personality is None:
            personality = PersonalityTraits(
                friendship=0.5,
                courage=0.5,
                curiosity=0.5,
                wisdom=0.5,
                determination=0.5
            )
        
        session = GameSession(
            session_id=session_id,
            config=self.config,
            starting_location=starting_location,
            initial_personality=personality
        )
        
        self.active_games[session_id] = session
        logger.info(f"Created new game session: {session_id}")
        return session
    
    def get_game_session(self, session_id: str) -> Optional['GameSession']:
        """Get an active game session."""
        return self.active_games.get(session_id)
    
    def save_game(self, session_id: str, save_name: str) -> bool:
        """Save a game session."""
        session = self.get_game_session(session_id)
        if not session:
            return False
        
        save_data = session.get_save_data()
        save_file = self.save_dir / f"{save_name}.json"
        
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=str)
            logger.info(f"Saved game {session_id} as {save_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game {session_id}: {e}")
            return False
    
    def load_game(self, session_id: str, save_name: str) -> Optional['GameSession']:
        """Load a game session."""
        save_file = self.save_dir / f"{save_name}.json"
        
        if not save_file.exists():
            logger.error(f"Save file not found: {save_name}")
            return None
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            session = GameSession.load_from_save_data(
                session_id=session_id,
                config=self.config,
                save_data=save_data
            )
            
            self.active_games[session_id] = session
            logger.info(f"Loaded game {session_id} from {save_name}")
            return session
        except Exception as e:
            logger.error(f"Failed to load game {save_name}: {e}")
            return None
    
    def list_saves(self) -> List[str]:
        """List available save files."""
        saves = []
        for save_file in self.save_dir.glob("*.json"):
            saves.append(save_file.stem)
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file."""
        save_file = self.save_dir / f"{save_name}.json"
        if save_file.exists():
            save_file.unlink()
            logger.info(f"Deleted save file: {save_name}")
            return True
        return False

class GameSession:
    """Represents an active game session."""
    
    def __init__(self, session_id: str, config: Config, starting_location: str, 
                 initial_personality: PersonalityTraits):
        """Initialize a game session."""
        self.session_id = session_id
        self.config = config
        self.story_generator = StoryGenerator(config)
        self.progression = ProgressionManager(config)
        
        # Initialize game state
        self.location = starting_location
        self.personality = initial_personality
        self.recent_events = []
        self.relationships = {}
        self.pokemon_partners = []
        self.memories = []
        
        # Generate initial narrative
        self.current_narrative = None
        self.current_choices = []
        self._generate_initial_narrative()
    
    def _generate_initial_narrative(self):
        """Generate the initial narrative for the game."""
        try:
            narrative_result = self.story_generator.generate_narrative(
                location=self.location,
                personality=self.personality.dict(),
                recent_events=self.recent_events
            )
            
            self.current_narrative = narrative_result["narrative"]
            
            # Generate initial choices
            choices = self.story_generator.generate_choices(
                current_situation=self.current_narrative,
                personality=self.personality.dict(),
                active_promises=narrative_result.get("active_promises", []),
                key_relationships=narrative_result.get("key_relationships", [])
            )
            
            self.current_choices = choices
            
        except Exception as e:
            logger.error(f"Failed to generate initial narrative: {e}")
            self.current_narrative = "Welcome to your Pokémon adventure in the Kanto region!"
            self.current_choices = [
                {"text": "Begin your journey", "effects": {}}
            ]
    
    def make_choice(self, choice_index: int) -> Optional[NarrativeResponse]:
        """Make a choice and progress the story."""
        if not (0 <= choice_index < len(self.current_choices)):
            return None
        
        choice = self.current_choices[choice_index]
        
        # Update recent events
        self.recent_events.insert(0, choice["text"])
        if len(self.recent_events) > 5:
            self.recent_events.pop()
        
        # Update personality based on choice effects
        for trait, effect in choice["effects"].items():
            if hasattr(self.personality, trait):
                current_value = getattr(self.personality, trait)
                new_value = max(0.0, min(1.0, current_value + effect))
                setattr(self.personality, trait, new_value)
        
        # Add choice to progression system
        self.progression.add_scene({
            "location": self.location,
            "description": choice["text"],
            "choices": [choice],
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate next narrative
        try:
            narrative_result = self.story_generator.generate_narrative(
                location=self.location,
                personality=self.personality.dict(),
                recent_events=self.recent_events
            )
            
            self.current_narrative = narrative_result["narrative"]
            
            # Generate new choices
            new_choices = self.story_generator.generate_choices(
                current_situation=self.current_narrative,
                personality=self.personality.dict(),
                active_promises=narrative_result.get("active_promises", []),
                key_relationships=narrative_result.get("key_relationships", [])
            )
            
            self.current_choices = new_choices
            
            # Convert choices to Choice objects
            choice_objects = [
                Choice(text=choice["text"], effects=choice["effects"])
                for choice in self.current_choices
            ]
            
            return NarrativeResponse(
                narrative=self.current_narrative,
                choices=choice_objects,
                location=self.location,
                personality=self.personality,
                active_promises=narrative_result.get("active_promises", []),
                key_relationships=narrative_result.get("key_relationships", []),
                story_context=narrative_result.get("context", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to generate narrative after choice: {e}")
            return None
    
    def get_current_state(self) -> NarrativeResponse:
        """Get the current game state."""
        choice_objects = [
            Choice(text=choice["text"], effects=choice["effects"])
            for choice in self.current_choices
        ]
        
        return NarrativeResponse(
            narrative=self.current_narrative or "Welcome to your Pokémon adventure!",
            choices=choice_objects,
            location=self.location,
            personality=self.personality,
            active_promises=[],
            key_relationships=[],
            story_context={}
        )
    
    def add_memory(self, memory_type: str, content: str, location: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a memory to the game session."""
        try:
            self.progression.knowledge_base.add_memory({
                "memory_type": memory_type,
                "content": content,
                "timestamp": datetime.now().timestamp(),
                "metadata": metadata or {}
            })
            self.memories.append(content)
            return True
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False
    
    def get_compressed_context(self) -> Dict[str, Any]:
        """Get compressed context for the current location."""
        return self.progression.get_compressed_context(self.location)
    
    def get_save_data(self) -> Dict[str, Any]:
        """Get save data for the session."""
        return {
            "session_id": self.session_id,
            "location": self.location,
            "personality": self.personality.dict(),
            "recent_events": self.recent_events,
            "relationships": self.relationships,
            "pokemon_partners": self.pokemon_partners,
            "memories": self.memories,
            "current_narrative": self.current_narrative,
            "current_choices": self.current_choices,
            "progression_data": {
                "scene_history": self.progression.scene_history
            }
        }
    
    @classmethod
    def load_from_save_data(cls, session_id: str, config: Config, save_data: Dict[str, Any]) -> 'GameSession':
        """Create a session from save data."""
        session = cls.__new__(cls)
        session.session_id = session_id
        session.config = config
        session.story_generator = StoryGenerator(config)
        session.progression = ProgressionManager(config)
        
        # Load game state
        session.location = save_data["location"]
        session.personality = PersonalityTraits(**save_data["personality"])
        session.recent_events = save_data["recent_events"]
        session.relationships = save_data["relationships"]
        session.pokemon_partners = save_data["pokemon_partners"]
        session.memories = save_data["memories"]
        session.current_narrative = save_data["current_narrative"]
        session.current_choices = save_data["current_choices"]
        
        # Load progression data
        if "progression_data" in save_data:
            session.progression.scene_history = save_data["progression_data"]["scene_history"]
        
        return session 