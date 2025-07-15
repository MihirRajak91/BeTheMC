#!/usr/bin/env python3
"""
Test Enhanced BeTheMC Storytelling with Ollama API
Demonstrates character-driven, anime-style stories using gemma3:27b
"""
import sys
from pathlib import Path
import json
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.bethemc.data.vector_store import KantoKnowledgeBase
from src.bethemc.ai.generator import StoryGenerator
from src.bethemc.core.progression import ProgressionManager
from src.bethemc.utils.config import Config

def create_ollama_config():
    """Create configuration for Ollama API with gemma3:27b."""
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
    """Test configuration wrapper."""
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

def test_enhanced_story_generation():
    """Test enhanced story generation with real LLM."""
    print("🎬 Testing Enhanced Story Generation with Ollama")
    print("=" * 60)
    
    config = TestConfig(create_ollama_config())
    
    try:
        # Initialize components
        print("📋 Initializing components...")
        knowledge_base = KantoKnowledgeBase(config)
        story_generator = StoryGenerator()
        progression = ProgressionManager(config)
        
        # Test scenario: Visiting Pewter City and meeting Brock
        location = "pewter-city"
        personality = {"kindness": 0.8, "courage": 0.7, "curiosity": 0.9}
        recent_events = ["arrived in Pewter City", "looking for the gym"]
        
        print(f"\n🎯 Scenario: Visiting {location}")
        print(f"Player Personality: {personality}")
        print(f"Recent Events: {', '.join(recent_events)}")
        
        # Generate enhanced narrative
        print("\n⏳ Generating enhanced story (this may take a moment)...")
        start_time = time.time()
        
        narrative_result = story_generator.generate_narrative(
            location=location,
            personality=personality,
            recent_events=recent_events,
            progression=progression
        )
        
        generation_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ Story Generated! (took {generation_time:.2f} seconds)")
        print("=" * 60)
        print("📖 GENERATED STORY:")
        print("=" * 60)
        print(narrative_result["narrative"])
        
        # Show enhanced context used
        print("\n" + "=" * 60)
        print("🔍 ENHANCED CONTEXT USED:")
        print("=" * 60)
        
        enhanced_context = narrative_result["metadata"]["enhanced_context"]
        print(f"🏞️  Location: {enhanced_context['location_atmosphere'][:100]}...")
        print(f"🌸 Season: {enhanced_context['seasonal_atmosphere']}")
        
        if enhanced_context['character_personalities']:
            print("👥 Characters:")
            for char in enhanced_context['character_personalities']:
                print(f"   • {char}")
        
        if enhanced_context['pokemon_personalities']:
            print("🐾 Pokémon:")
            for pokemon in enhanced_context['pokemon_personalities']:
                print(f"   • {pokemon}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_driven_choices():
    """Test character-driven choice generation."""
    print("\n🎯 Testing Character-Driven Choices")
    print("=" * 60)
    
    config = TestConfig(create_ollama_config())
    
    try:
        story_generator = StoryGenerator()
        progression = ProgressionManager(config)
        
        situation = "You're lost in a cave and see Brock ahead with his Pokémon"
        personality = {"kindness": 0.8, "courage": 0.6}
        location = "pewter-city"
        
        print(f"Situation: {situation}")
        print("\n⏳ Generating choices...")
        
        choices = story_generator.generate_choices(
            current_situation=situation,
            personality=personality,
            progression=progression,
            current_location=location
        )
        
        print("\n🎪 GENERATED CHOICES:")
        print("=" * 40)
        
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")
            if choice.get('type'):
                print(f"   Type: {choice['type']}")
            if choice.get('expected_response'):
                print(f"   Expected: {choice['expected_response']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_pokemon_encounter():
    """Test Pokémon encounter with personality."""
    print("\n🐾 Testing Pokémon Encounter Generation")
    print("=" * 60)
    
    config = TestConfig(create_ollama_config())
    
    try:
        story_generator = StoryGenerator()
        progression = ProgressionManager(config)
        
        location = "viridian-forest"
        pokemon_name = "pikachu"
        personality = {"kindness": 0.9, "playfulness": 0.8}
        
        print(f"Location: {location}")
        print(f"Pokémon: {pokemon_name}")
        print(f"Trainer Personality: {personality}")
        
        print("\n⏳ Generating Pokémon encounter...")
        
        encounter_result = story_generator.generate_pokemon_encounter(
            location=location,
            pokemon_name=pokemon_name,
            personality=personality,
            progression=progression
        )
        
        print("\n🌟 POKÉMON ENCOUNTER:")
        print("=" * 40)
        print(encounter_result["narrative"])
        
        print("\n🎮 ENCOUNTER CHOICES:")
        print("=" * 40)
        for i, choice in enumerate(encounter_result["choices"], 1):
            print(f"{i}. {choice['text']} ({choice['type']})")
            print(f"   Outcome: {choice['outcome']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_direct_ollama_api():
    """Test direct Ollama API call to verify connection."""
    print("\n🔧 Testing Direct Ollama API Connection")
    print("=" * 60)
    
    import requests
    
    try:
        print("📡 Testing connection to http://192.168.1.68:11434/api/generate")
        
        payload = {
            "model": "gemma3:27b",
            "prompt": "Write a short story about a Pokémon trainer meeting Pikachu for the first time in anime style.",
            "stream": False,
            "options": {
                "temperature": 0.8,
                "num_predict": 200
            }
        }
        
        print("⏳ Sending request...")
        start_time = time.time()
        
        response = requests.post(
            "http://192.168.1.68:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "No response")
            
            print(f"✅ Connection successful! (took {response_time:.2f} seconds)")
            print("=" * 40)
            print("📖 API Response:")
            print("=" * 40)
            print(content)
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Please check:")
        print("   1. Ollama is running on 192.168.1.68:11434")
        print("   2. The gemma3:27b model is available")
        print("   3. Network connectivity")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_streaming_api():
    """Test streaming API functionality."""
    print("\n🌊 Testing Streaming API")
    print("=" * 60)
    
    import requests
    import json
    
    try:
        payload = {
            "model": "gemma3:27b",
            "prompt": "Tell a short anime-style story about friendship between a trainer and Pokémon.",
            "stream": True,
            "options": {
                "temperature": 0.8,
                "num_predict": 150
            }
        }
        
        print("📡 Starting streaming request...")
        
        response = requests.post(
            "http://192.168.1.68:11434/api/generate",
            json=payload,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Streaming connection established")
            print("=" * 40)
            print("📖 Streaming Response:")
            print("=" * 40)
            
            full_content = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            content = chunk['response']
                            print(content, end='', flush=True)
                            full_content += content
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            print("\n\n✅ Streaming completed successfully!")
            return True
        else:
            print(f"❌ Streaming failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return False

def main():
    """Run all enhanced storytelling tests."""
    print("🎮 Enhanced BeTheMC + Ollama Integration Test Suite")
    print("=" * 70)
    print("Testing anime-style storytelling with gemma3:27b model")
    
    # Test results
    results = []
    
    # Test 1: Direct API connection
    print("\n" + "🔧 PHASE 1: API CONNECTION TEST" + "\n")
    results.append(test_direct_ollama_api())
    
    # Test 2: Streaming functionality
    print("\n" + "🌊 PHASE 2: STREAMING TEST" + "\n")
    results.append(test_streaming_api())
    
    # Only proceed with advanced tests if basic connection works
    if results[0]:
        # Test 3: Enhanced story generation
        print("\n" + "🎬 PHASE 3: ENHANCED STORY GENERATION" + "\n")
        results.append(test_enhanced_story_generation())
        
        # Test 4: Character-driven choices
        print("\n" + "🎯 PHASE 4: CHARACTER-DRIVEN CHOICES" + "\n")
        results.append(test_character_driven_choices())
        
        # Test 5: Pokémon encounter
        print("\n" + "🐾 PHASE 5: POKÉMON ENCOUNTER" + "\n")
        results.append(test_pokemon_encounter())
    else:
        print("\n⚠️  Skipping advanced tests due to connection issues")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    test_names = [
        "API Connection",
        "Streaming",
        "Enhanced Story Generation", 
        "Character-Driven Choices",
        "Pokémon Encounter"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    successful_tests = sum(results)
    total_tests = len(results)
    
    print(f"\nOverall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your enhanced BeTheMC system is ready for anime-style storytelling!")
        print("\nFeatures working:")
        print("• Rich character personalities driving interactions")
        print("• Enhanced location atmosphere")
        print("• Seasonal events and weather effects")
        print("• Pokémon personality-driven encounters")
        print("• Dynamic choice generation")
        print("• Streaming response support")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} test(s) failed")
        print("Please check the error messages above for troubleshooting")

if __name__ == "__main__":
    main() 