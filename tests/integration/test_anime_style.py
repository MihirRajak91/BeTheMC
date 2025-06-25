#!/usr/bin/env python3
"""
Test script to demonstrate anime-style storytelling.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.bethemc.core.game import GameLoop
from src.bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_anime_style():
    """Test the anime-style storytelling system."""
    logger.info("Testing anime-style storytelling...")
    
    try:
        # Initialize the game
        game = GameLoop()
        
        print("\n" + "="*80)
        print("🎬 POKÉMON ANIME-STYLE ADVENTURE")
        print("="*80)
        print("Welcome to an anime-style Pokémon adventure!")
        print("Focus on friendship, character development, and emotional bonds.")
        print("No rigid battle mechanics - just fluid storytelling and relationships.")
        print("="*80)
        
        # Show current personality traits
        print(f"\n📊 Your Current Personality:")
        for trait, value in game.player_state["personality"].items():
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            print(f"  {trait.title():12} [{bar}] {value:.1f}")
        
        # Start the story
        print(f"\n📍 Starting in: {game.player_state['location']}")
        print("\n" + "="*80)
        
        # Generate initial narrative
        narrative = game.story_generator.generate_narrative(
            location=game.player_state["location"],
            personality=game.player_state["personality"],
            recent_events=game.player_state["recent_events"],
            progression=game.progression
        )
        
        print("📖 STORY:")
        print(narrative["narrative"])
        print("="*80)
        
        # Generate choices
        choices = game.story_generator.generate_choices(
            current_situation=narrative["narrative"],
            personality=game.player_state["personality"],
            progression=game.progression
        )
        
        print("\n🤔 What would you like to do?")
        for i, choice in enumerate(choices):
            print(f"  {i + 1}. {choice['text']}")
            
            # Show personality effects
            if choice.get('effects'):
                effects = []
                for trait, effect in choice['effects'].items():
                    if effect > 0:
                        effects.append(f"+{effect:.1f} {trait}")
                    elif effect < 0:
                        effects.append(f"{effect:.1f} {trait}")
                if effects:
                    print(f"     💫 Effects: {', '.join(effects)}")
        
        print("\n✨ This is anime-style storytelling - focus on friendship and character growth!")
        print("No rigid battles, no levels, just meaningful relationships and personal development.")
        
        logger.info("Anime-style test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in anime-style test: {e}")
        raise

if __name__ == "__main__":
    test_anime_style() 