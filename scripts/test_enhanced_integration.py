#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced BeTheMC integration.
Shows character personalities, seasonal events, location atmosphere, and dynamic choices.
"""
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.bethemc.data.vector_store import KantoKnowledgeBase
from src.bethemc.core.progression import ProgressionManager
from src.bethemc.utils.config import Config

def create_test_config():
    """Create a test configuration for the demo."""
    return {
        "ai": {
            "embedder": {
                "provider": "sentence-transformers",
                "model": "all-MiniLM-L6-v2",
                "api_base": "",
                "api_key": ""
            },
            "llm": {
                "provider": "local",
                "model": "gemma3:27b",
                "temperature": 0.8,
                "max_tokens": 1500,
                "api_base": "http://192.168.1.68:11434/api/generate",
                "api_key": ""
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "host": "localhost",
            "port": 6333,
            "collections": {
                "story_segments": {
                    "name": "story_segments",
                    "vector_size": 384,
                    "similarity_threshold": 0.85
                },
                "character_memories": {
                    "name": "character_memories", 
                    "vector_size": 384,
                    "similarity_threshold": 0.8
                },
                "player_choices": {
                    "name": "player_choices",
                    "vector_size": 384,
                    "similarity_threshold": 0.75
                }
            },
            "max_results": 5
        },
        "story": {
            "max_history_length": 20
        },
        "save_dir": "data/saves",
        "logging": {
            "level": "INFO"
        }
    }

class TestConfig:
    """Test configuration class."""
    def __init__(self, config_dict):
        self.config = config_dict
    
    def get(self, key, default=None):
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

def test_enhanced_character_interactions():
    """Test enhanced character interactions."""
    print("🎭 Testing Enhanced Character Interactions")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    
    # Test character personality retrieval
    characters_to_test = ["Brock", "Misty", "Professor Oak"]
    
    for character_name in characters_to_test:
        character_info = knowledge_base.get_character_personality(character_name)
        print(f"\n🎯 {character_name}:")
        print(f"   Core Traits: {', '.join(character_info.get('core_traits', []))}")
        print(f"   Backstory: {character_info.get('backstory', 'Unknown')[:100]}...")
        
        # Test character-driven choices
        choices = knowledge_base.get_character_driven_choices(
            "You're lost in a cave and need help",
            [character_name]
        )
        
        if choices:
            choice = choices[0]
            print(f"   Choice: {choice['text']}")
            print(f"   Type: {choice['type']}")
            print(f"   Expected Response: {choice['expected_response']}")

def test_enhanced_location_atmosphere():
    """Test enhanced location atmosphere."""
    print("\n🏞️ Testing Enhanced Location Atmosphere")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    
    # Test locations
    locations_to_test = ["Pewter City", "Viridian Forest", "Pokemon Mansion"]
    
    for location in locations_to_test:
        location_info = knowledge_base.get_enhanced_location_info(location.lower().replace(" ", "-"))
        print(f"\n🎯 {location}:")
        print(f"   Description: {location_info.get('description', 'Unknown')[:100]}...")
        print(f"   Atmosphere: {location_info.get('atmosphere', 'Unknown')[:100]}...")
        
        encounters = location_info.get('encounters', [])
        if encounters:
            print(f"   Sample Encounters: {', '.join([enc.get('pokemon', 'Unknown') for enc in encounters[:3]])}")

def test_seasonal_storytelling():
    """Test seasonal storytelling elements."""
    print("\n🌸 Testing Seasonal Storytelling")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    
    # Test seasonal context
    seasonal_context = knowledge_base.get_seasonal_context()
    print(f"Current Season: {seasonal_context.get('season', 'Unknown')}")
    print(f"Atmosphere: {seasonal_context.get('atmosphere', 'Unknown')}")
    print(f"Events: {', '.join(seasonal_context.get('events', []))}")

def test_pokemon_personalities():
    """Test Pokémon personality system."""
    print("\n🐾 Testing Pokémon Personalities")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    
    # Test Pokémon personalities
    pokemon_to_test = ["Pikachu", "Charizard", "Bulbasaur"]
    
    for pokemon_name in pokemon_to_test:
        pokemon_info = knowledge_base.get_pokemon_personality(pokemon_name.lower())
        print(f"\n🎯 {pokemon_name}:")
        print(f"   Traits: {', '.join(pokemon_info.get('personality_traits', []))}")
        print(f"   Temperament: {pokemon_info.get('temperament', 'Unknown')}")
        
        behavior_patterns = pokemon_info.get('behavior_patterns', [])
        if behavior_patterns:
            print(f"   Behavior: {', '.join(behavior_patterns[:2])}")

def test_progression_system():
    """Test the enhanced progression system."""
    print("\n📈 Testing Enhanced Progression System")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    progression = ProgressionManager(config)
    
    # Test character relationship tracking
    print("Testing character relationship system:")
    progression.update_character_relationship("Brock", "positive_interaction", 0.3)
    relationship_status = progression.get_character_relationship_status("Brock")
    
    print(f"   Brock Relationship:")
    print(f"     Friendship Level: {relationship_status['friendship_level']:.2f}")
    print(f"     Trust Level: {relationship_status['trust_level']:.2f}")
    print(f"     Summary: {relationship_status['relationship_summary']}")
    
    # Test Pokémon bonding
    print("\nTesting Pokémon bonding system:")
    progression.track_pokemon_bond("Pikachu", "trust_building", 0.4)
    
    # Test seasonal event memory
    print("\nTesting seasonal event tracking:")
    progression.add_seasonal_event_memory("Cherry Blossom Festival", "Celadon City", ["Erika"])

def test_enhanced_story_context():
    """Test enhanced story context generation."""
    print("\n📖 Testing Enhanced Story Context")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    
    # Test enhanced story context
    context = knowledge_base.get_enhanced_story_context(
        "Exploring Pewter City with Brock and encountering wild Pokémon",
        include_seasonal=True
    )
    
    print("Enhanced Story Context:")
    print(f"   Characters Found: {len(context.get('characters', []))}")
    print(f"   Locations Found: {len(context.get('locations', []))}")
    print(f"   Pokémon Found: {len(context.get('pokemon', []))}")
    print(f"   Items Found: {len(context.get('items', []))}")
    
    # Show character details
    for character in context.get('characters', [])[:2]:
        print(f"     • {character.get('name', 'Unknown')}: {', '.join(character.get('core_traits', [])[:3])}")
    
    # Show seasonal context
    seasonal = context.get('seasonal', {})
    if seasonal:
        print(f"   Seasonal: {seasonal.get('season', 'Unknown')} - {seasonal.get('atmosphere', 'Unknown')[:50]}...")

def test_integration_workflow():
    """Test a complete integration workflow."""
    print("\n🔄 Testing Complete Integration Workflow")
    print("=" * 50)
    
    config = TestConfig(create_test_config())
    knowledge_base = KantoKnowledgeBase(config)
    progression = ProgressionManager(config)
    
    # Simulate a story scenario
    print("Scenario: Trainer visits Pewter City and meets Brock")
    
    # 1. Get location info
    location_info = knowledge_base.get_enhanced_location_info("pewter-city")
    print(f"\n1. Location Context:")
    print(f"   {location_info.get('name', 'Unknown')}: {location_info.get('description', 'Unknown')[:80]}...")
    
    # 2. Get character info
    character_info = knowledge_base.get_character_personality("Brock")
    print(f"\n2. Character Context:")
    print(f"   Brock: {', '.join(character_info.get('core_traits', [])[:3])}")
    
    # 3. Generate choices
    choices = knowledge_base.get_character_driven_choices(
        "You arrive in Pewter City and see Brock tending to his Pokémon",
        ["Brock"]
    )
    print(f"\n3. Generated Choices:")
    for i, choice in enumerate(choices, 1):
        print(f"   {i}. {choice['text']} ({choice['type']})")
    
    # 4. Update relationship
    progression.update_character_relationship("Brock", "positive_interaction", 0.2)
    print(f"\n4. Relationship Updated:")
    relationship = progression.get_character_relationship_status("Brock")
    print(f"   Friendship: {relationship['friendship_level']:.2f}")
    
    # 5. Get comprehensive context
    comprehensive_context = progression.get_comprehensive_story_context("pewter-city")
    print(f"\n5. Comprehensive Context Generated:")
    print(f"   Story Summary: {comprehensive_context['story_summary']}")
    print(f"   Relationships: {len(comprehensive_context['current_relationships'])}")

def main():
    """Run all integration tests."""
    print("🧪 Enhanced BeTheMC Integration Test Suite")
    print("=" * 60)
    print("Testing the integration of enhanced data with BeTheMC system...")
    
    try:
        test_enhanced_character_interactions()
        test_enhanced_location_atmosphere()
        test_seasonal_storytelling()
        test_pokemon_personalities()
        test_progression_system()
        test_enhanced_story_context()
        test_integration_workflow()
        
        print("\n✅ All Integration Tests Completed Successfully!")
        print("\nYour BeTheMC system now has:")
        print("• Rich character personalities driving interactions")
        print("• Enhanced location atmosphere for immersion")
        print("• Seasonal events and weather effects")
        print("• Pokémon personality-driven encounters")
        print("• Dynamic relationship tracking")
        print("• Character-driven choice generation")
        print("• Comprehensive story context with all elements")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 