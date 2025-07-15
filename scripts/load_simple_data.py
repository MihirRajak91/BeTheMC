#!/usr/bin/env python3
"""
Simple script to load enhanced Kanto data into Qdrant.
"""
import sys
import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

def setup_qdrant():
    """Setup Qdrant client and collections."""
    client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Ensure kanto_knowledge collection exists
    collections = [c.name for c in client.get_collections().collections]
    if "kanto_knowledge" not in collections:
        client.create_collection(
            collection_name="kanto_knowledge",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print("Created kanto_knowledge collection")
    
    return client, embedder

def load_locations_data(client, embedder):
    """Load location data with encounters."""
    data_file = Path("data/raw/kanto/locations.json")
    if not data_file.exists():
        print(f"File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    points = []
    for location in locations:
        # Create simple text description
        text_parts = [
            f"Location: {location.get('name', 'Unknown')}",
            f"Description: {location.get('description', '')}"
        ]
        
        # Handle encounters
        encounters = location.get('encounters', {})
        if encounters:
            if isinstance(encounters, dict):
                encounter_text = []
                for rarity, pokemon_list in encounters.items():
                    if pokemon_list:
                        encounter_text.append(f"{rarity}: {', '.join(pokemon_list)}")
                if encounter_text:
                    text_parts.append(f"Pokemon Encounters: {'; '.join(encounter_text)}")
            elif isinstance(encounters, list):
                text_parts.append(f"Pokemon Encounters: {', '.join(encounters)}")
        
        # Add climate if available
        if 'climate' in location and isinstance(location['climate'], dict):
            climate_desc = location['climate'].get('description', '')
            if climate_desc:
                text_parts.append(f"Climate: {climate_desc}")
        
        location_text = "\n".join(text_parts)
        
        # Create embedding
        embedding = embedder.encode([location_text])[0].tolist()
        
        # Create point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "location",
                "name": location.get('name', ''),
                "id": location.get('id', ''),
                "has_encounters": bool(encounters),
                "text": location_text
            }
        )
        points.append(point)
    
    # Upload to Qdrant
    if points:
        client.upsert(collection_name="kanto_knowledge", points=points)
        print(f"Loaded {len(points)} locations")

def load_characters_data(client, embedder):
    """Load character data."""
    data_file = Path("data/raw/kanto/characters.json")
    if not data_file.exists():
        print(f"File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        characters = json.load(f)
    
    points = []
    for character in characters:
        # Create simple text description
        text_parts = [
            f"Character: {character.get('name', 'Unknown')}",
            f"Role: {character.get('role', '')}",
            f"Description: {character.get('description', '')}"
        ]
        
        # Handle personality
        personality = character.get('personality', {})
        if isinstance(personality, dict):
            if 'core_traits' in personality:
                text_parts.append(f"Personality Traits: {', '.join(personality['core_traits'])}")
            if 'temperament' in personality:
                text_parts.append(f"Temperament: {personality['temperament']}")
        elif isinstance(personality, str):
            text_parts.append(f"Personality: {personality}")
        
        character_text = "\n".join(text_parts)
        
        # Create embedding
        embedding = embedder.encode([character_text])[0].tolist()
        
        # Create point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "character",
                "name": character.get('name', ''),
                "id": character.get('id', ''),
                "role": character.get('role', ''),
                "text": character_text
            }
        )
        points.append(point)
    
    # Upload to Qdrant
    if points:
        client.upsert(collection_name="kanto_knowledge", points=points)
        print(f"Loaded {len(points)} characters")

def load_items_data(client, embedder):
    """Load items data."""
    data_file = Path("data/raw/kanto/items.json")
    if not data_file.exists():
        print(f"File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        items_data = json.load(f)
    
    points = []
    for category in items_data:
        if category.get('_comment'):
            continue
        
        category_name = category.get('category', 'unknown')
        items = category.get('items', [])
        
        for item in items:
            text_parts = [
                f"Item: {item.get('name', 'Unknown')}",
                f"Category: {category_name}",
                f"Description: {item.get('description', '')}",
                f"Effect: {item.get('effect', '')}"
            ]
            
            if 'anime_description' in item:
                text_parts.append(f"Anime Description: {item['anime_description']}")
            
            item_text = "\n".join(text_parts)
            
            # Create embedding
            embedding = embedder.encode([item_text])[0].tolist()
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "type": "item",
                    "name": item.get('name', ''),
                    "category": category_name,
                    "rarity": item.get('rarity', ''),
                    "text": item_text
                }
            )
            points.append(point)
    
    # Upload to Qdrant
    if points:
        client.upsert(collection_name="kanto_knowledge", points=points)
        print(f"Loaded {len(points)} items")

def load_pokemon_data(client, embedder):
    """Load Pokemon with personality data."""
    data_file = Path("data/raw/kanto/pokemon.json")
    if not data_file.exists():
        print(f"File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        pokemon_data = json.load(f)
    
    points = []
    for pokemon in pokemon_data:
        # Only process Pokemon with anime personality
        if 'anime_personality' not in pokemon:
            continue
        
        personality = pokemon['anime_personality']
        
        text_parts = [
            f"Pokemon: {pokemon.get('display_name', 'Unknown')}",
            f"Types: {', '.join(pokemon.get('types', []))}"
        ]
        
        if 'core_traits' in personality:
            text_parts.append(f"Personality: {', '.join(personality['core_traits'])}")
        
        if 'temperament' in personality:
            text_parts.append(f"Temperament: {personality['temperament']}")
        
        if 'behavioral_notes' in personality:
            text_parts.append(f"Behavior: {personality['behavioral_notes']}")
        
        pokemon_text = "\n".join(text_parts)
        
        # Create embedding
        embedding = embedder.encode([pokemon_text])[0].tolist()
        
        # Create point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "pokemon",
                "name": pokemon.get('name', ''),
                "display_name": pokemon.get('display_name', ''),
                "types": pokemon.get('types', []),
                "has_personality": True,
                "text": pokemon_text
            }
        )
        points.append(point)
    
    # Upload to Qdrant
    if points:
        client.upsert(collection_name="kanto_knowledge", points=points)
        print(f"Loaded {len(points)} Pokemon with personalities")

def main():
    """Main function to load all data."""
    print("Setting up Qdrant connection...")
    client, embedder = setup_qdrant()
    
    print("Loading enhanced Kanto data...")
    load_locations_data(client, embedder)
    load_characters_data(client, embedder)
    load_items_data(client, embedder)
    load_pokemon_data(client, embedder)
    
    # Get final count
    total_count = client.count(collection_name="kanto_knowledge", exact=True).count
    print(f"\nData loading complete! Total entries in kanto_knowledge: {total_count}")

if __name__ == "__main__":
    main() 