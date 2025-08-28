#!/usr/bin/env python3
"""
Test script to verify location data loading and search.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.data.vector_store import KantoKnowledgeBase
from bethemc_complex.utils.config import Config

def test_location_data():
    """Test location data loading and search."""
    print("🧪 Testing Location Data...")
    
    try:
        # Initialize knowledge base
        config = Config()
        kb = KantoKnowledgeBase(config)
        
        # Test Pallet Town location info
        print("\n📍 Testing Pallet Town location info...")
        pallet_info = kb.get_location_info("Pallet Town")
        print(f"Pallet Town info: {pallet_info}")
        
        # Test story context for Pallet Town
        print("\n📖 Testing story context for Pallet Town...")
        story_context = kb.get_story_context("Events in Pallet Town involving player journey")
        print(f"Story context items: {len(story_context)}")
        for i, context in enumerate(story_context[:3]):
            print(f"Context {i+1}: {context['content'][:100]}...")
        
        print("\n✅ Location data test completed!")
        
    except Exception as e:
        print(f"❌ Error testing location data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_location_data() 