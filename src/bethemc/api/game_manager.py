"""
Simple Game Manager - Everything in one place!

This file contains ALL the game logic in one simple class.
No complex dependencies, adapters, or interfaces - just pure game logic!
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException

from ..models.models import (
    GameResponse, ChoiceResponse, 
    GameState, Player, Story, Choice, Memory, GameProgression
)
from ..database.service import SimpleDatabaseService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SimpleGameManager:
    """
    Simple Game Manager - Does EVERYTHING for the game!
    
    What this class does:
    1. Starts new games
    2. Processes player choices  
    3. Saves/loads games
    4. Manages player data
    5. Handles all database operations
    
    No complex layers - just simple, clear methods!
    """
    
    def __init__(self):
        """Initialize the simple game manager."""
        self.db = SimpleDatabaseService()
        logger.info("Simple Game Manager initialized!")
    
    async def start_new_game(self, player_name: str) -> GameResponse:
        """
        Start a brand new game for a player.
        
        Steps:
        1. Create a new player with default personality
        2. Create the opening story in Pallet Town  
        3. Create initial choices for the player
        4. Save everything to database
        5. Return the game state to the user
        """
        try:
            logger.info(f"Starting new game for player: {player_name}")
            
            # Step 1: Create a new player
            player = Player(
                id=str(uuid4()),  # Generate unique ID
                name=player_name,
                personality_traits={
                    "friendship": 5,
                    "courage": 5,
                    "curiosity": 5,
                    "wisdom": 5,
                    "determination": 5
                }
            )
            
            # Step 2: Create the opening story
            opening_story = Story(
                id=str(uuid4()),
                title="Welcome to Pallet Town!",
                content=f"Welcome {player_name}! You wake up in your cozy bedroom in Pallet Town. "
                       f"The sun is shining through your window, and you can hear Pidgey chirping outside. "
                       f"Today feels special - like the beginning of a great adventure! "
                       f"Professor Oak has been expecting you. What would you like to do?",
                location="Pallet Town"
            )
            
            # Step 3: Create initial choices
            initial_choices = [
                Choice(
                    id=str(uuid4()),
                    text="Go straight to Professor Oak's laboratory",
                    effects={"curiosity": 1}  # This choice increases curiosity
                ),
                Choice(
                    id=str(uuid4()),
                    text="Explore Pallet Town first to get familiar",
                    effects={"wisdom": 1}  # This choice increases wisdom
                ),
                Choice(
                    id=str(uuid4()),
                    text="Talk to your mom before leaving",
                    effects={"friendship": 1}  # This choice increases friendship
                )
            ]
            
            # Step 4: Create game progression (tracks where you've been)
            progression = GameProgression(
                current_location="Pallet Town",
                completed_events=[],  # Nothing completed yet
                relationships={},     # No relationships yet
                inventory=[]         # No items yet
            )
            
            # Step 5: Put it all together in a GameState
            game_state = GameState(
                player=player,
                current_story=opening_story,
                available_choices=initial_choices,
                memories=[],  # No memories yet
                progression=progression
            )
            
            # Step 6: Save to database
            await self.db.save_game_state(game_state)
            logger.info(f"Game saved for player: {player_name} (ID: {player.id})")
            
            # Step 7: Return formatted response
            return GameResponse(
                player_id=player.id,
                player_name=player.name,
                current_story=opening_story.__dict__,
                available_choices=[choice.__dict__ for choice in initial_choices],
                personality_traits=player.personality_traits,
                memories=[],
                game_progress=progression.__dict__
            )
            
        except Exception as e:
            logger.error(f"Failed to start game for {player_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Could not start game: {str(e)}")
    
    async def make_choice(self, player_id: str, choice_id: str) -> ChoiceResponse:
        """
        Process a player's choice and advance the story.
        
        Steps:
        1. Get the current game state from database
        2. Find the choice the player made
        3. Update personality based on choice effects
        4. Generate new story content
        5. Create new choices for the player
        6. Save updated game state
        7. Return the new story and choices
        """
        try:
            logger.info(f"Processing choice {choice_id} for player {player_id}")
            
            # Step 1: Get current game state
            game_state = await self.db.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail=f"No game found for player {player_id}")
            
            # Step 2: Find the choice the player made
            chosen_choice = None
            for choice in game_state.available_choices:
                if choice.id == choice_id:
                    chosen_choice = choice
                    break
            
            if not chosen_choice:
                available_ids = [choice.id for choice in game_state.available_choices]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid choice {choice_id}. Available: {available_ids}"
                )
            
            # Step 3: Update personality traits based on choice
            new_personality = game_state.player.personality_traits.copy()
            if chosen_choice.effects:
                for trait, change in chosen_choice.effects.items():
                    if trait in new_personality:
                        # Keep traits between 0 and 10
                        new_value = new_personality[trait] + change
                        new_personality[trait] = max(0, min(10, new_value))
            
            # Step 4: Generate new story based on the choice
            new_story = self._generate_story_from_choice(chosen_choice, game_state)
            
            # Step 5: Create new choices based on the story
            new_choices = self._generate_new_choices(new_story, game_state)
            
            # Step 6: Update game progression
            new_progression = GameProgression(
                current_location=game_state.progression.current_location,
                completed_events=game_state.progression.completed_events + [chosen_choice.text],
                relationships=game_state.progression.relationships,
                inventory=game_state.progression.inventory
            )
            
            # Step 7: Create updated player
            updated_player = Player(
                id=game_state.player.id,
                name=game_state.player.name,
                personality_traits=new_personality
            )
            
            # Step 8: Create updated game state
            updated_game_state = GameState(
                player=updated_player,
                current_story=new_story,
                available_choices=new_choices,
                memories=game_state.memories,
                progression=new_progression
            )
            
            # Step 9: Save to database
            await self.db.save_game_state(updated_game_state)
            
            # Step 10: Return response
            return ChoiceResponse(
                player_id=player_id,
                current_story=new_story.__dict__,
                available_choices=[choice.__dict__ for choice in new_choices],
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=new_progression.__dict__
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to process choice: {e}")
            raise HTTPException(status_code=500, detail=f"Could not process choice: {str(e)}")
    
    def _generate_story_from_choice(self, chosen_choice: Choice, game_state: GameState) -> Story:
        """
        Generate a new story segment based on the player's choice.
        
        This is a simple story generator - in a real game you'd have
        much more sophisticated story generation!
        """
        choice_text = chosen_choice.text.lower()
        location = game_state.progression.current_location
        player_name = game_state.player.name
        
        # Simple story generation based on keywords in the choice
        if "oak" in choice_text or "laboratory" in choice_text:
            title = "Professor Oak's Laboratory"
            content = (f"You walk into Professor Oak's laboratory, {player_name}. "
                      f"The lab is filled with books, computers, and... Pokéballs! "
                      f"Professor Oak turns to you with a warm smile. "
                      f"'Ah, {player_name}! Perfect timing. I have something special for you.' "
                      f"He gestures toward three Pokéballs on his desk.")
            new_location = "Oak's Laboratory"
            
        elif "explore" in choice_text or "town" in choice_text:
            title = "Exploring Pallet Town"
            content = (f"You decide to explore Pallet Town first, {player_name}. "
                      f"You walk through the peaceful streets, seeing other houses and "
                      f"trainers with their Pokémon. The town is small but charming. "
                      f"You notice some wild Pokémon in the tall grass at the edge of town. "
                      f"After your walk, you feel more prepared for your adventure.")
            new_location = "Pallet Town - Town Square"
            
        elif "mom" in choice_text or "talk" in choice_text:
            title = "A Chat with Mom"
            content = (f"You find your mom in the kitchen, {player_name}. "
                      f"She smiles warmly when she sees you. "
                      f"'Oh honey, are you ready for your Pokémon adventure?' "
                      f"She gives you a big hug and hands you a bag. "
                      f"'I packed some supplies for you. Be safe out there!' "
                      f"You feel loved and prepared for the journey ahead.")
            new_location = "Your House"
            
        else:
            # Default story for any other choice
            title = "The Adventure Continues"
            content = (f"You chose: {chosen_choice.text}. "
                      f"The adventure continues, {player_name}! "
                      f"Each choice you make shapes your journey through the Pokémon world.")
            new_location = location
        
        return Story(
            id=str(uuid4()),
            title=title,
            content=content,
            location=new_location
        )
    
    def _generate_new_choices(self, current_story: Story, game_state: GameState) -> List[Choice]:
        """
        Generate new choices based on the current story and game state.
        
        This creates appropriate choices for each story situation.
        """
        story_title = current_story.title.lower()
        
        if "laboratory" in story_title:
            # Player is at Oak's lab - offer starter Pokémon choices
            return [
                Choice(
                    id=str(uuid4()),
                    text="Choose Bulbasaur (Grass-type)",
                    effects={"wisdom": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Choose Charmander (Fire-type)",
                    effects={"courage": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Choose Squirtle (Water-type)",
                    effects={"friendship": 1}
                )
            ]
            
        elif "exploring" in story_title or "town square" in story_title:
            # Player explored town - offer next steps
            return [
                Choice(
                    id=str(uuid4()),
                    text="Now go to Professor Oak's laboratory",
                    effects={"determination": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Investigate the wild Pokémon in the grass",
                    effects={"curiosity": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Visit other trainers in town",
                    effects={"friendship": 1}
                )
            ]
            
        elif "mom" in story_title or "chat" in story_title:
            # Player talked to mom - offer next steps
            return [
                Choice(
                    id=str(uuid4()),
                    text="Head to Professor Oak's laboratory",
                    effects={"determination": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Check what's in the bag mom gave you",
                    effects={"curiosity": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Say one more goodbye to mom",
                    effects={"friendship": 1}
                )
            ]
            
        else:
            # Default choices for any other situation
            return [
                Choice(
                    id=str(uuid4()),
                    text="Continue your adventure",
                    effects={"determination": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Look around carefully",
                    effects={"wisdom": 1}
                ),
                Choice(
                    id=str(uuid4()),
                    text="Be brave and move forward",
                    effects={"courage": 1}
                )
            ]
    
    async def save_game(self, player_id: str, save_name: str) -> Dict[str, Any]:
        """
        Save the current game to a save file.
        
        Simple: Just get the current game state and save it with a name.
        """
        try:
            game_state = await self.db.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="No game found to save")
            
            save_id = await self.db.save_game(game_state, save_name)
            
            return {
                "message": "Game saved successfully!",
                "save_id": save_id,
                "save_name": save_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            raise HTTPException(status_code=500, detail=f"Could not save game: {str(e)}")
    
    async def load_game(self, player_id: str, save_id: str) -> GameResponse:
        """
        Load a saved game.
        
        Simple: Get the saved game state and make it the current game.
        """
        try:
            game_state = await self.db.load_game(player_id, save_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="Save file not found")
            
            # Make this the current game
            await self.db.save_game_state(game_state)
            
            return GameResponse(
                player_id=game_state.player.id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
            
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            raise HTTPException(status_code=500, detail=f"Could not load game: {str(e)}")
    
    async def get_current_game(self, player_id: str) -> GameResponse:
        """
        Get the current game state for a player.
        
        Simple: Just get whatever game state is in the database.
        """
        try:
            game_state = await self.db.get_game_state(player_id)
            if not game_state:
                raise HTTPException(status_code=404, detail="No game found for this player")
            
            return GameResponse(
                player_id=game_state.player.id,
                player_name=game_state.player.name,
                current_story=game_state.current_story.__dict__,
                available_choices=[choice.__dict__ for choice in game_state.available_choices],
                personality_traits=game_state.player.personality_traits,
                memories=[memory.__dict__ for memory in game_state.memories],
                game_progress=game_state.progression.__dict__
            )
            
        except Exception as e:
            logger.error(f"Failed to get current game: {e}")
            raise HTTPException(status_code=500, detail=f"Could not get game: {str(e)}")


# Simple dependency function - just creates one instance
def get_simple_game_manager() -> SimpleGameManager:
    """Get the simple game manager instance."""
    return SimpleGameManager() 