"""
Save/load service for game persistence with summarization support.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid
import gzip

from ..core.interfaces import SaveManager
from ..models.core import GameState, Player, Story, Choice, Memory, PersonalityTrait, GameProgression
from ..utils.logger import get_logger
from .summarization_service import SummarizationService

logger = get_logger(__name__)

class SaveService(SaveManager):
    """Service for managing game saves with automatic summarization."""
    
    def __init__(self, save_dir: str = "data/saves", max_saves_per_player: int = 10, 
                 compression_threshold_kb: int = 50):
        """Initialize the save service."""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.max_saves_per_player = max_saves_per_player
        self.compression_threshold_kb = compression_threshold_kb
        self.summarization_service = SummarizationService()
    
    async def save_game(self, game_state: GameState, save_name: str) -> Dict[str, Any]:
        """Save game state to file with automatic optimization."""
        try:
            save_id = str(uuid.uuid4())
            
            # Check if we should use summarization
            size_estimate = self.summarization_service.get_save_size_estimate(game_state)
            
            if size_estimate["should_summarize"]:
                # Use summarized save for large game states
                save_data = self._create_summarized_save(game_state, save_name, save_id)
                save_file = self.save_dir / f"{save_id}.summary.json"
                is_summarized = True
            else:
                # Use full save for smaller game states
                save_data = self._create_full_save(game_state, save_name, save_id)
                save_file = self.save_dir / f"{save_id}.json"
                is_summarized = False
            
            # Check if compression is needed
            data_size = len(json.dumps(save_data))
            if data_size > self.compression_threshold_kb * 1024:
                # Use gzip compression
                save_file = save_file.with_suffix('.json.gz')
                with gzip.open(save_file, 'wt', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, default=str)
                is_compressed = True
            else:
                # Save as regular JSON
                with open(save_file, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, default=str)
                is_compressed = False
            
            # Clean up old saves for this player
            await self._cleanup_old_saves(game_state.player.id)
            
            logger.info(f"Saved game for player {game_state.player.name} as {save_name} "
                       f"(summarized: {is_summarized}, compressed: {is_compressed})")
            
            return {
                "save_id": save_id,
                "save_name": save_name,
                "timestamp": save_data["timestamp"],
                "is_summarized": is_summarized,
                "is_compressed": is_compressed,
                "size_estimate": size_estimate
            }
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            raise
    
    def _create_full_save(self, game_state: GameState, save_name: str, save_id: str) -> Dict[str, Any]:
        """Create a full save with complete game state."""
        return {
            "save_id": save_id,
            "save_name": save_name,
            "timestamp": datetime.now().isoformat(),
            "save_type": "full",
            "player": game_state.player.__dict__,
            "current_story": game_state.current_story.__dict__,
            "available_choices": [c.__dict__ for c in game_state.available_choices],
            "memories": [m.__dict__ for m in game_state.memories],
            "progression": game_state.progression.__dict__
        }
    
    def _create_summarized_save(self, game_state: GameState, save_name: str, save_id: str) -> Dict[str, Any]:
        """Create a summarized save for large game states."""
        summarized_state = self.summarization_service.summarize_game_state(game_state)
        
        return {
            "save_id": save_id,
            "save_name": save_name,
            "timestamp": datetime.now().isoformat(),
            "save_type": "summarized",
            "summarized_state": summarized_state,
            "original_memory_count": len(game_state.memories),
            "original_completed_events": len(game_state.progression.completed_events)
        }
    
    async def load_game(self, player_id: str, save_id: str) -> GameState:
        """Load game state from file with support for summarized saves."""
        try:
            # Try different file extensions
            possible_files = [
                self.save_dir / f"{save_id}.json.gz",
                self.save_dir / f"{save_id}.summary.json.gz",
                self.save_dir / f"{save_id}.summary.json",
                self.save_dir / f"{save_id}.json"
            ]
            
            save_file = None
            for file_path in possible_files:
                if file_path.exists():
                    save_file = file_path
                    break
            
            if not save_file:
                raise FileNotFoundError(f"Save file not found: {save_id}")
            
            # Load the save data
            if save_file.suffix == '.gz':
                with gzip.open(save_file, 'rt', encoding='utf-8') as f:
                    save_data = json.load(f)
            else:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
            
            # Reconstruct game state based on save type
            if save_data.get("save_type") == "summarized":
                game_state = self.summarization_service.expand_summarized_state(
                    save_data["summarized_state"]
                )
                logger.info(f"Loaded summarized save for player {game_state.player.name}")
            else:
                # Full save reconstruction
                game_state = self._reconstruct_full_save(save_data)
                logger.info(f"Loaded full save for player {game_state.player.name}")
            
            return game_state
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            raise
    
    def _reconstruct_full_save(self, save_data: Dict[str, Any]) -> GameState:
        """Reconstruct game state from full save data."""
        player = Player(**save_data["player"])
        current_story = Story(**save_data["current_story"])
        available_choices = [Choice(**c) for c in save_data["available_choices"]]
        memories = [Memory(**m) for m in save_data["memories"]]
        progression = GameProgression(**save_data["progression"])
        
        return GameState(
            player=player,
            current_story=current_story,
            available_choices=available_choices,
            memories=memories,
            progression=progression
        )
    
    async def get_player_saves(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all saves for a player with optimization info."""
        try:
            saves = []
            for save_file in self.save_dir.glob("*"):
                if not save_file.is_file():
                    continue
                
                try:
                    # Load save metadata
                    if save_file.suffix == '.gz':
                        with gzip.open(save_file, 'rt', encoding='utf-8') as f:
                            save_data = json.load(f)
                    else:
                        with open(save_file, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                    
                    if save_data.get("player", {}).get("id") == player_id:
                        save_info = {
                            "save_id": save_data["save_id"],
                            "save_name": save_data["save_name"],
                            "timestamp": save_data["timestamp"],
                            "player_name": save_data.get("player", {}).get("name", "Unknown"),
                            "save_type": save_data.get("save_type", "full"),
                            "is_compressed": save_file.suffix == '.gz',
                            "file_size_kb": save_file.stat().st_size / 1024
                        }
                        
                        # Add optimization info for summarized saves
                        if save_data.get("save_type") == "summarized":
                            save_info.update({
                                "original_memory_count": save_data.get("original_memory_count", 0),
                                "current_memory_count": len(save_data.get("summarized_state", {}).get("key_memories", [])),
                                "compression_ratio": save_data.get("original_memory_count", 0) / max(1, len(save_data.get("summarized_state", {}).get("key_memories", [])))
                            })
                        
                        saves.append(save_info)
                except Exception as e:
                    logger.warning(f"Failed to read save file {save_file}: {e}")
                    continue
            
            return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"Failed to get saves for player {player_id}: {e}")
            raise
    
    async def _cleanup_old_saves(self, player_id: str) -> None:
        """Clean up old saves for a player, keeping only the most recent ones."""
        try:
            saves = await self.get_player_saves(player_id)
            if len(saves) > self.max_saves_per_player:
                saves_to_delete = saves[self.max_saves_per_player:]
                for save in saves_to_delete:
                    self.delete_save(save["save_id"])
                logger.info(f"Cleaned up {len(saves_to_delete)} old saves for player {player_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup old saves for player {player_id}: {e}")
    
    def delete_save(self, save_id: str) -> bool:
        """Delete a save file."""
        try:
            # Try different file extensions
            possible_files = [
                self.save_dir / f"{save_id}.json.gz",
                self.save_dir / f"{save_id}.summary.json.gz",
                self.save_dir / f"{save_id}.summary.json",
                self.save_dir / f"{save_id}.json"
            ]
            
            for file_path in possible_files:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted save file: {save_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete save {save_id}: {e}")
            return False
    
    def get_save_stats(self) -> Dict[str, Any]:
        """Get statistics about all saves."""
        try:
            saves = list(self.save_dir.glob("*"))
            file_sizes = [f.stat().st_size for f in saves if f.is_file()]
            
            total_size_mb = sum(file_sizes) / (1024 * 1024) if file_sizes else 0
            average_size_kb = sum(file_sizes) / len(file_sizes) / 1024 if file_sizes else 0
            largest_save_kb = max(file_sizes) / 1024 if file_sizes else 0
            
            # Count by type
            full_saves = len([f for f in saves if f.is_file() and f.suffix == '.json' and not f.stem.endswith('.summary')])
            summarized_saves = len([f for f in saves if f.is_file() and 'summary' in f.name])
            compressed_saves = len([f for f in saves if f.is_file() and f.suffix == '.gz'])
            
            return {
                "total_saves": len(saves),
                "total_size_mb": total_size_mb,
                "average_size_kb": average_size_kb,
                "largest_save_kb": largest_save_kb,
                "save_types": {
                    "full": full_saves,
                    "summarized": summarized_saves,
                    "compressed": compressed_saves
                }
            }
        except Exception as e:
            logger.error(f"Failed to get save stats: {e}")
            raise 