#!/usr/bin/env python3
"""
Sample story generator using our enhanced Kanto data.
Demonstrates how the LLM can access and use our comprehensive data.
"""
import sys
from pathlib import Path
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_story_generation():
    """Setup components for story generation."""
    client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return client, embedder

def get_relevant_context(client, embedder, query, limit=3):
    """Get relevant context from our enhanced data."""
    query_vector = embedder.encode([query])[0].tolist()
    
    results = client.search(
        collection_name="kanto_knowledge",
        query_vector=query_vector,
        limit=limit,
        with_payload=True
    )
    
    context = []
    for result in results:
        payload = result.payload
        context.append({
            "type": payload.get("type", "unknown"),
            "name": payload.get("name", "Unknown"),
            "description": payload.get("text", ""),
            "relevance_score": result.score
        })
    
    return context

def generate_story_prompt(context, story_type="adventure"):
    """Generate a story prompt using our enhanced data."""
    
    # Build context description
    context_desc = []
    for item in context:
        context_desc.append(f"{item['type'].title()}: {item['name']} - {item['description'][:150]}...")
    
    context_text = "\n".join(context_desc)
    
    # Create story prompt
    if story_type == "adventure":
        prompt = f"""
You are creating an anime-style Pokémon adventure story in the Kanto region. 
Use this rich context from the world:

{context_text}

Create a compelling scene that incorporates these elements naturally. Focus on:
- Character personalities and relationships
- Pokémon with distinct personalities
- Emotional moments and growth
- Anime-style dialogue and atmosphere
- Environmental details and atmosphere

Write a 2-3 paragraph scene that feels like it belongs in a Pokémon anime episode.
"""
    
    elif story_type == "character_development":
        prompt = f"""
You are writing a character development scene in the Pokémon anime style.
Use this character and location context:

{context_text}

Focus on:
- Deep character emotions and motivations
- Personal growth and learning
- Relationships between characters and Pokémon
- Anime-style emotional storytelling
- Meaningful dialogue and introspection

Write a scene that shows character growth and emotional depth.
"""
    
    elif story_type == "pokemon_encounter":
        prompt = f"""
You are writing a Pokémon encounter scene in anime style.
Use this location and Pokémon context:

{context_text}

Focus on:
- The unique personality of the Pokémon
- The trainer's approach and respect
- Environmental atmosphere and mood
- Anime-style encounter dynamics
- Emotional connection and understanding

Write a scene that captures the magic of meeting a new Pokémon.
"""
    
    return prompt

def demonstrate_story_generation():
    """Demonstrate story generation with our enhanced data."""
    client, embedder = setup_story_generation()
    
    print("🎬 Enhanced Kanto Story Generation Demo")
    print("=" * 50)
    
    # Demo 1: Adventure Story
    print("\n🌟 Demo 1: Adventure Story")
    print("-" * 30)
    adventure_context = get_relevant_context(
        client, embedder, 
        "Pikachu and trainer exploring new location with rare Pokemon encounters"
    )
    adventure_prompt = generate_story_prompt(adventure_context, "adventure")
    print("Context Retrieved:")
    for item in adventure_context:
        print(f"  • {item['type'].title()}: {item['name']} (Score: {item['relevance_score']:.3f})")
    print(f"\nStory Prompt Generated ({len(adventure_prompt)} characters)")
    print("Ready for LLM processing!")
    
    # Demo 2: Character Development
    print("\n🌟 Demo 2: Character Development")
    print("-" * 30)
    character_context = get_relevant_context(
        client, embedder,
        "Brock gym leader personality caring nurturing trainer"
    )
    character_prompt = generate_story_prompt(character_context, "character_development")
    print("Context Retrieved:")
    for item in character_context:
        print(f"  • {item['type'].title()}: {item['name']} (Score: {item['relevance_score']:.3f})")
    print(f"\nStory Prompt Generated ({len(character_prompt)} characters)")
    print("Ready for LLM processing!")
    
    # Demo 3: Pokémon Encounter
    print("\n🌟 Demo 3: Pokémon Encounter")
    print("-" * 30)
    pokemon_context = get_relevant_context(
        client, embedder,
        "Charizard proud powerful independent personality"
    )
    pokemon_prompt = generate_story_prompt(pokemon_context, "pokemon_encounter")
    print("Context Retrieved:")
    for item in pokemon_context:
        print(f"  • {item['type'].title()}: {item['name']} (Score: {item['relevance_score']:.3f})")
    print(f"\nStory Prompt Generated ({len(pokemon_prompt)} characters)")
    print("Ready for LLM processing!")
    
    print("\n✅ Story generation demo complete!")
    print("\nThis demonstrates how our enhanced data enables:")
    print("• Semantic context retrieval")
    print("• Rich, anime-style storytelling")
    print("• Character-driven narratives")
    print("• Dynamic world building")

if __name__ == "__main__":
    demonstrate_story_generation() 