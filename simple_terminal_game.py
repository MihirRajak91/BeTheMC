#!/usr/bin/env python3
"""
BeTheMC - Simple Terminal Pokemon Adventure Game

A streamlined version that uses existing codebase components without complex database dependencies.
"""

import sys
import os
import json
import time
import uuid
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from bethemc.ai.generator import StoryGenerator
    from bethemc.core.progression import ProgressionManager
    from bethemc.utils.config import Config
    from bethemc.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please ensure all required packages are installed.")
    sys.exit(1)

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

def colored_print(text: str, color: str = Colors.END):
    """Print colored text."""
    print(f"{color}{text}{Colors.END}")

def print_separator(char: str = "=", length: int = 60):
    """Print a separator line."""
    print(char * length)

def print_banner():
    """Print the game banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║               🎮 BeTheMC Terminal Game 🎮               ║
    ║                 Pokemon Adventure Awaits!                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    colored_print(banner, Colors.CYAN + Colors.BOLD)

def print_personality_bar(trait: str, value: float, width: int = 30):
    """Print a personality trait bar."""
    filled_length = int(width * value)
    bar = "█" * filled_length + "░" * (width - filled_length)
    percentage = int(value * 100)
    
    color = Colors.GREEN if value >= 0.7 else Colors.YELLOW if value >= 0.4 else Colors.RED
    colored_print(f"{trait:12} |{bar}| {percentage:3}%", color)

class SimpleTerminalGame:
    def __init__(self):
        """Initialize the terminal game."""
        self.config = Config()
        self.save_dir = Path("data/saves")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Game state
        self.player_name = ""
        self.personality = {
            "friendship": 5.0,
            "courage": 5.0,
            "curiosity": 5.0,
            "wisdom": 5.0,
            "determination": 5.0
        }
        self.current_location = "Pallet Town"
        self.story_history = []
        self.relationships = {}
        self.pokemon_partners = []
        self.memories = []
        self.game_started = False
        
        # Game components
        self.story_generator = None
        self.progression = None
        
        colored_print("🎮 Initializing BeTheMC Simple Terminal Game...", Colors.CYAN)
        colored_print("✨ Features: Clean narrative display, File saves, Qdrant story reference", Colors.GRAY)

    def initialize_game_components(self):
        """Initialize the game components."""
        try:
            colored_print("🤖 Initializing AI story generator...", Colors.YELLOW)
            self.story_generator = StoryGenerator()
            
            colored_print("📈 Setting up progression tracking...", Colors.YELLOW)
            self.progression = ProgressionManager(self.config)
            
            colored_print("✅ All systems ready!", Colors.GREEN)
            return True
        except Exception as e:
            colored_print(f"❌ Failed to initialize game components: {e}", Colors.RED)
            colored_print("Please ensure Qdrant is running and all dependencies are installed.", Colors.YELLOW)
            return False

    def start_game(self):
        """Start the main game loop."""
        print_banner()
        
        if not self.initialize_game_components():
            return
        
        while True:
            print_separator()
            colored_print("\n🎮 MAIN MENU", Colors.HEADER + Colors.BOLD)
            print("1. 🆕 New Game")
            print("2. 💾 Load Game")
            print("3. ❓ Help")
            print("4. 🚪 Exit")
            
            choice = input(f"\n{Colors.CYAN}Choose an option (1-4): {Colors.END}").strip()
            
            if choice == "1":
                self.new_game()
            elif choice == "2":
                self.load_game()
            elif choice == "3":
                self.show_help()
            elif choice == "4":
                colored_print("👋 Thanks for playing BeTheMC! See you next time!", Colors.GREEN)
                break
            else:
                colored_print("❌ Invalid choice. Please try again.", Colors.RED)

    def new_game(self):
        """Start a new game."""
        print_separator()
        colored_print("\n🆕 STARTING NEW ADVENTURE", Colors.HEADER + Colors.BOLD)
        
        # Get player name
        while True:
            name = input(f"\n{Colors.GREEN}What's your name, trainer? {Colors.END}").strip()
            if name:
                self.player_name = name
                break
            colored_print("Please enter a valid name.", Colors.RED)
        
        colored_print(f"\nWelcome, {self.player_name}! Let's set up your personality...", Colors.CYAN)
        
        # Personality setup
        self.setup_personality()
        
        # Start the story
        self.game_started = True
        self.story_loop()

    def setup_personality(self):
        """Interactive personality setup."""
        colored_print("\n🧠 PERSONALITY SETUP", Colors.HEADER + Colors.BOLD)
        colored_print("Your personality affects how you experience the world and what choices are available.", Colors.CYAN)
        colored_print("Each trait ranges from 1-10. Choose wisely - this shapes your entire adventure!\n", Colors.CYAN)
        
        trait_descriptions = {
            "friendship": "How easily you bond with Pokemon and people",
            "courage": "Your willingness to face challenges and dangers",
            "curiosity": "Your desire to explore and discover new things",
            "wisdom": "Your thoughtfulness and ability to learn from experience",
            "determination": "Your persistence and refusal to give up"
        }
        
        for trait, description in trait_descriptions.items():
            colored_print(f"\n{trait.title()}: {description}", Colors.BLUE)
            
            while True:
                try:
                    value = input(f"Set {trait} (1-10, current: {self.personality[trait]:.1f}): ").strip()
                    if not value:  # Keep current value if empty
                        break
                    value = float(value)
                    if 1 <= value <= 10:
                        self.personality[trait] = float(value)
                        break
                    else:
                        colored_print("Please enter a number between 1 and 10.", Colors.RED)
                except ValueError:
                    colored_print("Please enter a valid number.", Colors.RED)
        
        # Show final personality
        self.show_personality()

    def show_personality(self):
        """Display current personality traits."""
        colored_print("\n👤 YOUR PERSONALITY PROFILE", Colors.HEADER + Colors.BOLD)
        for trait, value in self.personality.items():
            print_personality_bar(trait.title(), value / 10.0)

    def story_loop(self):
        """Main story generation and choice loop."""
        try:
            while self.game_started:
                # Generate story segment
                colored_print("\n📖 GENERATING STORY...", Colors.YELLOW)
                
                narrative = self.story_generator.generate_narrative(
                    location=self.current_location,
                    personality=self.personality,
                    recent_events=self.story_history[-3:] if self.story_history else [],
                    progression=self.progression
                )
                
                # Display story
                print_separator("─")
                colored_print(f"\n📍 Location: {self.current_location}", Colors.BLUE + Colors.BOLD)
                print_separator("─")
                
                # Extract clean narrative from LLM response
                raw_narrative = narrative.get("narrative", "Your adventure continues...")
                story_text = self.extract_clean_narrative(raw_narrative)
                self.print_wrapped_text(story_text, Colors.END)
                
                print_separator("─")
                
                # Generate choices
                colored_print("\n🔄 GENERATING CHOICES...", Colors.YELLOW)
                
                choices_data = self.story_generator.generate_choices(
                    current_situation=story_text,
                    personality=self.personality,
                    progression=self.progression,
                    current_location=self.current_location
                )
                
                choices = choices_data.get("choices", [])
                
                # Add special choices
                choices.extend([
                    {"text": "📊 Check Status", "effects": {}, "special": "status"},
                    {"text": "💾 Save Game", "effects": {}, "special": "save"},
                    {"text": "🚪 Main Menu", "effects": {}, "special": "menu"}
                ])
                
                # Display choices
                colored_print("\n🎯 WHAT DO YOU WANT TO DO?", Colors.GREEN + Colors.BOLD)
                for i, choice in enumerate(choices, 1):
                    print(f"{i:2}. {choice['text']}")
                
                # Get player choice
                while True:
                    try:
                        choice_num = input(f"\n{Colors.CYAN}Choose an action (1-{len(choices)}): {Colors.END}").strip()
                        if choice_num.lower() in ['q', 'quit', 'exit']:
                            self.game_started = False
                            break
                        
                        choice_idx = int(choice_num) - 1
                        if 0 <= choice_idx < len(choices):
                            self.process_choice(choices[choice_idx])
                            break
                        else:
                            colored_print("❌ Invalid choice number. Please try again.", Colors.RED)
                    except ValueError:
                        colored_print("❌ Please enter a valid number.", Colors.RED)
                    except KeyboardInterrupt:
                        colored_print("\n👋 Game interrupted. Returning to main menu...", Colors.YELLOW)
                        self.game_started = False
                        break
                        
        except Exception as e:
            colored_print(f"❌ An error occurred during the story: {e}", Colors.RED)
            colored_print("Returning to main menu...", Colors.YELLOW)
            self.game_started = False

    def extract_clean_narrative(self, raw_text: str) -> str:
        """Extract clean narrative content from LLM response."""
        if not raw_text:
            return "Your adventure continues..."
        
        # Remove common LLM formatting and instructions
        lines = raw_text.split('\n')
        clean_lines = []
        skip_patterns = [
            '🎮', '🏞️', '🌸', '👥', '🐾', '📚', '📖',  # Emoji headers
            'PLAYER CONTEXT', 'ENHANCED LOCATION', 'SEASONAL CONTEXT',
            'CHARACTER PERSONALITIES', 'POKÉMON PERSONALITIES', 
            'KNOWLEDGE BASE', 'STORY CONTINUITY', 'INSTRUCTIONS',
            'Current Location:', 'Player\'s Personality:', 'Recent Events:',
            'Story Summary:', 'Current Relationships:', 'Active Promises:',
            'What will the Player do next?', 'CHOICES:', '**{', '**CHOICES:**',
            'Explanation of Choices', 'Personality Alignment:', 'Character Roles:',
            'Seasonal Tie-In:', 'Meaningful Consequences:', 'No Rigid Mechanics:',
            'Emotional Connection:', '*', 'Choice X:'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at start/end
            if not line:
                if clean_lines:  # Only add empty lines if we have content
                    clean_lines.append("")
                continue
            
            # Check if this line should be skipped
            should_skip = False
            for pattern in skip_patterns:
                if pattern in line:
                    should_skip = True
                    break
            
            # Stop processing when we hit choice/instruction sections
            if any(marker in line.lower() for marker in ['what will', 'choices:', 'choice 1:', 'choice x:', '1.', '2.', '3.', '4.']):
                break
                
            if not should_skip:
                clean_lines.append(line)
        
        # Join and clean up the result
        result = '\n'.join(clean_lines).strip()
        
        # Remove any remaining formatting artifacts
        result = result.replace('**', '').replace('***', '')
        result = result.replace('[Memory:', '\n[Memory:').replace('[End Memory]', '[End Memory]\n')
        
        # If result is too short or empty, provide default
        if len(result) < 50:
            return "Your adventure continues in the world of Pokémon..."
        
        return result

    def print_wrapped_text(self, text: str, color: str = Colors.END, width: int = 80):
        """Print text wrapped to terminal width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        for line in lines:
            colored_print(line, color)

    def process_choice(self, choice: Dict[str, Any]):
        """Process a player choice."""
        # Handle special choices
        if choice.get("special"):
            if choice["special"] == "status":
                self.show_status()
                return
            elif choice["special"] == "save":
                self.save_game()
                return
            elif choice["special"] == "menu":
                self.game_started = False
                return
        
        # Process regular choice
        choice_text = choice["text"]
        effects = choice.get("effects", {})
        
        # Add to story history
        self.story_history.append(choice_text)
        
        # Apply personality effects
        for trait, effect in effects.items():
            if trait in self.personality:
                old_value = self.personality[trait]
                self.personality[trait] = max(1.0, min(10.0, old_value + effect * 10))
                
                # Show personality change
                if abs(effect) > 0.05:
                    change_text = "increased" if effect > 0 else "decreased"
                    colored_print(f"✨ Your {trait} has {change_text}!", Colors.GREEN)
        
        # Add memory to progression manager
        self.progression.add_memory(
            memory_type="choice",
            content=f"Player chose: {choice_text}",
            metadata={"location": self.current_location}
        )
        
        colored_print(f"\n🎯 You chose: {choice_text}", Colors.GREEN)
        time.sleep(1)  # Small pause for dramatic effect

    def show_status(self):
        """Show detailed player status."""
        print_separator()
        colored_print(f"\n📊 STATUS - {self.player_name}", Colors.HEADER + Colors.BOLD)
        
        colored_print(f"\n📍 Current Location: {self.current_location}", Colors.BLUE)
        colored_print(f"🎲 Choices Made: {len(self.story_history)}", Colors.BLUE)
        colored_print(f"❤️ Relationships: {len(self.relationships)}", Colors.BLUE)
        colored_print(f"🎭 Memories: {len(self.memories)}", Colors.BLUE)
        
        self.show_personality()
        
        if self.story_history:
            colored_print(f"\n📜 Recent Actions:", Colors.YELLOW)
            for action in self.story_history[-5:]:
                print(f"  • {action}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    def save_game(self):
        """Save the current game state to file."""
        try:
            save_data = {
                "player_name": self.player_name,
                "personality": self.personality,
                "current_location": self.current_location,
                "story_history": self.story_history,
                "relationships": self.relationships,
                "pokemon_partners": self.pokemon_partners,
                "memories": self.memories,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Generate save filename
            safe_name = "".join(c for c in self.player_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.json"
            filepath = self.save_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            colored_print(f"💾 Game saved as: {filename}", Colors.GREEN)
            
        except Exception as e:
            colored_print(f"❌ Failed to save game: {e}", Colors.RED)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    def load_game(self):
        """Load a saved game."""
        save_files = list(self.save_dir.glob("*.json"))
        
        if not save_files:
            colored_print("❌ No saved games found.", Colors.RED)
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        print_separator()
        colored_print("\n💾 SAVED GAMES", Colors.HEADER + Colors.BOLD)
        
        for i, save_file in enumerate(save_files, 1):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                name = save_data.get("player_name", "Unknown")
                timestamp = save_data.get("timestamp", "Unknown time")
                location = save_data.get("current_location", "Unknown location")
                
                print(f"{i:2}. {name} - {location} ({timestamp[:19]})")
                
            except Exception as e:
                print(f"{i:2}. {save_file.name} (corrupted)")
        
        print(f"{len(save_files) + 1:2}. Cancel")
        
        while True:
            try:
                choice = int(input(f"\n{Colors.CYAN}Choose save file (1-{len(save_files) + 1}): {Colors.END}"))
                
                if choice == len(save_files) + 1:
                    return
                
                if 1 <= choice <= len(save_files):
                    save_file = save_files[choice - 1]
                    self.load_save_file(save_file)
                    break
                else:
                    colored_print("❌ Invalid choice.", Colors.RED)
            except ValueError:
                colored_print("❌ Please enter a valid number.", Colors.RED)

    def load_save_file(self, save_file: Path):
        """Load a specific save file."""
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.player_name = save_data.get("player_name", "")
            self.personality = save_data.get("personality", self.personality)
            self.current_location = save_data.get("current_location", "Pallet Town")
            self.story_history = save_data.get("story_history", [])
            self.relationships = save_data.get("relationships", {})
            self.pokemon_partners = save_data.get("pokemon_partners", [])
            self.memories = save_data.get("memories", [])
            
            colored_print(f"✅ Game loaded successfully! Welcome back, {self.player_name}!", Colors.GREEN)
            self.game_started = True
            self.story_loop()
            
        except Exception as e:
            colored_print(f"❌ Failed to load game: {e}", Colors.RED)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    def show_help(self):
        """Show game help information."""
        print_separator()
        colored_print("\n❓ GAME HELP", Colors.HEADER + Colors.BOLD)
        
        help_text = """
🎮 HOW TO PLAY:
• Choose from numbered options by typing the number and pressing Enter
• Your personality traits influence available choices and story outcomes
• Save your game anytime using the Save option
• Build relationships with Pokemon and characters you meet

🎭 PERSONALITY TRAITS:
• Friendship: Affects how easily you bond with Pokemon and people
• Courage: Determines your willingness to face dangers
• Curiosity: Influences your desire to explore new places
• Wisdom: Affects your ability to make thoughtful decisions
• Determination: Shows your persistence in difficult situations

⌨️ CONTROLS:
• Type numbers (1, 2, 3, etc.) to select choices
• Type 'q', 'quit', or 'exit' to return to main menu
• Ctrl+C to interrupt if needed
        """
        
        self.print_wrapped_text(help_text.strip(), Colors.CYAN)
        input(f"\n{Colors.GREEN}Press Enter to return to main menu...{Colors.END}")

def main():
    """Main entry point."""
    try:
        game = SimpleTerminalGame()
        game.start_game()
    except KeyboardInterrupt:
        colored_print("\n\n👋 Thanks for playing BeTheMC!", Colors.GREEN)
    except Exception as e:
        colored_print(f"\n❌ Unexpected error: {e}", Colors.RED)
        colored_print("Please report this issue on GitHub.", Colors.YELLOW)

if __name__ == "__main__":
    main() 