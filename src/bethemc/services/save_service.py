"""
Save/load service for game persistence.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid

from ..core.interfaces import SaveManager
from ..models.core import GameState, Player, Story, Choice, Memory, PersonalityTrait, GameProgression
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SaveService(SaveManager):
    """Service for managing game saves."""
    
    def __init__(self, save_dir: str = "data/saves"):
        """Initialize the save service."""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_game(self, game_state: GameState, save_name: str) -> Dict[str, Any]:
        """Save game state to file."""
        try:
            save_id = str(uuid.uuid4())
            save_file = self.save_dir / f"{save_id}.json"
            
            # Convert game state to dict
            save_data = {
                "save_id": save_id,
                "save_name": save_name,
                "timestamp": datetime.now().isoformat(),
                "player": game_state.player.__dict__,
                "current_story": game_state.current_story.__dict__,
                "available_choices": [c.__dict__ for c in game_state.available_choices],
                "memories": [m.__dict__ for m in game_state.memories],
                "progression": game_state.progression.__dict__
            }
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            logger.info(f"Saved game for player {game_state.player.name} as {save_name}")
            return {
                "save_id": save_id,
                "save_name": save_name,
                "timestamp": save_data["timestamp"]
            }
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            raise
    
    async def load_game(self, player_id: str, save_id: str) -> GameState:
        """Load game state from file."""
        try:
            save_file = self.save_dir / f"{save_id}.json"
            
            if not save_file.exists():
                raise FileNotFoundError(f"Save file not found: {save_id}")
            
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Reconstruct game state
            player = Player(**save_data["player"])
            current_story = Story(**save_data["current_story"])
            available_choices = [Choice(**c) for c in save_data["available_choices"]]
            memories = [Memory(**m) for m in save_data["memories"]]
            progression = GameProgression(**save_data["progression"])
            
            game_state = GameState(
                player=player,
                current_story=current_story,
                available_choices=available_choices,
                memories=memories,
                progression=progression
            )
            
            logger.info(f"Loaded game for player {player.name} from {save_data['save_name']}")
            return game_state
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            raise
    
    async def get_player_saves(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all saves for a player."""
        try:
            saves = []
            for save_file in self.save_dir.glob("*.json"):
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                if save_data["player"]["id"] == player_id:
                    saves.append({
                        "save_id": save_data["save_id"],
                        "save_name": save_data["save_name"],
                        "timestamp": save_data["timestamp"],
                        "player_name": save_data["player"]["name"]
                    })
            
            return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"Failed to get saves for player {player_id}: {e}")
            raise
    
    def delete_save(self, save_id: str) -> bool:
        """Delete a save file."""
        try:
            save_file = self.save_dir / f"{save_id}.json"
            if save_file.exists():
                save_file.unlink()
                logger.info(f"Deleted save file: {save_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete save {save_id}: {e}")
            return False 