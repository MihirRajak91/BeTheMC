"""
Story scene management for the narrative-driven Pokémon adventure.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

class SceneType(Enum):
    DIALOGUE = "dialogue"
    EXPLORATION = "exploration"
    BATTLE = "battle"
    PUZZLE = "puzzle"

@dataclass
class Choice:
    text: str
    next_scene: str
    effects: Dict[str, float]  # Effects on story variables
    requirements: Optional[Dict[str, float]] = None  # Requirements to show this choice

@dataclass
class Scene:
    id: str
    type: SceneType
    description: str
    choices: List[Choice]
    background: Optional[str] = None
    music: Optional[str] = None
    npc: Optional[str] = None
    requirements: Optional[Dict[str, float]] = None

class StoryManager:
    def __init__(self, story_data_path: str = "data/raw/story"):
        """Initialize the story manager."""
        self.story_data_path = Path(story_data_path)
        self.current_scene: Optional[Scene] = None
        self.scene_history: List[str] = []
        self.story_state: Dict[str, float] = {}
        self.scenes: Dict[str, Scene] = {}
        
        # Load story data
        self._load_story_data()

    def _load_story_data(self):
        """Load story scenes from JSON files."""
        for scene_file in self.story_data_path.glob("*.json"):
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
                scene = self._create_scene_from_data(scene_data)
                self.scenes[scene.id] = scene

    def _create_scene_from_data(self, data: Dict) -> Scene:
        """Create a Scene object from JSON data."""
        choices = [
            Choice(
                text=choice["text"],
                next_scene=choice["next_scene"],
                effects=choice.get("effects", {}),
                requirements=choice.get("requirements")
            )
            for choice in data["choices"]
        ]
        
        return Scene(
            id=data["id"],
            type=SceneType(data["type"]),
            description=data["description"],
            choices=choices,
            background=data.get("background"),
            music=data.get("music"),
            npc=data.get("npc"),
            requirements=data.get("requirements")
        )

    def start_story(self, starting_scene_id: str):
        """Start the story from a specific scene."""
        if starting_scene_id not in self.scenes:
            raise ValueError(f"Starting scene {starting_scene_id} not found")
        
        self.current_scene = self.scenes[starting_scene_id]
        self.scene_history = [starting_scene_id]
        self.story_state = {}

    def get_available_choices(self) -> List[Choice]:
        """Get available choices for the current scene based on requirements."""
        if not self.current_scene:
            return []
        
        available_choices = []
        for choice in self.current_scene.choices:
            if self._check_requirements(choice.requirements):
                available_choices.append(choice)
        
        return available_choices

    def _check_requirements(self, requirements: Optional[Dict[str, float]]) -> bool:
        """Check if requirements are met for a choice or scene."""
        if not requirements:
            return True
        
        for key, value in requirements.items():
            if self.story_state.get(key, 0) < value:
                return False
        return True

    def make_choice(self, choice_index: int) -> Optional[Scene]:
        """Make a choice and progress the story."""
        if not self.current_scene:
            return None
        
        available_choices = self.get_available_choices()
        if not available_choices or choice_index >= len(available_choices):
            return None
        
        choice = available_choices[choice_index]
        
        # Apply choice effects
        for key, value in choice.effects.items():
            self.story_state[key] = self.story_state.get(key, 0) + value
        
        # Move to next scene
        next_scene = self.scenes[choice.next_scene]
        self.current_scene = next_scene
        self.scene_history.append(next_scene.id)
        
        return next_scene

    def get_story_state(self) -> Dict[str, float]:
        """Get the current state of the story."""
        return self.story_state.copy()

    def get_scene_history(self) -> List[str]:
        """Get the history of visited scenes."""
        return self.scene_history.copy() 