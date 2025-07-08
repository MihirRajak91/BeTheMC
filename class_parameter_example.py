#!/usr/bin/env python3
"""
🎯 EXAMPLE: How Parameters Can Accept Class Types

This shows how:
1. Type hints work
2. Dependency injection works  
3. How FastAPI uses this pattern
"""

from typing import Optional
from dataclasses import dataclass

# 🎮 Example Classes
@dataclass
class Player:
    name: str
    level: int = 1

@dataclass  
class GameManager:
    def __init__(self):
        self.players = []
    
    def add_player(self, name: str) -> Player:
        player = Player(name=name, level=1)
        self.players.append(player)
        return player
    
    def get_player(self, name: str) -> Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return None

# 🔧 Dependency Function (like get_simple_game_manager)
def get_game_manager() -> GameManager:
    """Create and return a GameManager instance."""
    return GameManager()

# 🎯 Function with Class Type Parameter
def process_player(
    player_name: str,
    game_manager: GameManager = None  # Type hint: expects GameManager object
) -> Player:
    """
    This function takes a GameManager object as a parameter.
    
    The type hint `: GameManager` tells Python:
    - "This parameter should be a GameManager instance"
    - It's like saying "I expect a GameManager object here"
    """
    if game_manager is None:
        game_manager = get_game_manager()  # Create one if not provided
    
    return game_manager.add_player(player_name)

# 🚀 Let's Test It!
def main():
    print("🎮 Testing Class Type Parameters")
    print("=" * 40)
    
    # Method 1: Pass the object directly
    print("1️⃣ Passing GameManager object directly:")
    manager = GameManager()
    player1 = process_player("Ash", game_manager=manager)
    print(f"   Created player: {player1}")
    
    # Method 2: Let the function create the object
    print("\n2️⃣ Letting function create GameManager:")
    player2 = process_player("Misty")  # game_manager will be None, so it creates one
    print(f"   Created player: {player2}")
    
    # Method 3: Show type hints in action
    print("\n3️⃣ Type hints help with IDE and tools:")
    print("   - IDE knows game_manager is a GameManager")
    print("   - Can autocomplete: game_manager.add_player()")
    print("   - Type checkers can verify correctness")
    
    # Method 4: FastAPI style (simplified)
    print("\n4️⃣ FastAPI style dependency injection:")
    def fastapi_style_function(
        player_name: str,
        game_manager: GameManager = get_game_manager()  # Default value
    ):
        return game_manager.add_player(player_name)
    
    player3 = fastapi_style_function("Brock")
    print(f"   Created player: {player3}")

if __name__ == "__main__":
    main() 