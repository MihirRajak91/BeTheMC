#!/usr/bin/env python3
"""
Test script for the compressed context functionality in long stories.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bethemc.core.progression import ProgressionManager
from bethemc.ai.story_generator import StoryGenerator
from bethemc.utils.config import Config
from bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_compressed_context():
    """Test the compressed context functionality."""
    print("🧪 Testing Compressed Context for Long Stories")
    print("=" * 50)
    
    # Initialize components
    config = Config()
    progression = ProgressionManager(config)
    story_generator = StoryGenerator(config)
    
    # Simulate a long story by adding many scenes and memories
    print("\n📚 Simulating a long story with many scenes...")
    
    # Add some sample memories to simulate a long story
    sample_memories = [
        {
            "type": "promise",
            "content": "Promised to help Professor Oak find the missing Pokémon",
            "location": "Pallet Town",
            "timestamp": "2024-01-01T10:00:00"
        },
        {
            "type": "friendship", 
            "content": "Became close friends with Ash after helping him catch Pikachu",
            "location": "Route 1",
            "timestamp": "2024-01-01T11:00:00"
        },
        {
            "type": "promise",
            "content": "Vowed to become the best Pokémon trainer in Kanto",
            "location": "Viridian City",
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "type": "friendship",
            "content": "Formed a strong bond with Misty during the journey",
            "location": "Route 2", 
            "timestamp": "2024-01-01T13:00:00"
        },
        {
            "type": "promise",
            "content": "Swore to protect all Pokémon from Team Rocket",
            "location": "Viridian Forest",
            "timestamp": "2024-01-01T14:00:00"
        }
    ]
    
    # Add memories to the knowledge base
    for memory in sample_memories:
        progression.knowledge_base.add_memory({
            "memory_type": memory["type"],
            "content": memory["content"],
            "timestamp": memory["timestamp"],
            "metadata": {"location": memory["location"]}
        })
    
    # Simulate many scenes (more than the threshold of 10)
    for i in range(15):
        scene_data = {
            "location": f"Scene {i+1}",
            "description": f"This is scene number {i+1}",
            "choices": [],
            "timestamp": f"2024-01-01T{10+i}:00:00"
        }
        progression.scene_history.append(scene_data)
    
    print(f"✅ Added {len(sample_memories)} memories and {len(progression.scene_history)} scenes")
    
    # Test compressed context
    print("\n🎯 Testing compressed context...")
    compressed = progression.get_compressed_context("Viridian City")
    
    print(f"📝 Compressed Summary: {compressed['compressed_summary']}")
    print(f"🤝 Active Promises: {len(compressed['active_promises'])}")
    print(f"💕 Key Relationships: {len(compressed['key_relationships'])}")
    print(f"📍 Location Context: {len(compressed['location_context'])}")
    print(f"📊 Story Length: {compressed['story_length']}")
    
    # Test story generation with compressed context
    print("\n🎭 Testing story generation with compressed context...")
    
    personality = {
        "friendship": 0.8,
        "courage": 0.7,
        "curiosity": 0.9,
        "wisdom": 0.6,
        "determination": 0.8
    }
    
    recent_events = ["Arrived in Viridian City", "Met a mysterious trainer"]
    
    try:
        narrative_result = story_generator.generate_narrative(
            location="Viridian City",
            personality=personality,
            recent_events=recent_events
        )
        
        print("✅ Story generation successful!")
        print(f"📖 Narrative preview: {narrative_result['narrative'][:200]}...")
        print(f"🤝 Active promises in context: {len(narrative_result.get('active_promises', []))}")
        print(f"💕 Key relationships in context: {len(narrative_result.get('key_relationships', []))}")
        
    except Exception as e:
        print(f"❌ Story generation failed: {e}")
        logger.error(f"Story generation error: {e}")
    
    # Test choice generation with context
    print("\n🎯 Testing choice generation with context...")
    
    try:
        choices = story_generator.generate_choices(
            current_situation="Standing in Viridian City with new friends",
            personality=personality,
            active_promises=compressed['active_promises'],
            key_relationships=compressed['key_relationships']
        )
        
        print(f"✅ Generated {len(choices)} choices:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice['text']}")
            print(f"     Effects: {choice['effects']}")
        
    except Exception as e:
        print(f"❌ Choice generation failed: {e}")
        logger.error(f"Choice generation error: {e}")
    
    print("\n🎉 Compressed context test completed!")

if __name__ == "__main__":
    test_compressed_context() 