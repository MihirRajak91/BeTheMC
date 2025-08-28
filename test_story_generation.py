#!/usr/bin/env python3
"""
Test script for story generation without MongoDB dependencies.
"""

import sys
import os
from typing import Dict, List, Any

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.ai.story_generator import StoryGenerator
from bethemc_complex.utils.config import Config

def test_story_generation():
    """Test the story generation functionality."""
    print("🧪 Testing Story Generation...")
    
    try:
        # Initialize story generator
        config = Config()
        story_generator = StoryGenerator(config)
        
        # Test data
        location = "Pallet Town"
        personality = {
            "friendship": 6,
            "courage": 5,
            "curiosity": 7,
            "wisdom": 4,
            "determination": 6
        }
        recent_events = ["Player started their journey", "Explored Pallet Town"]
        
        print(f"📍 Location: {location}")
        print(f"🧠 Personality: {personality}")
        print(f"📖 Recent Events: {recent_events}")
        print("\n" + "="*60)
        
        # Test narrative generation
        print("🎭 Generating narrative...")
        narrative_result = story_generator.generate_narrative(
            location=location,
            personality=personality,
            recent_events=recent_events
        )
        
        print("📝 Generated Narrative:")
        print("-" * 40)
        print(narrative_result.get("narrative", "No narrative generated"))
        print("-" * 40)
        
        # Test choice generation
        print("\n🎯 Generating choices...")
        choices = story_generator.generate_choices(
            current_situation=f"Player is in {location}",
            personality=personality
        )
        
        print("📋 Generated Choices:")
        print("-" * 40)
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice.get('text', 'No text')}")
            print(f"   Effects: {choice.get('effects', {})}")
        print("-" * 40)
        
        print("\n✅ Story generation test completed!")
        
    except Exception as e:
        print(f"❌ Error testing story generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_story_generation() 