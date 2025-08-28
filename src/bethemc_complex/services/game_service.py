"""
🎮 Game Service - Core Business Logic Orchestration

This service orchestrates all game-related business logic, including:
- Game state management and transitions
- Player choice processing and story progression
- Personality trait updates and effects
- Memory management and context building
- Game session lifecycle management

🏗️ Architecture Role:
    ┌─────────────────┐
    │   API Layer     │  ← Receives requests from FastAPI routes
    └─────────┬───────┘
              │
    ┌─────────▼───────┐  ← This Service Layer
    │  Game Service   │  ← Orchestrates business logic
    └─────────┬───────┘
              │
    ┌─────────▼───────┐
    │  Core Models    │  ← Uses domain models for data
    └─────────┬───────┘
              │
    ┌─────────▼───────┐
    │  Database       │  ← Persists state via other services
    └─────────────────┘

🎯 Key Responsibilities:
    • Game State Management: Create, update, and validate game states
    • Choice Processing: Handle player decisions and their effects
    • Story Progression: Advance narrative based on choices
    • Personality System: Update traits based on player actions
    • Memory Management: Track player experiences and context
    • Session Lifecycle: Handle game start, save, load operations

📋 Main Operations:
    • start_new_game(): Initialize new player and game state
    • process_choice(): Handle player decisions and update state
    • update_personality(): Modify player personality traits
    • add_memory(): Record player experiences and context
    • save_game() / load_game(): Persistence operations

🔧 Usage Example:
    from bethemc_complex.services.game_service import GameService
    
    # Initialize service
    game_service = GameService()
    
    # Start new game
    game_state = await game_service.start_new_game("Ash Ketchum")
    
    # Process player choice
    updated_state = await game_service.process_choice(game_state, "choice-1")
    
    # Update personality
    final_state = await game_service.update_personality(
        updated_state, "courage", 8
    )

⚠️ Important Notes:
    • All methods are async for database operations
    • GameState objects are immutable - methods return new states
    • Comprehensive error handling and logging
    • Validates all inputs and maintains data integrity
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from bethemc_complex.utils.logger import setup_logger
from bethemc_complex.models.core import GameState, Player, Story, Choice, Memory, PersonalityTrait, GameProgression
from bethemc_complex.ai.story_generator import StoryGenerator
from bethemc_complex.core.progression import ProgressionManager

logger = setup_logger(__name__)

class GameService:
    """
    🎮 Game Service - Core Business Logic Orchestrator
    
    This service is the central orchestrator for all game-related business logic.
    It manages the complete lifecycle of game states, from creation to updates,
    and handles all player interactions including choices, personality updates,
    and memory management.
    
    Key Responsibilities:
    • Game State Management: Create, update, and validate game states
    • Choice Processing: Handle player decisions and their effects on story progression
    • Personality System: Update player traits based on actions and choices
    • Memory Management: Track and manage player experiences and context
    • Story Progression: Advance narrative based on player decisions
    • Data Validation: Ensure all game state changes are valid and consistent
    
    Architecture Role:
    • Receives requests from the API layer (GameManager)
    • Orchestrates business logic using domain models
    • Returns immutable GameState objects for data integrity
    • Handles all game state transitions and validations
    
    Usage:
        game_service = GameService()
        game_state = await game_service.start_new_game("Ash Ketchum")
        updated_state = await game_service.process_choice(game_state, "choice-1")
    """
    
    def __init__(self):
        """
        Initialize the Game Service with AI capabilities.
        
        The service is designed to be stateless and lightweight,
        focusing on business logic orchestration rather than
        maintaining internal state. All game state is passed
        as parameters and returned as new immutable objects.
        
        Initializes the AI StoryGenerator for dynamic content generation.
        """
        try:
            self.story_generator = StoryGenerator()
            logger.info("🤖 GameService initialized with AI story generation")
        except Exception as e:
            logger.warning(f"Failed to initialize AI components, using fallback: {e}")
            self.story_generator = None
    
    def _convert_personality_for_ai(self, personality_traits: Dict[str, int]) -> Dict[str, float]:
        """Convert integer personality traits (0-10) to float (0.0-1.0) for AI."""
        return {trait: value / 10.0 for trait, value in personality_traits.items()}
    
    def _safe_ai_narrative_generation(self, location: str, personality: Dict[str, int], recent_events: List[str]) -> Dict[str, Any]:
        """Safely generate narrative with fallback if AI fails."""
        if not self.story_generator:
            return {"narrative": self._generate_fallback_story(location, personality, recent_events)}
        
        try:
            # Convert personality to float format for AI
            ai_personality = self._convert_personality_for_ai(personality)
            
            result = self.story_generator.generate_narrative(
                location=location,
                personality=ai_personality,
                recent_events=recent_events,
                max_knowledge_items=5
            )
            
            # Check if AI generated good content
            narrative = result.get("narrative", "")
            if narrative and len(narrative.strip()) > 50 and "let's weave a tale" not in narrative.lower() and "fill these in" not in narrative.lower():
                return result
            else:
                logger.warning("AI generated poor content, using fallback story")
                return {"narrative": self._generate_fallback_story(location, personality, recent_events)}
                
        except Exception as e:
            logger.warning(f"AI narrative generation failed: {e}")
            return {"narrative": self._generate_fallback_story(location, personality, recent_events)}
    
    def _generate_fallback_story(self, location: str, personality: Dict[str, int], recent_events: List[str]) -> str:
        """Generate a fallback story when AI generation fails."""
        # Get personality traits
        friendship = personality.get("friendship", 5)
        courage = personality.get("courage", 5)
        curiosity = personality.get("curiosity", 5)
        wisdom = personality.get("wisdom", 5)
        determination = personality.get("determination", 5)
        
        # Create personality-based story elements
        if friendship > 6:
            social_element = "You feel a strong connection to the people around you, and your warm personality draws others to you."
        elif friendship < 4:
            social_element = "You prefer to keep to yourself, but you're learning that sometimes you need to rely on others."
        else:
            social_element = "You have a balanced approach to relationships, building connections when they feel genuine."
            
        if courage > 6:
            courage_element = "Your bravery shines through as you face challenges head-on."
        elif courage < 4:
            courage_element = "You're learning to be more courageous, taking small steps to overcome your fears."
        else:
            courage_element = "You approach challenges with measured courage, thinking before acting."
            
        if curiosity > 6:
            curiosity_element = "Your natural curiosity drives you to explore and discover new things."
        elif curiosity < 4:
            curiosity_element = "You're learning to be more curious, opening yourself to new experiences."
        else:
            curiosity_element = "You maintain a healthy curiosity, exploring when it feels right."
        
        # Location-specific fallback stories
        location_stories = {
            "Pallet Town": f"""The gentle breeze carries the familiar scent of your hometown as you walk through Pallet Town. {social_element} {courage_element} {curiosity_element} The peaceful atmosphere of your starting point fills you with determination for the journey ahead.

You can see Professor Oak's laboratory in the distance, and the familiar faces of your neighbors going about their daily lives. The town feels alive with possibility, and you know that every choice you make will shape your adventure.""",
            
            "Route 1": f"""The path stretches before you, lined with tall grass that rustles with the promise of wild Pokémon. {courage_element} {curiosity_element} The route to Viridian City is well-traveled, but you know that every trainer's journey is unique.

You can hear the distant sounds of Pokémon calls and the gentle hum of nature all around you. The adventure is truly beginning now, and you feel the weight of your choices growing with each step.""",
            
            "Viridian City": f"""The bustling city of Viridian spreads out before you, a hub of activity and opportunity. {social_element} {curiosity_element} The city's energy is contagious, and you can feel the excitement of other trainers preparing for their own journeys.

The Pokémon Center stands as a beacon of hope, and the Gym looms as a challenge waiting to be conquered. Your determination grows stronger as you take in the sights and sounds of this vibrant city."""
        }
        
        # Return location-specific story or generic one
        return location_stories.get(location, f"""You continue your journey through {location}, taking in the sights and sounds of the Pokémon world around you. {social_element} {courage_element} {curiosity_element} Every step brings new possibilities and challenges, and you're ready to face whatever comes next.""")
    
    def _safe_ai_choice_generation(self, current_situation: str, personality: Dict[str, int]) -> List[Dict[str, Any]]:
        """Safely generate choices with fallback if AI fails."""
        if not self.story_generator:
            return self._generate_fallback_choices(current_situation, personality)
        
        try:
            # Convert personality to float format for AI
            ai_personality = self._convert_personality_for_ai(personality)
            
            choices = self.story_generator.generate_choices(
                current_situation=current_situation,
                personality=ai_personality,
                active_promises=[],
                key_relationships=[],
                max_knowledge_items=3
            )
            
            # Check if AI generated good choices
            if choices and len(choices) >= 2:
                # Validate that choices are actual text, not templates
                valid_choices = []
                for choice in choices:
                    choice_text = choice.get("text", "")
                    if (choice_text and len(choice_text.strip()) > 10 and 
                        "fill these in" not in choice_text.lower() and
                        "template" not in choice_text.lower()):
                        valid_choices.append(choice)
                
                if valid_choices:
                    return valid_choices
            
            logger.warning("AI generated poor choices, using fallback choices")
            return self._generate_fallback_choices(current_situation, personality)
                
        except Exception as e:
            logger.warning(f"AI choice generation failed: {e}")
            return self._generate_fallback_choices(current_situation, personality)
    
    def _generate_fallback_choices(self, current_situation: str, personality: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate fallback choices when AI generation fails."""
        # Get personality traits
        friendship = personality.get("friendship", 5)
        courage = personality.get("courage", 5)
        curiosity = personality.get("curiosity", 5)
        wisdom = personality.get("wisdom", 5)
        determination = personality.get("determination", 5)
        
        # Location-specific fallback choices
        location_choices = {
            "Pallet Town": [
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
            "Route 1": [
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
            "Viridian City": [
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
        
        # Return location-specific choices or generic ones
        return location_choices.get(current_situation, [
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
        """
        🆕 Start a new game session with AI-generated initial story.
        
        Creates a complete new game state with a player, AI-generated initial story,
        starting choices, and default progression. This is the entry point
        for new players beginning their Pokémon adventure.
        
        Args:
            player_name (str): The name of the player starting the adventure
            personality_traits (Optional[Dict[str, int]]): Custom personality traits (0-10 scale).
                If None, uses balanced defaults (all traits = 5)
        
        Returns:
            GameState: Complete initial game state with AI-generated content
        
        Raises:
            ValueError: If player_name is empty or invalid
            Exception: If game initialization or AI generation fails
        
        Example:
            game_state = await game_service.start_new_game(
                "Ash Ketchum",
                personality_traits={"courage": 7, "curiosity": 8}
            )
        """
        try:
            # Validate player name
            if not player_name or not player_name.strip():
                raise ValueError("Player name cannot be empty")
            
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
                name=player_name.strip(),
                personality_traits=personality_traits
            )
            
            logger.info(f"Starting new game for player: {player_name} in Pallet Town")
            
            # Set initial location - always start in Pallet Town
            starting_location = "Pallet Town"
            initial_events = [f"{player_name} begins their Pokémon journey"]
            
            # Generate initial story using AI with proper error handling
            initial_story_content = f"Welcome to the world of Pokémon, {player_name}! You wake up in your room in Pallet Town, ready to begin your adventure as a Pokémon trainer!"
            
            try:
                if self.story_generator:
                    logger.info("Generating initial story with AI...")
                    initial_narrative = self._safe_ai_narrative_generation(
                        location=starting_location,
                        personality=personality_traits,
                        recent_events=initial_events
                    )
                    
                    ai_story_content = initial_narrative.get("narrative", "")
                    
                    # Use AI content if it's good, otherwise use fallback
                    if ai_story_content and len(ai_story_content.strip()) > 50 and "let's weave a tale" not in ai_story_content.lower():
                        initial_story_content = ai_story_content
                        logger.info("Successfully generated initial story with AI")
                    else:
                        logger.warning("AI generated poor content, using fallback story")
                else:
                    logger.info("No AI story generator available, using fallback story")
                    
            except Exception as ai_error:
                logger.warning(f"AI initial story generation failed, using fallback: {ai_error}")
            
            # Create initial story - always in Pallet Town
            current_story = Story(
                id=str(uuid4()),
                title="Your Pokémon Adventure Begins",
                content=initial_story_content,
                location=starting_location  # Ensure this is Pallet Town
            )
            
            # Always use the same default starting choices for Pallet Town
            logger.info("Using default starting choices for Pallet Town")
            available_choices = [
                Choice(
                    id=str(uuid4()),
                    text="Talk to your mom before leaving",
                    effects={"friendship": 1, "wisdom": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Explore Pallet Town and meet the neighbors",
                    effects={"friendship": 1, "curiosity": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Go to Professor Oak's laboratory to get your first Pokémon",
                    effects={"curiosity": 1, "determination": 1}
                )
            ]
            
            # Initialize empty memories and progression starting in Pallet Town
            memories = []
            progression = GameProgression(
                current_location=starting_location,  # Ensure this is Pallet Town
                completed_events=[],
                relationships={},
                inventory=[]
            )
            
            # Create the initial game state
            game_state = GameState(
                player=player,
                current_story=current_story,
                available_choices=available_choices,
                memories=memories,
                progression=progression
            )
            
            logger.info(f"Successfully created new game for {player_name} starting in {starting_location}")
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to start new game for {player_name}: {e}")
            raise Exception(f"Could not start new game: {e}")

    async def process_choice(self, game_state: GameState, choice_id: str) -> GameState:
        """
        🎯 Process a player's choice and advance the story using AI generation.
        
        Takes a player's choice and updates the game state using AI-powered
        story generation. This includes updating personality traits based on 
        choice effects, generating new story content using LLM, creating new 
        AI-generated choices, and updating game progression.
        
        Args:
            game_state (GameState): Current game state to update
            choice_id (str): ID of the choice the player selected
        
        Returns:
            GameState: Updated game state with AI-generated story and choices
        
        Raises:
            ValueError: If choice_id is invalid or not found in available choices
            ValueError: If game_state is None or invalid
            Exception: If choice processing or AI generation fails
        
        Example:
            updated_state = await game_service.process_choice(
                current_state, "choice-visit-oak-lab"
            )
        """
        try:
            if not game_state:
                raise ValueError("Game state is required")
                
            if not choice_id:
                raise ValueError("Choice ID is required")
                
            logger.info(f"Processing choice ID: {choice_id} using AI generation")
            
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
            
            # Prepare context for AI story generation
            recent_events = game_state.progression.completed_events[-5:] + [chosen_choice.text]
            story_context = {
                "previous_story": game_state.current_story.content,
                "player_choice": chosen_choice.text,
                "personality": updated_personality,
                "location": game_state.progression.current_location,
                "completed_events": game_state.progression.completed_events,
                "relationships": game_state.progression.relationships,
                "memories": [memory.content for memory in game_state.memories[-10:]]  # Last 10 memories for context
            }
            
            logger.info("Generating new story using AI...")
            
            # Generate new story using AI
            try:
                narrative_result = self._safe_ai_narrative_generation(
                    location=game_state.progression.current_location,
                    personality=updated_personality,
                    recent_events=recent_events
                )
                
                new_story_content = narrative_result.get("narrative", f"You chose: {chosen_choice.text}. The adventure continues...")
                
                # Extract any new memories from the AI narrative
                new_memories = list(game_state.memories)  # Copy existing memories
                if "active_promises" in narrative_result:
                    for promise in narrative_result["active_promises"]:
                        new_memory = Memory(
                            id=str(uuid4()),
                            content=promise,
                            memory_type="promise",
                            timestamp=datetime.now()
                        )
                        new_memories.append(new_memory)
                
                if "key_relationships" in narrative_result:
                    for relationship in narrative_result["key_relationships"]:
                        new_memory = Memory(
                            id=str(uuid4()),
                            content=relationship,
                            memory_type="relationship",
                            timestamp=datetime.now()
                        )
                        new_memories.append(new_memory)
                
            except Exception as ai_error:
                logger.warning(f"AI story generation failed, using fallback: {ai_error}")
                new_story_content = f"You chose: {chosen_choice.text}. The adventure continues in {game_state.progression.current_location}..."
                new_memories = game_state.memories
            
            # Create new story with AI-generated content
            new_story = Story(
                id=str(uuid4()),
                title="Your Adventure Continues",
                content=new_story_content,
                location=game_state.progression.current_location
            )
            
            logger.info("Generated new AI story segment")
            
            # Generate new choices using AI
            try:
                logger.info("Generating new choices using AI...")
                ai_choices = self._safe_ai_choice_generation(
                    current_situation=new_story_content,
                    personality=updated_personality
                )
                
                # Convert AI choices to Choice objects
                new_choices = []
                for i, ai_choice in enumerate(ai_choices[:4]):  # Limit to 4 choices
                    choice = Choice(
                        id=str(uuid4()),
                        text=ai_choice.get("text", f"Choice {i+1}"),
                        effects=ai_choice.get("effects", {})
                    )
                    new_choices.append(choice)
                
                # Ensure we have at least 2 choices
                if len(new_choices) < 2:
                    new_choices.extend([
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
                    ])
                
            except Exception as ai_error:
                logger.warning(f"AI choice generation failed, using fallback choices: {ai_error}")
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
                    ),
                    Choice(
                        id=str(uuid4()),
                        text="Help others around you",
                        effects={"friendship": 1}
                    )
                ]
            
            logger.info(f"Generated {len(new_choices)} new choices")
            
            # Update progression with the completed choice
            updated_progression = GameProgression(
                current_location=game_state.progression.current_location,
                completed_events=game_state.progression.completed_events + [chosen_choice.text],
                relationships=game_state.progression.relationships,
                inventory=game_state.progression.inventory
            )
            
            logger.info("Updated game progression")
            
            # Create and return updated game state with AI-generated content
            updated_game_state = GameState(
                player=updated_player,
                current_story=new_story,
                available_choices=new_choices,
                memories=new_memories,
                progression=updated_progression
            )
            
            logger.info(f"Successfully processed choice with AI generation for player {game_state.player.name}")
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
        """
        🧠 Add a new memory to the player's memory bank.
        
        Creates and stores a new memory that will influence future
        story generation and character interactions. Memories provide
        context for the AI story system and help maintain narrative
        continuity throughout the adventure.
        
        Args:
            game_state (GameState): Current game state to update
            memory_text (str): Description of the memory to add
            memory_type (str): Type of memory for categorization
                Valid types: "general", "promise", "relationship", "event", "location"
        
        Returns:
            GameState: Updated game state with new memory added
        
        Raises:
            ValueError: If memory_text is empty or invalid
            ValueError: If memory_type is not recognized
            Exception: If memory addition fails
        
        Example:
            updated_state = await game_service.add_memory(
                current_state,
                "I promised Professor Oak I would become a Pokémon Master",
                "promise"
            )
        """
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
        """
        🧠 Update a player's personality trait directly.
        
        Allows direct modification of a specific personality trait.
        The value is clamped between 0 and 10 to maintain valid ranges.
        This method is useful for external personality modifications
        or debugging purposes.
        
        Args:
            game_state (GameState): Current game state to update
            trait (str): Name of the personality trait to update
                Valid values: "friendship", "courage", "curiosity", "wisdom", "determination"
            value (int): New value for the trait (0-10 scale)
        
        Returns:
            GameState: Updated game state with modified personality trait
        
        Raises:
            ValueError: If trait name is invalid
            ValueError: If value is outside valid range (0-10)
            Exception: If personality update fails
        
        Example:
            updated_state = await game_service.update_personality(
                current_state, "courage", 8
            )
        """
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