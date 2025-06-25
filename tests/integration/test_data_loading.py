#!/usr/bin/env python3
"""
Test script to verify Kanto data loading.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.bethemc.data.vector_store import KantoKnowledgeBase
from src.bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_data_loading():
    """Test the data loading functionality."""
    logger.info("Testing Kanto data loading...")
    
    try:
        # Initialize knowledge base
        kb = KantoKnowledgeBase()
        
        # Test location info
        logger.info("Testing location info...")
        pallet_town = kb.get_location_info("pallet-town")
        print(f"Pallet Town info: {pallet_town}")
        
        # Test story context
        logger.info("Testing story context...")
        context = kb.get_story_context("Pokémon adventure in Kanto")
        print(f"Found {len(context)} relevant context items")
        
        # Test memory functionality
        logger.info("Testing memory functionality...")
        test_memory = {
            "memory_type": "promise",
            "content": "I promised to help Professor Oak with his research",
            "timestamp": 1234567890.0,
            "metadata": {"character": "Professor Oak"}
        }
        kb.add_memory(test_memory)
        
        # Test retrieving memories
        memories = kb.get_memories_by_type("promise")
        print(f"Found {len(memories)} promise memories")
        
        logger.info("Data loading test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in data loading test: {e}")
        raise

if __name__ == "__main__":
    test_data_loading() 