#!/usr/bin/env python3
"""
Test script for the modular BeTheMC API.
"""
import asyncio
import json
from src.bethemc.services.game_service import GameService
from src.bethemc.services.save_service import SaveService
from src.bethemc.api.game_manager import GameManager
from src.bethemc.utils.logger import get_logger
from src.bethemc.ai.story_generator import StoryGenerator

logger = get_logger(__name__)

class DummyKnowledgeBase:
    def add_memory(self, memory):
        pass

class DummyProgressionTracker:
    def __init__(self):
        self.current_location = "Pallet Town"
        self.completed_events = []
        self.relationships = {}
        self.inventory = []

    def add_scene(self, scene):
        pass
    def get_compressed_context(self, location):
        return {}
    def get_story_context(self):
        return {}

async def test_modular_api():
    """Test the modular API components."""
    try:
        # Initialize services and dependencies
        story_generator = StoryGenerator()
        knowledge_base = DummyKnowledgeBase()
        progression_tracker = DummyProgressionTracker()
        save_service = SaveService()
        game_service = GameService(
            story_generator=story_generator,
            knowledge_base=knowledge_base,
            progression_tracker=progression_tracker,
            save_manager=save_service
        )
        game_manager = GameManager(game_service, save_service)
        
        logger.info("✅ Services initialized successfully")
        
        # Test starting a new game
        logger.info("Testing game start...")
        game_response = await game_manager.start_game(
            player_name="TestPlayer",
            personality_traits={"friendship": 7, "courage": 8, "curiosity": 6}
        )
        
        logger.info(f"✅ Game started for player: {game_response.player_name}")
        logger.info(f"   Player ID: {game_response.player_id}")
        logger.info(f"   Story: {game_response.current_story['title']}")
        logger.info(f"   Choices: {len(game_response.available_choices)}")
        
        # Test making a choice
        if game_response.available_choices:
            choice_id = game_response.available_choices[0]['id']
            logger.info(f"Testing choice: {choice_id}")
            
            choice_response = await game_manager.make_choice(
                game_response.player_id, 
                choice_id
            )
            
            logger.info(f"✅ Choice processed successfully")
            logger.info(f"   New story: {choice_response.current_story['title']}")
            logger.info(f"   New choices: {len(choice_response.available_choices)}")
        
        # Test saving game
        logger.info("Testing game save...")
        save_result = await game_manager.save_game(
            game_response.player_id, 
            "test_save"
        )
        
        logger.info(f"✅ Game saved successfully: {save_result['save_id']}")
        
        # Test getting saves
        logger.info("Testing get saves...")
        saves_result = await game_manager.get_saves(game_response.player_id)
        
        logger.info(f"✅ Saves retrieved: {len(saves_result['saves'])} saves")
        
        # Test adding memory
        logger.info("Testing memory addition...")
        memory_result = await game_manager.add_memory(
            game_response.player_id,
            "I met Professor Oak and received my first Pokémon!",
            "milestone"
        )
        
        logger.info(f"✅ Memory added successfully")
        logger.info(f"   Total memories: {len(memory_result['memories'])}")
        
        # Test updating personality
        logger.info("Testing personality update...")
        personality_result = await game_manager.update_personality(
            game_response.player_id,
            "courage",
            9
        )
        
        logger.info(f"✅ Personality updated successfully")
        logger.info(f"   Courage: {personality_result['personality_traits']['courage']}")
        
        logger.info("🎉 All modular API tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_modular_api()) 