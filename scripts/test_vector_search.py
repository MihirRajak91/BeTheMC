#!/usr/bin/env python3
"""
Test script to demonstrate vector search capabilities with our enhanced Kanto data.
"""
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import json

def setup_search():
    """Setup Qdrant client and embedder for search."""
    client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return client, embedder

def search_kanto_knowledge(client, embedder, query, limit=5):
    """Search for relevant Kanto knowledge based on a query."""
    # Create query embedding
    query_vector = embedder.encode([query])[0].tolist()
    
    # Search in Qdrant
    results = client.search(
        collection_name="kanto_knowledge",
        query_vector=query_vector,
        limit=limit,
        with_payload=True
    )
    
    return results

def format_results(results):
    """Format search results for display."""
    formatted = []
    for i, result in enumerate(results, 1):
        payload = result.payload
        formatted.append(f"""
{i}. {payload.get('type', 'Unknown').title()}: {payload.get('name', 'Unknown')}
   Score: {result.score:.3f}
   Text: {payload.get('text', 'No description available')[:200]}...
        """.strip())
    
    return "\n\n".join(formatted)

def test_searches():
    """Test various search queries."""
    client, embedder = setup_search()
    
    # Test queries that an LLM might ask
    test_queries = [
        "Where can I find electric type Pokemon?",
        "Tell me about gym leaders and their personalities",
        "What items help in Pokemon battles?", 
        "Locations with rare Pokemon encounters",
        "Characters who are friendly and helpful",
        "Fire type Pokemon with strong personalities"
    ]
    
    print("🔍 Testing Vector Search for LLM Access")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🎯 Query: '{query}'")
        print("-" * 40)
        
        results = search_kanto_knowledge(client, embedder, query)
        if results:
            print(format_results(results))
        else:
            print("No results found.")
        
        print("\n" + "="*50)

def get_collection_stats():
    """Get statistics about the stored data."""
    client, _ = setup_search()
    
    # Get total count
    total_count = client.count(collection_name="kanto_knowledge", exact=True).count
    
    # Get counts by type
    type_counts = {}
    for data_type in ["location", "character", "item", "pokemon"]:
        count_result = client.count(
            collection_name="kanto_knowledge", 
            count_filter={
                "must": [{"key": "type", "match": {"value": data_type}}]
            },
            exact=True
        )
        type_counts[data_type] = count_result.count
    
    print("📊 Qdrant Collection Statistics")
    print("=" * 30)
    print(f"Total entries: {total_count}")
    print("\nBy type:")
    for data_type, count in type_counts.items():
        print(f"  {data_type.title()}: {count}")

if __name__ == "__main__":
    print("🚀 Enhanced Kanto Data - Vector Search Test")
    print("=" * 50)
    
    # Show statistics
    get_collection_stats()
    
    # Test searches
    test_searches()
    
    print("\n✅ Vector search test complete!")
    print("\nThis demonstrates how an LLM can:")
    print("• Find relevant Pokemon, locations, characters, and items")
    print("• Use semantic search (meaning-based, not just keyword matching)")
    print("• Get context for story generation")
    print("• Access all our enhanced data instantly") 