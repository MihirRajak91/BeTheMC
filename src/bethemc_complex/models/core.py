"""
Core domain models for BeTheMC.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class PersonalityTraits:
    friendship: float
    courage: float
    curiosity: float
    wisdom: float
    determination: float

@dataclass
class Player:
    id: str
    name: str
    personality_traits: Dict[str, int]

@dataclass
class Story:
    id: str
    title: str
    content: str
    location: str

@dataclass
class Choice:
    id: str
    text: str
    effects: Dict[str, int] = field(default_factory=dict)

@dataclass
class Memory:
    id: str
    content: str
    memory_type: str
    timestamp: datetime

@dataclass
class PersonalityTrait:
    name: str
    value: int

@dataclass
class GameProgression:
    current_location: str
    completed_events: List[str] = field(default_factory=list)
    relationships: Dict[str, Any] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)

@dataclass
class GameState:
    player: Player
    current_story: Story
    available_choices: List[Choice]
    memories: List[Memory]
    progression: GameProgression

@dataclass
class NarrativeSegment:
    content: str
    location: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict) 