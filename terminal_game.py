#!/usr/bin/env python3
"""
🎮 BeTheMC Terminal Game - Full Pokémon Adventure in Your Terminal!

A complete terminal-based Pokémon adventure game using the bethemc_complex architecture.
Uses AI story generation, personality system, and MongoDB for saves.
"""

import asyncio
import sys
import os
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import json

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.services.game_service import GameService
from bethemc_complex.models.core import GameState, Player, Story, Choice, Memory, GameProgression
from bethemc_complex.database.service import SimpleDatabaseService
from bethemc_complex.database.connection import connect_to_database, disconnect_from_database
from bethemc_complex.utils.logger import get_logger

logger = get_logger(__name__)

class Colors:
    """Terminal color codes for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TerminalGame:
    """Main terminal game class using bethemc_complex architecture"""
    
    def __init__(self):
        """Initialize the terminal game with the complex architecture services"""
        self.game_service = GameService()
        self.db_service = SimpleDatabaseService()
        self.current_game_state: Optional[GameState] = None
        
    def print_header(self, text: str, color: str = Colors.CYAN):
        """Print a formatted header"""
        print(f"\n{color}{'='*60}")
        print(f"{text.center(60)}")
        print(f"{'='*60}{Colors.END}\n")
    
    def print_story(self, story: Story):
        """Print the current story with beautiful formatting"""
        # Extract clean narrative from the story content
        clean_content = self.extract_clean_narrative(story.content)
        
        print(f"{Colors.BLUE}📍 Location: {Colors.BOLD}{story.location}{Colors.END}")
        print(f"{Colors.GREEN}📖 {story.title}{Colors.END}\n")
        print(f"{Colors.CYAN}{clean_content}{Colors.END}\n")
    
    def extract_clean_narrative(self, content: str) -> str:
        """Extract clean narrative from LLM-generated content"""
        # Remove common LLM formatting artifacts
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and common LLM artifacts
            if not line:
                continue
            if line.startswith('**') and line.endswith('**'):
                continue
            if line.startswith('Choice') and ':' in line:
                continue
            if line.lower().startswith('what do you'):
                continue
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def print_choices(self, choices: List[Choice]):
        """Print available choices"""
        print(f"{Colors.YELLOW}🎯 What do you want to do?{Colors.END}")
        for i, choice in enumerate(choices, 1):
            effects_str = ""
            if choice.effects:
                effects_list = [f"+{v} {k}" for k, v in choice.effects.items()]
                effects_str = f" {Colors.GRAY}({', '.join(effects_list)}){Colors.END}"
            print(f"  {Colors.BOLD}{i}.{Colors.END} {choice.text}{effects_str}")
        print()
    
    def print_personality(self, personality: Dict[str, int]):
        """Print current personality traits"""
        print(f"{Colors.GREEN}🧠 Personality Traits:{Colors.END}")
        for trait, value in personality.items():
            bar_length = 10
            filled = int((value / 10) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"  {trait.capitalize()}: {bar} {value}/10")
        print()
    
    async def get_player_choice(self, choices: List[Choice]) -> Choice:
        """Get the player's choice"""
        while True:
            try:
                choice_input = input(f"{Colors.BOLD}Enter your choice (1-{len(choices)}) or 'q' to quit: {Colors.END}")
                
                if choice_input.lower() in ['q', 'quit', 'exit']:
                    print(f"{Colors.YELLOW}Thanks for playing! Your progress has been saved.{Colors.END}")
                    await self.save_game()
                    sys.exit(0)
                
                choice_index = int(choice_input) - 1
                if 0 <= choice_index < len(choices):
                    return choices[choice_index]
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and {len(choices)}.{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Please enter a number or 'q' to quit.{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Game interrupted. Your progress has been saved.{Colors.END}")
                await self.save_game()
                sys.exit(0)
    
    async def start_new_game(self):
        """Start a new game using the default bethemc_complex initialization"""
        self.print_header("🎮 Welcome to BeTheMC - Your Pokémon Adventure!", Colors.GREEN)
        
        print(f"{Colors.CYAN}Welcome to the world of Pokémon! You're about to embark on an incredible adventure.{Colors.END}")
        print(f"{Colors.BLUE}This game features AI-powered storytelling that adapts to your choices and personality.{Colors.END}\n")
        
        # Get player name
        player_name = input(f"{Colors.BOLD}What's your name, trainer? {Colors.END}").strip()
        if not player_name:
            player_name = "Trainer"
        
        print(f"\n{Colors.GREEN}Welcome, {player_name}! Your adventure begins now...{Colors.END}")
        
        try:
            # Use the default bethemc_complex game initialization
            self.current_game_state = await self.game_service.start_new_game(player_name)
            
            # Set a consistent player ID for terminal game saves
            self.current_game_state.player.id = "terminal_game_player"
            
            logger.info(f"Started new game for player: {player_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start new game: {e}")
            print(f"{Colors.RED}Error starting the game: {e}{Colors.END}")
            return False
    
    async def load_game(self):
        """Load a saved game"""
        try:
            # Try to load existing save using a default player ID for terminal game
            save_data = await self.db_service.get_game_state("terminal_game_player")
            if save_data:
                self.current_game_state = save_data
                self.print_header("🔄 Game Loaded Successfully!", Colors.GREEN)
                return True
            else:
                print(f"{Colors.YELLOW}No saved game found. Starting a new adventure!{Colors.END}")
                return False
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            print(f"{Colors.RED}Error loading game: {e}{Colors.END}")
            return False
    
    async def save_game(self):
        """Save the current game state"""
        if not self.current_game_state:
            return
        
        try:
            await self.db_service.save_game_state(self.current_game_state)
            print(f"{Colors.GREEN}✅ Game saved successfully!{Colors.END}")
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            print(f"{Colors.RED}Error saving game: {e}{Colors.END}")
    
    async def game_loop(self):
        """Main game loop"""
        if not self.current_game_state:
            return
        
        turn_count = 0
        
        while True:
            turn_count += 1
            
            # Display current state
            self.print_header(f"🎮 Turn {turn_count} - {self.current_game_state.current_story.location}")
            self.print_story(self.current_game_state.current_story)
            
            # Show personality traits
            self.print_personality(self.current_game_state.player.personality_traits)
            
            # Show choices
            if not self.current_game_state.available_choices:
                print(f"{Colors.RED}No choices available. The adventure ends here.{Colors.END}")
                break
            
            self.print_choices(self.current_game_state.available_choices)
            
            # Get player choice
            selected_choice = await self.get_player_choice(self.current_game_state.available_choices)
            
            print(f"\n{Colors.CYAN}You chose: {selected_choice.text}{Colors.END}")
            
            # Process choice using the game service
            try:
                self.current_game_state = await self.game_service.process_choice(
                    self.current_game_state, 
                    selected_choice.id
                )
                
                # Auto-save every few turns
                if turn_count % 3 == 0:
                    await self.save_game()
                    
            except Exception as e:
                logger.error(f"Error processing choice: {e}")
                print(f"{Colors.RED}Error processing your choice: {e}{Colors.END}")
                break
            
            # Add some spacing
            print("\n" + "─" * 60 + "\n")
    
    async def run(self):
        """Main entry point for the terminal game"""
        try:
            # Connect to database
            await connect_to_database()
            logger.info("Connected to database successfully")
            
            # Show welcome and ask for new game or load
            self.print_header("🎮 BeTheMC - Pokémon Terminal Adventure", Colors.GREEN)
            print(f"{Colors.CYAN}Welcome to your Pokémon adventure!{Colors.END}")
            print(f"{Colors.BLUE}1. Start New Game")
            print(f"2. Load Saved Game")
            print(f"3. Quit{Colors.END}")
            
            choice = input(f"\n{Colors.BOLD}Choose an option (1-3): {Colors.END}").strip()
            
            if choice == "1":
                if await self.start_new_game():
                    await self.game_loop()
            elif choice == "2":
                if await self.load_game():
                    await self.game_loop()
                else:
                    if await self.start_new_game():
                        await self.game_loop()
            elif choice == "3":
                print(f"{Colors.YELLOW}Thanks for visiting! Come back anytime!{Colors.END}")
                return
            else:
                print(f"{Colors.RED}Invalid choice. Starting new game...{Colors.END}")
                if await self.start_new_game():
                    await self.game_loop()
            
        except Exception as e:
            logger.error(f"Game error: {e}")
            print(f"{Colors.RED}An error occurred: {e}{Colors.END}")
        finally:
            # Ensure we save before disconnecting
            if self.current_game_state:
                await self.save_game()
            await disconnect_from_database()
            logger.info("Disconnected from database")

async def main():
    """Main function to run the terminal game"""
    game = TerminalGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main()) 