#!/usr/bin/env python3
"""
Debug script to see what's in the vector store.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.data.vector_store import KantoKnowledgeBase
from bethemc_complex.utils.config import Config
from qdrant_client import QdrantClient

def debug_vector_store():
    """Debug what's in the vector store."""
    print("🔍 Debugging vector store contents...")
    
    try:
        # Get config
        config = Config()
        vector_store_config = config.get("vector_store")
        
        # Connect to Qdrant
        client = QdrantClient(
            host=vector_store_config.get("host", "localhost"), 
            port=vector_store_config.get("port", 6333)
        )
        
        # Get all documents
        collection_name = "kanto_knowledge"
        all_points = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        print(f"\n📊 Found {len(all_points[0])} documents in vector store")
        
        # Show location documents
        location_docs = []
        pokemon_docs = []
        character_docs = []
        story_docs = []
        
        for point in all_points[0]:
            payload = point.payload
            doc_type = payload.get("type", "unknown")
            doc_name = payload.get("name", "unknown")
            
            if doc_type == "location":
                location_docs.append(doc_name)
            elif doc_type == "pokemon":
                pokemon_docs.append(doc_name)
            elif doc_type == "character":
                character_docs.append(doc_name)
            elif doc_type == "story_element":
                story_docs.append(doc_name)
        
        print(f"\n📍 Location documents ({len(location_docs)}):")
        for i, loc in enumerate(location_docs[:10]):
            print(f"  {i+1}. {loc}")
            
        print(f"\n🐛 Pokémon documents ({len(pokemon_docs)}):")
        for i, pokemon in enumerate(pokemon_docs[:10]):
            print(f"  {i+1}. {pokemon}")
            
        print(f"\n👤 Character documents ({len(character_docs)}):")
        for i, char in enumerate(character_docs[:10]):
            print(f"  {i+1}. {char}")
            
        print(f"\n📖 Story documents ({len(story_docs)}):")
        for i, story in enumerate(story_docs[:10]):
            print(f"  {i+1}. {story}")
        
        # Show all document types
        print(f"\n📊 Document type breakdown:")
        type_counts = {}
        for point in all_points[0]:
            payload = point.payload
            doc_type = payload.get("type", "unknown")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        for doc_type, count in type_counts.items():
            print(f"  {doc_type}: {count}")
        
        # Search for Pallet Town specifically
        print(f"\n🔍 Searching for 'pallet'...")
        search_results = client.search(
            collection_name=collection_name,
            query_vector=[0.1] * 384,  # Dummy vector
            limit=10,
            query_filter={"type": "location"}
        )
        
        print(f"Search returned {len(search_results)} results")
        for result in search_results:
            payload = result.payload
            print(f"  - {payload.get('name', 'unknown')} (score: {result.score})")
        
    except Exception as e:
        print(f"❌ Error debugging vector store: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vector_store() 