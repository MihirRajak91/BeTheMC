#!/usr/bin/env python3
"""
🎮 BeTheMC - Simple Example

This script shows you exactly how to use the simplified BeTheMC API!
Run this after starting the API server to see a complete game session.

What this example does:
1. Starts a new game
2. Makes several choices
3. Shows how personality changes
4. Saves the game
5. Loads the game back
6. Shows the current state

Prerequisites:
- API server running on localhost:8000
- MongoDB running and connected
"""

import requests
import json
import time
from typing import Dict, Any


class BeTheMCExample:
    """Simple example client for the BeTheMC API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the example client."""
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.player_id = None
        self.player_name = "Ash"
        
        print("🎮 BeTheMC Simple Example")
        print("=" * 50)
        print(f"API Base URL: {self.api_base}")
        print()
    
    def check_api_health(self) -> bool:
        """Check if the API is running."""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API Health: {health_data.get('status', 'Unknown')}")
                print(f"✅ Database: {health_data.get('database', 'Unknown')}")
                return True
            else:
                print(f"❌ API not healthy: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure the server is running!")
            return False
    
    def start_new_game(self) -> Dict[str, Any]:
        """Start a new game and return the initial game state."""
        print(f"\n🚀 Starting new game for '{self.player_name}'...")
        
        # Make the API request
        response = requests.post(
            f"{self.api_base}/game/start",
            json={"player_name": self.player_name}
        )
        
        if response.status_code == 200:
            game_data = response.json()
            self.player_id = game_data["player_id"]
            
            print(f"✅ Game started! Player ID: {self.player_id}")
            print(f"📖 Story: {game_data['current_story']['title']}")
            print(f"📝 Content: {game_data['current_story']['content'][:100]}...")
            print(f"🧠 Starting personality: {game_data['personality_traits']}")
            print(f"⭐ Available choices: {len(game_data['available_choices'])}")
            
            # Show the choices
            for i, choice in enumerate(game_data['available_choices']):
                print(f"   {i+1}. {choice['text']} (Effects: {choice['effects']})")
            
            return game_data
        else:
            print(f"❌ Failed to start game: {response.status_code}")
            print(f"Error: {response.text}")
            return {}
    
    def make_choice(self, choice_index: int, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a choice and return the updated game state."""
        if not game_data or 'available_choices' not in game_data:
            print("❌ No game data or choices available")
            return {}
        
        if choice_index >= len(game_data['available_choices']):
            print(f"❌ Invalid choice index: {choice_index}")
            return {}
        
        chosen_choice = game_data['available_choices'][choice_index]
        print(f"\n⚡ Making choice: '{chosen_choice['text']}'")
        
        # Make the API request
        response = requests.post(
            f"{self.api_base}/game/choice",
            json={
                "player_id": self.player_id,
                "choice_id": chosen_choice["id"]
            }
        )
        
        if response.status_code == 200:
            updated_data = response.json()
            
            print(f"✅ Choice processed!")
            print(f"📖 New story: {updated_data['current_story']['title']}")
            print(f"📝 Content: {updated_data['current_story']['content'][:100]}...")
            print(f"⭐ New choices: {len(updated_data['available_choices'])}")
            
            # Show new choices
            for i, choice in enumerate(updated_data['available_choices']):
                print(f"   {i+1}. {choice['text']} (Effects: {choice['effects']})")
            
            return updated_data
        else:
            print(f"❌ Failed to make choice: {response.status_code}")
            print(f"Error: {response.text}")
            return {}
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current game state."""
        print(f"\n📋 Getting current game state...")
        
        response = requests.get(f"{self.api_base}/game/state/{self.player_id}")
        
        if response.status_code == 200:
            game_data = response.json()
            print(f"✅ Current state retrieved!")
            print(f"🧠 Current personality: {game_data['personality_traits']}")
            print(f"📍 Location: {game_data['game_progress']['current_location']}")
            print(f"📚 Completed events: {len(game_data['game_progress']['completed_events'])}")
            
            if game_data['game_progress']['completed_events']:
                print("   Recent events:")
                for event in game_data['game_progress']['completed_events'][-3:]:
                    print(f"   - {event}")
            
            return game_data
        else:
            print(f"❌ Failed to get current state: {response.status_code}")
            return {}
    
    def save_game(self, save_name: str) -> str:
        """Save the current game and return the save ID."""
        print(f"\n💾 Saving game as '{save_name}'...")
        
        response = requests.post(
            f"{self.api_base}/game/save",
            json={
                "player_id": self.player_id,
                "save_name": save_name
            }
        )
        
        if response.status_code == 200:
            save_data = response.json()
            save_id = save_data["save_id"]
            print(f"✅ Game saved! Save ID: {save_id}")
            print(f"📅 Timestamp: {save_data['timestamp']}")
            return save_id
        else:
            print(f"❌ Failed to save game: {response.status_code}")
            return ""
    
    def load_game(self, save_id: str) -> Dict[str, Any]:
        """Load a saved game."""
        print(f"\n📂 Loading game from save ID: {save_id}")
        
        response = requests.post(
            f"{self.api_base}/game/load",
            json={
                "player_id": self.player_id,
                "save_id": save_id
            }
        )
        
        if response.status_code == 200:
            game_data = response.json()
            print(f"✅ Game loaded successfully!")
            print(f"📖 Story: {game_data['current_story']['title']}")
            print(f"🧠 Personality: {game_data['personality_traits']}")
            return game_data
        else:
            print(f"❌ Failed to load game: {response.status_code}")
            return {}
    
    def list_saves(self) -> list:
        """List all saves for the current player."""
        print(f"\n📁 Listing all saves for player...")
        
        response = requests.get(f"{self.api_base}/game/saves/{self.player_id}")
        
        if response.status_code == 200:
            saves_data = response.json()
            saves = saves_data["saves"]
            print(f"✅ Found {len(saves)} save files:")
            
            for save in saves:
                print(f"   📄 {save['save_name']} (ID: {save['save_id'][:8]}...)")
                print(f"      Created: {save['created_at']}")
                print(f"      Location: {save['current_location']}")
            
            return saves
        else:
            print(f"❌ Failed to list saves: {response.status_code}")
            return []
    
    def run_complete_example(self):
        """Run a complete example session."""
        print("🎯 Running complete example session...")
        print("This will demonstrate all API functionality!\n")
        
        # Step 1: Check API health
        if not self.check_api_health():
            print("🛑 Cannot proceed - API is not available!")
            return
        
        time.sleep(1)
        
        # Step 2: Start a new game
        game_data = self.start_new_game()
        if not game_data:
            print("🛑 Cannot proceed - failed to start game!")
            return
        
        time.sleep(2)
        
        # Step 3: Make first choice (go to Oak's lab)
        game_data = self.make_choice(0, game_data)  # Choose first option
        if not game_data:
            print("🛑 Cannot proceed - failed to make choice!")
            return
        
        time.sleep(2)
        
        # Step 4: Make second choice (if available)
        if game_data and game_data.get('available_choices'):
            game_data = self.make_choice(1, game_data)  # Choose second option
            time.sleep(2)
        
        # Step 5: Get current state to see changes
        current_state = self.get_current_state()
        time.sleep(1)
        
        # Step 6: Save the game
        save_id = self.save_game("Example Session Save")
        if not save_id:
            print("⚠️ Save failed, but continuing...")
        time.sleep(1)
        
        # Step 7: List all saves
        saves = self.list_saves()
        time.sleep(1)
        
        # Step 8: Load the game back (if we have a save)
        if save_id:
            loaded_data = self.load_game(save_id)
            time.sleep(1)
        
        # Step 9: Final state check
        final_state = self.get_current_state()
        
        print("\n" + "=" * 50)
        print("🎉 Example completed successfully!")
        print("\nWhat we demonstrated:")
        print("✅ Health check")
        print("✅ Starting a new game")
        print("✅ Making choices that affect personality")
        print("✅ Getting current game state")
        print("✅ Saving the game")
        print("✅ Listing save files")
        print("✅ Loading a saved game")
        print("\n🎮 Your BeTheMC API is working perfectly!")
        
        if final_state:
            print(f"\n📊 Final Stats:")
            print(f"   Player: {final_state['player_name']}")
            print(f"   Personality: {final_state['personality_traits']}")
            print(f"   Events completed: {len(final_state['game_progress']['completed_events'])}")


def main():
    """Main function to run the example."""
    print("🎮 BeTheMC Simple API Example")
    print("=" * 50)
    print("This example will test all API endpoints and show you how to use them.")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Ask user if they want to proceed
    proceed = input("Ready to start the example? (y/n): ").lower().strip()
    if proceed != 'y':
        print("👋 Example cancelled. Run again when ready!")
        return
    
    # Run the example
    example = BeTheMCExample()
    example.run_complete_example()


if __name__ == "__main__":
    main()


# 🎯 SIMPLE USAGE INSTRUCTIONS:
#
# 1. Start your API server:
#    python main.py
#
# 2. Run this example:
#    python SIMPLE_EXAMPLE.py
#
# 3. Watch it demonstrate all API features!
#
# You can also use individual methods:
# example = BeTheMCExample()
# example.check_api_health()
# game_data = example.start_new_game()
# updated_data = example.make_choice(0, game_data)
# etc. 