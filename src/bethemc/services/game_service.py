"""
Game service for orchestrating game logic.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from src.bethemc.utils.logger import setup_logger
from src.bethemc.models.models import GameState, Player, Story, Choice, Memory, GameProgression

logger = setup_logger(__name__)

class GameService:
    """Service for managing game logic and state.
    This service is responsible for managing the game state, including the player's progress, choices, and memories.
    It also handles the generation of new stories and choices, as well as the updating of the player's personality traits.
    The service is responsible for the overall flow of the game, including the initial setup, the main game loop, and the end of the game.
    The service is also responsible for the generation of the game's narrative, including the initial story, the choices, and the memories.
    The service is also responsible for the generation of the game's choices, including the initial choices, the choices after a choice, and the choices after a memory.
    The service is also responsible for the generation of the game's memories, including the initial memories, the memories after a choice, and the memories after a memory.
    The service is also responsible for the generation of the game's progression, including the initial progression, the progression after a choice, and the progression after a memory.
    """
    
    def __init__(self):
        """Initialize the game service."""
        # The new modular approach doesn't need these dependencies
        # as the GameState model is self-contained
        pass
    
    def create_session(self, session_id: str, location: str = "Pallet Town", 
                      personality: Optional[Dict[str, int]] = None) -> GameState:
        """Create a new game session."""
        if personality is None:
            personality = {
                "friendship": 5, "courage": 5, "curiosity": 5,
                "wisdom": 5, "determination": 5
            }
        
        # Create player
        player = Player(
            id=str(uuid4()),
            name=f"Player_{session_id}",
            personality_traits=personality
        )
        
        # Create initial story
        current_story = Story(
            id=str(uuid4()),
            title="Welcome to Kanto",
            content="You wake up in your room in Pallet Town, ready to begin your Pokémon adventure!",
            location=location
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
            current_location=location,
            completed_events=[],
            relationships={},
            inventory=[]
        )
        
        game_state = GameState(
            player=player,
            current_story=current_story,
            available_choices=available_choices,
            memories=memories,
            progression=progression
        )
        
        logger.info(f"Created new game session: {session_id}")
        return game_state
    
    def get_session(self, session_id: str) -> Optional[GameState]:
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
    
    def load_session(self, session_id: str, save_name: str) -> Optional[GameState]:
        """Load a game session."""
        return None  # The new modular approach doesn't use session-based loads
    
    def _generate_current_narrative(self, session: GameState) -> Optional[Dict[str, Any]]:
        """Generate current narrative and choices."""
        return None  # The new modular approach doesn't use narrative generation
    
    def _generate_next_narrative(self, session: GameState) -> Optional[Dict[str, Any]]:
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
            if not game_state:
                raise ValueError("Game state is required")
                
            if not choice_id:
                raise ValueError("Choice ID is required")
                
            logger.info(f"Processing choice ID: {choice_id}")
            
            # Validate game state has required attributes
            if not hasattr(game_state, 'available_choices') or not game_state.available_choices:
                raise ValueError("No available choices in game state")
                
            # Log available choices for debugging
            choice_ids = [str(choice.id) for choice in game_state.available_choices]
            logger.info(f"Available choice IDs: {choice_ids}")
            
            # Find the chosen choice
            chosen_choice = None
            for choice in game_state.available_choices:
                if str(choice.id) == str(choice_id):
                    chosen_choice = choice
                    break
            
            if not chosen_choice:
                raise ValueError(f"Choice with ID '{choice_id}' not found in available choices. Available choices: {choice_ids}")
            
            logger.info(f"Found choice: {chosen_choice.text} (ID: {chosen_choice.id})")
            
            # Update personality traits based on choice effects
            updated_personality = game_state.player.personality_traits.copy()
            if hasattr(chosen_choice, 'effects') and chosen_choice.effects:
                for trait, effect in chosen_choice.effects.items():
                    if trait in updated_personality:
                        updated_personality[trait] = min(10, max(0, updated_personality[trait] + effect))
            
            # Create updated player
            updated_player = Player(
                id=game_state.player.id,
                name=game_state.player.name,
                personality_traits=updated_personality
            )
            
            logger.info(f"Updated player personality: {updated_personality}")
            
            # Generate new story based on choice
            new_story = Story(
                id=str(uuid4()),
                title="Story Continues",
                content=f"You chose: {chosen_choice.text}. The adventure continues...",
                location=game_state.progression.current_location
            )
            
            logger.info("Generated new story segment")
            
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
            
            logger.info(f"Generated {len(new_choices)} new choices")
            
            # Update progression
            updated_progression = GameProgression(
                current_location=game_state.progression.current_location,
                completed_events=game_state.progression.completed_events + [chosen_choice.text],
                relationships=game_state.progression.relationships,
                inventory=game_state.progression.inventory
            )
            
            logger.info("Updated game progression")
            
            # Create and return updated game state
            updated_game_state = GameState(
                player=updated_player,
                current_story=new_story,
                available_choices=new_choices,
                memories=game_state.memories,
                progression=updated_progression
            )
            
            logger.info(f"Successfully processed choice for player {game_state.player.name}")
            return updated_game_state
            
        except ValueError as ve:
            # Log validation errors with more context
            logger.error(f"Validation error in process_choice: {str(ve)}")
            raise ve
            
        except AttributeError as ae:
            # Log attribute errors which might indicate issues with the game state structure
            error_msg = f"Invalid game state structure: {str(ae)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from ae
            
        except Exception as e:
            # Log the full exception for debugging
            logger.error(f"Unexpected error in process_choice: {str(e)}", exc_info=True)
            raise Exception(f"Failed to process choice: {str(e)}") from e

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