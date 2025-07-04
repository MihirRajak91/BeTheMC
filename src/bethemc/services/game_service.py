"""
Game service for orchestrating game logic.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from ..core.interfaces import (
    StoryGenerator, KnowledgeBase, ProgressionTracker, 
    GameState, SaveManager, PersonalityTraits, Choice, NarrativeSegment
)
from ..core.state import GameStateImpl
from ..utils.logger import setup_logger
from ..models.core import GameState, Player, Story, Choice, Memory, PersonalityTrait, GameProgression

logger = setup_logger(__name__)

class GameService:
    """Service for managing game logic and state."""
    
    def __init__(self):
        """Initialize the game service."""
        # The new modular approach doesn't need these dependencies
        # as the GameState model is self-contained
        pass
    
    def create_session(self, session_id: str, location: str = "Pallet Town", 
                      personality: Optional[PersonalityTraits] = None) -> GameStateImpl:
        """Create a new game session."""
        if personality is None:
            personality = PersonalityTraits(
                friendship=0.5, courage=0.5, curiosity=0.5,
                wisdom=0.5, determination=0.5
            )
        
        game_state = GameStateImpl(
            location=location,
            personality=personality
        )
        
        logger.info(f"Created new game session: {session_id}")
        return game_state
    
    def get_session(self, session_id: str) -> Optional[GameStateImpl]:
        """Get an active game session."""
        return None  # The new modular approach doesn't use active sessions
    
    def make_choice(self, session_id: str, choice_index: int) -> Optional[Dict[str, Any]]:
        """Make a choice and progress the story."""
        return None  # The new modular approach doesn't use session-based choices
    
    def get_current_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current game state."""
        return None  # The new modular approach doesn't use session-based states
    
    def add_memory(self, session_id: str, memory_type: str, content: str, 
                   location: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a memory to the session."""
        return False  # The new modular approach doesn't use session-based memories
    
    def get_compressed_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get compressed context for the session."""
        return None  # The new modular approach doesn't use session-based contexts
    
    def save_session(self, session_id: str, save_name: str) -> bool:
        """Save a game session."""
        return False  # The new modular approach doesn't use session-based saves
    
    def load_session(self, session_id: str, save_name: str) -> Optional[GameStateImpl]:
        """Load a game session."""
        return None  # The new modular approach doesn't use session-based loads
    
    def _generate_current_narrative(self, session: GameStateImpl) -> Optional[Dict[str, Any]]:
        """Generate current narrative and choices."""
        return None  # The new modular approach doesn't use narrative generation
    
    def _generate_next_narrative(self, session: GameStateImpl) -> Optional[Dict[str, Any]]:
        """Generate next narrative after a choice."""
        return None  # The new modular approach doesn't use narrative generation

    async def start_new_game(self, player_name: str, personality_traits: Optional[Dict[str, int]] = None) -> GameState:
        """Start a new game and return a modular GameState."""
        try:
            # Create player with default personality traits if none provided
            if personality_traits is None:
                personality_traits = {
                    "friendship": 5,
                    "courage": 5,
                    "curiosity": 5,
                    "wisdom": 5,
                    "determination": 5
                }
            
            player = Player(
                id=str(uuid4()),
                name=player_name,
                personality_traits=personality_traits
            )
            
            # Create initial story
            current_story = Story(
                id=str(uuid4()),
                title="Welcome to Kanto",
                content="You wake up in your room in Pallet Town, ready to begin your Pokémon adventure!",
                location="Pallet Town"
            )
            
            # Create initial choices
            available_choices = [
                Choice(
                    id=str(uuid4()),
                    text="Visit Professor Oak's lab",
                    effects={"curiosity": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Explore Pallet Town first",
                    effects={"courage": 1}
                )
            ]
            
            # Initialize empty memories and progression
            memories = []
            progression = GameProgression(
                current_location="Pallet Town",
                completed_events=[],
                relationships={},
                inventory=[]
            )
            
            # Create and return the game state
            game_state = GameState(
                player=player,
                current_story=current_story,
                available_choices=available_choices,
                memories=memories,
                progression=progression
            )
            
            logger.info(f"Started new game for player: {player_name}")
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to start new game: {e}")
            raise

    async def process_choice(self, game_state: GameState, choice_id: str) -> GameState:
        """Process a player's choice and return updated game state."""
        try:
            # Find the chosen choice
            chosen_choice = None
            for choice in game_state.available_choices:
                if choice.id == choice_id:
                    chosen_choice = choice
                    break
            
            if not chosen_choice:
                raise ValueError(f"Choice with id {choice_id} not found")
            
            # Update personality traits based on choice effects
            updated_personality = game_state.player.personality_traits.copy()
            for trait, effect in chosen_choice.effects.items():
                if trait in updated_personality:
                    updated_personality[trait] = min(10, max(0, updated_personality[trait] + effect))
            
            # Create updated player
            updated_player = Player(
                id=game_state.player.id,
                name=game_state.player.name,
                personality_traits=updated_personality
            )
            
            # Generate new story based on choice
            new_story = Story(
                id=str(uuid4()),
                title="Story Continues",
                content=f"You chose: {chosen_choice.text}. The adventure continues...",
                location=game_state.progression.current_location
            )
            
            # Generate new choices
            new_choices = [
                Choice(
                    id=str(uuid4()),
                    text="Continue exploring",
                    effects={"curiosity": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Take a moment to reflect",
                    effects={"wisdom": 1}
                )
            ]
            
            # Update progression
            updated_progression = GameProgression(
                current_location=game_state.progression.current_location,
                completed_events=game_state.progression.completed_events + [chosen_choice.text],
                relationships=game_state.progression.relationships,
                inventory=game_state.progression.inventory
            )
            
            # Create and return updated game state
            updated_game_state = GameState(
                player=updated_player,
                current_story=new_story,
                available_choices=new_choices,
                memories=game_state.memories,
                progression=updated_progression
            )
            
            logger.info(f"Processed choice for player {game_state.player.name}")
            return updated_game_state
            
        except Exception as e:
            logger.error(f"Failed to process choice: {e}")
            raise

    async def add_memory(self, game_state: GameState, memory_text: str, memory_type: str = "general") -> GameState:
        """Add a memory to the game state."""
        try:
            new_memory = Memory(
                id=str(uuid4()),
                content=memory_text,
                memory_type=memory_type,
                timestamp=datetime.now()
            )
            
            updated_memories = game_state.memories + [new_memory]
            
            updated_game_state = GameState(
                player=game_state.player,
                current_story=game_state.current_story,
                available_choices=game_state.available_choices,
                memories=updated_memories,
                progression=game_state.progression
            )
            
            logger.info(f"Added memory for player {game_state.player.name}")
            return updated_game_state
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            raise

    async def update_personality(self, game_state: GameState, trait: str, value: int) -> GameState:
        """Update a player's personality trait."""
        try:
            updated_personality = game_state.player.personality_traits.copy()
            updated_personality[trait] = min(10, max(0, value))
            
            updated_player = Player(
                id=game_state.player.id,
                name=game_state.player.name,
                personality_traits=updated_personality
            )
            
            updated_game_state = GameState(
                player=updated_player,
                current_story=game_state.current_story,
                available_choices=game_state.available_choices,
                memories=game_state.memories,
                progression=game_state.progression
            )
            
            logger.info(f"Updated personality trait {trait} for player {game_state.player.name}")
            return updated_game_state
            
        except Exception as e:
            logger.error(f"Failed to update personality: {e}")
            raise 