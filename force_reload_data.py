#!/usr/bin/env python3
"""
Force reload the vector store data.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.data.vector_store import KantoKnowledgeBase
from bethemc_complex.utils.config import Config
from qdrant_client import QdrantClient

def force_reload_data():
    """Force reload the vector store data."""
    print("🔄 Force reloading vector store data...")
    
    try:
        # Get config
        config = Config()
        vector_store_config = config.get("vector_store")
        
        # Connect to Qdrant
        client = QdrantClient(
            host=vector_store_config.get("host", "localhost"), 
            port=vector_store_config.get("port", 6333)
        )
        
        # Delete existing collection
        collection_name = "kanto_knowledge"
        try:
            client.delete_collection(collection_name)
            print(f"✅ Deleted existing collection: {collection_name}")
        except Exception as e:
            print(f"Collection deletion failed (might not exist): {e}")
        
        # Create new knowledge base (this will reload data)
        print("🔄 Creating new knowledge base...")
        kb = KantoKnowledgeBase(config)
        
        # Check collection count
        count = client.count(collection_name=collection_name, exact=True).count
        print(f"✅ Loaded {count} knowledge items")
        
        # Test Pallet Town
        print("\n📍 Testing Pallet Town after reload...")
        pallet_info = kb.get_location_info("Pallet Town")
        print(f"Pallet Town info: {pallet_info}")
        
        print("\n✅ Force reload completed!")
        
    except Exception as e:
        print(f"❌ Error force reloading data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_reload_data() 