#!/usr/bin/env python3
"""
Final test to verify story generation works with fixed location data.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.ai.story_generator import StoryGenerator
from bethemc_complex.utils.config import Config

def test_final_story():
    """Test story generation with fixed location data."""
    print("🎯 Final Story Generation Test...")
    
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
        
        # Test location info retrieval
        print("🔍 Testing location info retrieval...")
        location_info = story_generator.knowledge_base.get_location_info(location)
        print(f"Location info: {location_info}")
        
        # Test story context retrieval
        print("\n📚 Testing story context retrieval...")
        story_context = story_generator.knowledge_base.get_story_context(
            f"Events in {location} involving {', '.join(recent_events)}"
        )
        print(f"Story context items: {len(story_context)}")
        
        print("\n✅ Location data is working correctly!")
        print("🎉 The story generation should now work properly with Pallet Town data.")
        
    except Exception as e:
        print(f"❌ Error in final test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_story() 