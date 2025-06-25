#!/usr/bin/env python3
"""
Test script for the BeTheMC FastAPI endpoints.
"""
import sys
import os
import requests
import json
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing BeTheMC API Endpoints")
    print("=" * 50)
    
    # Test health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test API info
    print("\n2️⃣ Testing API info...")
    try:
        response = requests.get(f"{base_url}/api/v1/info")
        if response.status_code == 200:
            print("✅ API info retrieved")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API info error: {e}")
    
    # Test creating a new game
    print("\n3️⃣ Testing new game creation...")
    try:
        new_game_data = {
            "starting_location": "Pallet Town",
            "personality": {
                "friendship": 0.7,
                "courage": 0.6,
                "curiosity": 0.8,
                "wisdom": 0.5,
                "determination": 0.9
            }
        }
        
        response = requests.post(
            f"{base_url}/api/v1/game/new",
            json=new_game_data
        )
        
        if response.status_code == 200:
            print("✅ New game created")
            result = response.json()
            session_id = result["data"]["session_id"]
            print(f"   Session ID: {session_id}")
            print(f"   Narrative: {result['data']['game_state']['narrative'][:100]}...")
            print(f"   Choices: {len(result['data']['game_state']['choices'])}")
        else:
            print(f"❌ New game creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ New game creation error: {e}")
        return
    
    # Test getting game state
    print("\n4️⃣ Testing get game state...")
    try:
        response = requests.get(f"{base_url}/api/v1/game/{session_id}/state")
        if response.status_code == 200:
            print("✅ Game state retrieved")
            state = response.json()
            print(f"   Location: {state['location']}")
            print(f"   Personality: {state['personality']}")
            print(f"   Choices: {len(state['choices'])}")
        else:
            print(f"❌ Get game state failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get game state error: {e}")
    
    # Test making a choice
    print("\n5️⃣ Testing make choice...")
    try:
        choice_data = {"choice_index": 0}
        response = requests.post(
            f"{base_url}/api/v1/game/{session_id}/choice",
            json=choice_data
        )
        
        if response.status_code == 200:
            print("✅ Choice made successfully")
            result = response.json()
            print(f"   New narrative: {result['narrative'][:100]}...")
            print(f"   New choices: {len(result['choices'])}")
        else:
            print(f"❌ Make choice failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Make choice error: {e}")
    
    # Test adding a memory
    print("\n6️⃣ Testing add memory...")
    try:
        memory_data = {
            "memory_type": "friendship",
            "content": "Became friends with a local Pokémon trainer",
            "location": "Pallet Town",
            "metadata": {"trainer_name": "Ash"}
        }
        
        response = requests.post(
            f"{base_url}/api/v1/game/{session_id}/memory",
            json=memory_data
        )
        
        if response.status_code == 200:
            print("✅ Memory added successfully")
        else:
            print(f"❌ Add memory failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Add memory error: {e}")
    
    # Test getting compressed context
    print("\n7️⃣ Testing get compressed context...")
    try:
        response = requests.get(f"{base_url}/api/v1/game/{session_id}/context")
        if response.status_code == 200:
            print("✅ Compressed context retrieved")
            context = response.json()
            print(f"   Story length: {context['story_length']}")
            print(f"   Active promises: {len(context['active_promises'])}")
            print(f"   Key relationships: {len(context['key_relationships'])}")
        else:
            print(f"❌ Get compressed context failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get compressed context error: {e}")
    
    # Test saving game
    print("\n8️⃣ Testing save game...")
    try:
        save_data = {"save_name": "test_save"}
        response = requests.post(
            f"{base_url}/api/v1/game/{session_id}/save",
            json=save_data
        )
        
        if response.status_code == 200:
            print("✅ Game saved successfully")
        else:
            print(f"❌ Save game failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Save game error: {e}")
    
    # Test listing saves
    print("\n9️⃣ Testing list saves...")
    try:
        response = requests.get(f"{base_url}/api/v1/saves")
        if response.status_code == 200:
            print("✅ Saves listed successfully")
            saves = response.json()
            print(f"   Available saves: {saves['data']['saves']}")
        else:
            print(f"❌ List saves failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List saves error: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    print("⚠️  Make sure the API server is running on http://localhost:8000")
    print("   Run: python run_api.py")
    print("=" * 50)
    
    # Wait a moment for user to read
    time.sleep(2)
    
    test_api() 