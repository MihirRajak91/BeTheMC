"""
Main game loop for the dynamic Pokémon adventure.
"""
from typing import Dict, Any, List
from bethemc.ai.story_generator import StoryGenerator
from bethemc.utils.config import Config
from bethemc.utils.logger import setup_logger
from bethemc.core.progression import ProgressionManager

logger = setup_logger(__name__)

class GameLoop:
    def __init__(self):
        """Initialize the game loop."""
        self.config = Config()
        self.story_generator = StoryGenerator()
        self.progression = ProgressionManager(self.config)
        self.player_state = {
            "location": "Pallet Town",
            "personality": {
                "friendship": 0.5,      # Ability to form bonds
                "courage": 0.5,         # Willingness to face challenges
                "curiosity": 0.5,       # Desire to explore and learn
                "wisdom": 0.5,          # Ability to make good decisions
                "determination": 0.5    # Persistence in achieving goals
            },
            "recent_events": [],
            "relationships": {},        # Friendships with characters and Pokémon
            "pokemon_partners": [],     # Pokémon companions (not just team)
            "memories": []              # Important moments and bonds
        }

    def start_game(self):
        """Start the game and begin the story."""
        logger.info("Starting new game...")
        
        # Generate initial narrative
        narrative = self.story_generator.generate_narrative(
            location=self.player_state["location"],
            personality=self.player_state["personality"],
            recent_events=self.player_state["recent_events"]
        )
        
        print("\n" + "="*80)
        print(narrative["narrative"])
        print("="*80 + "\n")
        
        # Generate initial choices
        choices = self.story_generator.generate_choices(
            current_situation=narrative["narrative"],
            personality=self.player_state["personality"],
            active_promises=narrative.get("active_promises", []),
            key_relationships=narrative.get("key_relationships", [])
        )
        
        self._display_choices(choices)
        return choices

    def process_choice(self, choice_index: int, choices: List[Dict[str, Any]]):
        """Process the player's choice and generate the next story segment."""
        if not 0 <= choice_index < len(choices):
            logger.error(f"Invalid choice index: {choice_index}")
            return None
        
        choice = choices[choice_index]
        logger.info(f"Player chose: {choice['text']}")
        
        # Update player state
        self.player_state["recent_events"].insert(0, choice["text"])
        if len(self.player_state["recent_events"]) > 5:
            self.player_state["recent_events"].pop()
        
        # Update personality based on choice effects
        for trait, effect in choice["effects"].items():
            if trait in self.player_state["personality"]:
                self.player_state["personality"][trait] = min(1.0, max(0.0, 
                    self.player_state["personality"][trait] + effect))
        
        # Add choice to progression system
        self.progression.add_scene({
            "location": self.player_state["location"],
            "description": choice["text"],
            "choices": [choice],
            "timestamp": "2024-01-01T12:00:00"  # Simplified timestamp
        })
        
        # Generate next narrative
        narrative = self.story_generator.generate_narrative(
            location=self.player_state["location"],
            personality=self.player_state["personality"],
            recent_events=self.player_state["recent_events"]
        )
        
        print("\n" + "="*80)
        print(narrative["narrative"])
        print("="*80 + "\n")
        
        # Generate new choices
        new_choices = self.story_generator.generate_choices(
            current_situation=narrative["narrative"],
            personality=self.player_state["personality"],
            active_promises=narrative.get("active_promises", []),
            key_relationships=narrative.get("key_relationships", [])
        )
        
        self._display_choices(new_choices)
        return new_choices

    def _display_choices(self, choices: List[Dict[str, Any]]):
        """Display available choices to the player."""
        print("\nWhat would you like to do?")
        for i, choice in enumerate(choices):
            print(f"{i + 1}. {choice['text']}")
        print()

def main():
    """Main entry point for the game."""
    game = GameLoop()
    choices = game.start_game()
    
    while True:
        try:
            choice = input("Enter your choice (1-{}): ".format(len(choices)))
            if choice.lower() in ['q', 'quit', 'exit']:
                break
            
            choice_index = int(choice) - 1
            choices = game.process_choice(choice_index, choices)
            
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\nGame ended by user.")
            break

if __name__ == "__main__":
    main() 