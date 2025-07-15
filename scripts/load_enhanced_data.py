#!/usr/bin/env python3
"""
Script to load enhanced Kanto data into Qdrant vector store.
This script loads all the enhanced data we created into the existing Qdrant setup.
"""
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Batch
from sentence_transformers import SentenceTransformer
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EnhancedDataLoader:
    """Load enhanced Kanto data into Qdrant for LLM access."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.client = QdrantClient(host="localhost", port=6333)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.data_dir = Path("data/raw/kanto")
        
        # Collection configurations
        self.collections = {
            "kanto_knowledge": {
                "vector_size": 384,
                "distance": Distance.COSINE
            },
            "story_elements": {
                "vector_size": 384, 
                "distance": Distance.COSINE
            },
            "character_personalities": {
                "vector_size": 384,
                "distance": Distance.COSINE
            }
        }
    
    def setup_collections(self):
        """Create collections if they don't exist."""
        existing_collections = [c.name for c in self.client.get_collections().collections]
        
        for collection_name, config in self.collections.items():
            if collection_name not in existing_collections:
                logger.info(f"Creating collection: {collection_name}")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=config["vector_size"],
                        distance=config["distance"]
                    )
                )
            else:
                logger.info(f"Collection {collection_name} already exists")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        return self.embedder.encode(texts).tolist()
    
    def load_locations_data(self):
        """Load enhanced locations data with rarity encounters."""
        logger.info("Loading locations data...")
        locations_file = self.data_dir / "locations.json"
        
        if not locations_file.exists():
            logger.warning(f"Locations file not found: {locations_file}")
            return
        
        with open(locations_file, 'r', encoding='utf-8') as f:
            locations_data = json.load(f)
        
        points = []
        texts = []
        
        for location in locations_data:
            # Create rich text for embedding
            location_text = f"""
            Location: {location.get('name', 'Unknown')}
            Description: {location.get('description', '')}
            Climate: {location.get('climate', {}).get('description', '')}
            Culture: {location.get('cultural_significance', '')}
            Encounters: {self._format_encounters(location.get('encounters', {}))}
            Story Events: {'; '.join(location.get('story_events', []))}
            Trainers: {'; '.join([t.get('name', '') for t in location.get('trainers', [])])}
            Atmosphere: {location.get('atmosphere', {}).get('mood', '')}
            """.strip()
            
            texts.append(location_text)
            
            metadata = {
                "type": "location",
                "location_id": location.get('id', ''),
                "name": location.get('name', ''),
                "region": "kanto",
                "has_encounters": bool(location.get('encounters')),
                "has_gym": bool(location.get('gym')),
                "story_significance": len(location.get('story_events', []))
            }
            
            points.append({
                "text": location_text,
                "metadata": metadata
            })
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create Qdrant points
        qdrant_points = []
        for i, (point, embedding) in enumerate(zip(points, embeddings)):
            qdrant_points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=point["metadata"]
            ))
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name="kanto_knowledge",
            points=qdrant_points
        )
        
        logger.info(f"Loaded {len(qdrant_points)} location entries")
    
    def load_characters_data(self):
        """Load enhanced character data with deep personalities."""
        logger.info("Loading characters data...")
        characters_file = self.data_dir / "characters.json"
        
        if not characters_file.exists():
            logger.warning(f"Characters file not found: {characters_file}")
            return
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            characters_data = json.load(f)
        
        points = []
        texts = []
        
        for character in characters_data:
            # Create rich text for embedding
            character_text = f"""
            Character: {character.get('name', 'Unknown')}
            Role: {character.get('role', '')}
            Description: {character.get('description', '')}
            Personality: {self._format_personality(character.get('personality', {}))}
            Relationships: {self._format_relationships(character.get('relationships', {}))}
            Pokemon Specialty: {character.get('pokemon_specialty', '')}
            Battle Style: {character.get('battle_style', '')}
            Character Arc: {character.get('character_arc', '')}
            Quotes: {'; '.join(character.get('famous_quotes', []))}
            """.strip()
            
            texts.append(character_text)
            
            metadata = {
                "type": "character",
                "character_id": character.get('id', ''),
                "name": character.get('name', ''),
                "role": character.get('role', ''),
                "age": character.get('age', 0),
                "location": character.get('location', ''),
                "has_deep_personality": bool(character.get('personality', {}).get('core_traits')),
                "has_relationships": bool(character.get('relationships', {}))
            }
            
            points.append({
                "text": character_text,
                "metadata": metadata
            })
        
        # Create embeddings and upload
        embeddings = self.create_embeddings(texts)
        qdrant_points = []
        for i, (point, embedding) in enumerate(zip(points, embeddings)):
            qdrant_points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=point["metadata"]
            ))
        
        self.client.upsert(
            collection_name="character_personalities",
            points=qdrant_points
        )
        
        logger.info(f"Loaded {len(qdrant_points)} character entries")
    
    def load_pokemon_personalities(self):
        """Load Pokémon with anime-style personalities."""
        logger.info("Loading Pokémon personality data...")
        pokemon_file = self.data_dir / "pokemon.json"
        
        if not pokemon_file.exists():
            logger.warning(f"Pokemon file not found: {pokemon_file}")
            return
        
        with open(pokemon_file, 'r', encoding='utf-8') as f:
            pokemon_data = json.load(f)
        
        points = []
        texts = []
        
        for pokemon in pokemon_data:
            # Only process Pokémon with anime personality data
            if 'anime_personality' not in pokemon:
                continue
                
            personality = pokemon['anime_personality']
            
            # Create rich text for embedding
            pokemon_text = f"""
            Pokémon: {pokemon.get('display_name', 'Unknown')}
            Types: {', '.join(pokemon.get('types', []))}
            Personality: {', '.join(personality.get('core_traits', []))}
            Temperament: {personality.get('temperament', '')}
            Behavior: {personality.get('behavioral_notes', '')}
            Battle Style: {personality.get('battle_style', '')}
            Social Behavior: {personality.get('social_behavior', '')}
            Habitat: {personality.get('habitat_preferences', '')}
            Likes: {'; '.join(personality.get('favorite_activities', []))}
            Dislikes: {'; '.join(personality.get('dislikes', []))}
            Voice: {personality.get('voice_characteristics', '')}
            """.strip()
            
            texts.append(pokemon_text)
            
            metadata = {
                "type": "pokemon",
                "pokemon_id": pokemon.get('id', 0),
                "name": pokemon.get('name', ''),
                "display_name": pokemon.get('display_name', ''),
                "types": pokemon.get('types', []),
                "has_personality": True,
                "temperament": personality.get('temperament', ''),
                "core_traits": personality.get('core_traits', [])
            }
            
            points.append({
                "text": pokemon_text,
                "metadata": metadata
            })
        
        if not points:
            logger.warning("No Pokémon with personality data found")
            return
        
        # Create embeddings and upload
        embeddings = self.create_embeddings(texts)
        qdrant_points = []
        for i, (point, embedding) in enumerate(zip(points, embeddings)):
            qdrant_points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=point["metadata"]
            ))
        
        self.client.upsert(
            collection_name="kanto_knowledge",
            points=qdrant_points
        )
        
        logger.info(f"Loaded {len(qdrant_points)} Pokémon personality entries")
    
    def load_story_elements(self):
        """Load enhanced story elements and frameworks."""
        logger.info("Loading story elements...")
        story_file = self.data_dir / "story_elements.json"
        
        if not story_file.exists():
            logger.warning(f"Story elements file not found: {story_file}")
            return
        
        with open(story_file, 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        
        points = []
        texts = []
        
        for story_element in story_data:
            if story_element.get('_comment'):
                continue  # Skip comments
                
            # Create rich text for embedding
            story_text = f"""
            Story Type: {story_element.get('story_type', story_element.get('name', 'Unknown'))}
            Title: {story_element.get('title', '')}
            Description: {story_element.get('description', '')}
            Themes: {'; '.join(story_element.get('anime_themes', []))}
            Characters: {'; '.join(story_element.get('key_characters', []))}
            Setting: {story_element.get('setting', '')}
            Stakes: {story_element.get('emotional_stakes', '')}
            Story Hooks: {'; '.join(story_element.get('story_hooks', []))}
            Outcomes: {'; '.join(story_element.get('possible_outcomes', []))}
            """.strip()
            
            texts.append(story_text)
            
            metadata = {
                "type": "story_element",
                "story_type": story_element.get('story_type', story_element.get('name', '')),
                "title": story_element.get('title', ''),
                "themes": story_element.get('anime_themes', []),
                "complexity": len(story_element.get('story_hooks', [])),
                "has_character_development": bool(story_element.get('character_development')),
                "plot_type": story_element.get('type', 'unknown')
            }
            
            points.append({
                "text": story_text,
                "metadata": metadata
            })
        
        # Create embeddings and upload
        embeddings = self.create_embeddings(texts)
        qdrant_points = []
        for i, (point, embedding) in enumerate(zip(points, embeddings)):
            qdrant_points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=point["metadata"]
            ))
        
        self.client.upsert(
            collection_name="story_elements",
            points=qdrant_points
        )
        
        logger.info(f"Loaded {len(qdrant_points)} story element entries")
    
    def load_items_and_mechanics(self):
        """Load items and battle mechanics data."""
        logger.info("Loading items and battle mechanics...")
        
        # Load items
        items_file = self.data_dir / "items.json"
        if items_file.exists():
            with open(items_file, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
            self._process_items(items_data)
        
        # Load battle mechanics
        battle_file = self.data_dir / "battle_mechanics.json"
        if battle_file.exists():
            with open(battle_file, 'r', encoding='utf-8') as f:
                battle_data = json.load(f)
            self._process_battle_mechanics(battle_data)
        
        # Load seasonal calendar
        calendar_file = self.data_dir / "seasonal_calendar.json"
        if calendar_file.exists():
            with open(calendar_file, 'r', encoding='utf-8') as f:
                calendar_data = json.load(f)
            self._process_seasonal_calendar(calendar_data)
    
    def _process_items(self, items_data):
        """Process items data for vector storage."""
        points = []
        texts = []
        
        for category in items_data:
            if category.get('_comment'):
                continue
                
            category_name = category.get('category', 'unknown')
            items = category.get('items', [])
            
            for item in items:
                item_text = f"""
                Item: {item.get('name', 'Unknown')}
                Category: {category_name}
                Description: {item.get('description', '')}
                Anime Description: {item.get('anime_description', '')}
                Effect: {item.get('effect', '')}
                Rarity: {item.get('rarity', '')}
                Cultural Significance: {item.get('cultural_significance', '')}
                Usage Tips: {item.get('usage_tips', '')}
                Philosophy: {item.get('capture_philosophy', item.get('philosophy', ''))}
                """.strip()
                
                texts.append(item_text)
                
                metadata = {
                    "type": "item",
                    "item_id": item.get('id', ''),
                    "name": item.get('name', ''),
                    "category": category_name,
                    "rarity": item.get('rarity', ''),
                    "cost": item.get('cost', 0) if isinstance(item.get('cost'), int) else 0
                }
                
                points.append({
                    "text": item_text,
                    "metadata": metadata
                })
        
        if points:
            embeddings = self.create_embeddings(texts)
            qdrant_points = []
            for i, (point, embedding) in enumerate(zip(points, embeddings)):
                qdrant_points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=point["metadata"]
                ))
            
            self.client.upsert(
                collection_name="kanto_knowledge",
                points=qdrant_points
            )
            
            logger.info(f"Loaded {len(qdrant_points)} item entries")
    
    def _process_battle_mechanics(self, battle_data):
        """Process battle mechanics for vector storage."""
        points = []
        texts = []
        
        for category in battle_data:
            if category.get('_comment'):
                continue
                
            category_name = category.get('category', 'unknown')
            mechanics = category.get('mechanics', [])
            
            for mechanic in mechanics:
                mechanic_text = f"""
                Battle Mechanic: {mechanic.get('name', 'Unknown')}
                Category: {category_name}
                Description: {mechanic.get('description', '')}
                Anime Description: {mechanic.get('anime_description', '')}
                Trigger Conditions: {'; '.join(mechanic.get('trigger_conditions', []))}
                Effects: {'; '.join(mechanic.get('effects', []))}
                Examples: {'; '.join(mechanic.get('anime_examples', []))}
                """.strip()
                
                texts.append(mechanic_text)
                
                metadata = {
                    "type": "battle_mechanic",
                    "mechanic_id": mechanic.get('id', ''),
                    "name": mechanic.get('name', ''),
                    "category": category_name,
                    "has_examples": bool(mechanic.get('anime_examples'))
                }
                
                points.append({
                    "text": mechanic_text,
                    "metadata": metadata
                })
        
        if points:
            embeddings = self.create_embeddings(texts)
            qdrant_points = []
            for i, (point, embedding) in enumerate(zip(points, embeddings)):
                qdrant_points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=point["metadata"]
                ))
            
            self.client.upsert(
                collection_name="kanto_knowledge",
                points=qdrant_points
            )
            
            logger.info(f"Loaded {len(qdrant_points)} battle mechanic entries")
    
    def _process_seasonal_calendar(self, calendar_data):
        """Process seasonal calendar for vector storage."""
        points = []
        texts = []
        
        for season_data in calendar_data:
            if season_data.get('_comment'):
                continue
                
            season = season_data.get('season', 'unknown')
            events = season_data.get('events', [])
            
            for event in events:
                event_text = f"""
                Event: {event.get('name', 'Unknown')}
                Season: {season}
                Month: {event.get('month', '')}
                Location: {event.get('location', '')}
                Description: {event.get('description', '')}
                Anime Description: {event.get('anime_description', '')}
                Activities: {'; '.join(event.get('activities', []))}
                Special Encounters: {'; '.join(event.get('special_encounters', []))}
                Cultural Significance: {event.get('cultural_significance', '')}
                """.strip()
                
                texts.append(event_text)
                
                metadata = {
                    "type": "seasonal_event",
                    "event_id": event.get('id', ''),
                    "name": event.get('name', ''),
                    "season": season,
                    "month": event.get('month', ''),
                    "location": event.get('location', ''),
                    "duration": event.get('duration', '')
                }
                
                points.append({
                    "text": event_text,
                    "metadata": metadata
                })
        
        if points:
            embeddings = self.create_embeddings(texts)
            qdrant_points = []
            for i, (point, embedding) in enumerate(zip(points, embeddings)):
                qdrant_points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=point["metadata"]
                ))
            
            self.client.upsert(
                collection_name="kanto_knowledge",
                points=qdrant_points
            )
            
            logger.info(f"Loaded {len(qdrant_points)} seasonal event entries")
    
    def _format_encounters(self, encounters: Dict) -> str:
        """Format encounter data for text embedding."""
        if not encounters:
            return ""
        
        if isinstance(encounters, list):
            return ", ".join(encounters)
        
        formatted = []
        for rarity, pokemon_list in encounters.items():
            if pokemon_list:
                formatted.append(f"{rarity}: {', '.join(pokemon_list)}")
        
        return "; ".join(formatted)
    
    def _format_personality(self, personality: Dict) -> str:
        """Format personality data for text embedding."""
        if not personality:
            return ""
        
        if isinstance(personality, str):
            return personality
        
        parts = []
        if 'core_traits' in personality:
            parts.append(f"Traits: {', '.join(personality['core_traits'])}")
        if 'temperament' in personality:
            parts.append(f"Temperament: {personality['temperament']}")
        if 'fears' in personality:
            parts.append(f"Fears: {', '.join(personality['fears'])}")
        if 'motivations' in personality:
            parts.append(f"Motivations: {', '.join(personality['motivations'])}")
        
        return "; ".join(parts)
    
    def _format_relationships(self, relationships: Dict) -> str:
        """Format relationship data for text embedding."""
        if not relationships:
            return ""
        
        parts = []
        for rel_type, people in relationships.items():
            if people:
                if isinstance(people, list):
                    parts.append(f"{rel_type}: {', '.join(people)}")
                else:
                    parts.append(f"{rel_type}: {people}")
        
        return "; ".join(parts)
    
    def get_collection_stats(self):
        """Get statistics about loaded collections."""
        stats = {}
        for collection_name in self.collections.keys():
            try:
                count = self.client.count(collection_name=collection_name, exact=True).count
                stats[collection_name] = count
            except Exception as e:
                stats[collection_name] = f"Error: {e}"
        
        return stats
    
    def run(self):
        """Run the complete data loading process."""
        logger.info("Starting enhanced data loading process...")
        
        try:
            # Setup collections
            self.setup_collections()
            
            # Load all data types
            self.load_locations_data()
            self.load_characters_data()
            self.load_pokemon_personalities()
            self.load_story_elements()
            self.load_items_and_mechanics()
            
            # Print statistics
            stats = self.get_collection_stats()
            logger.info("Data loading completed! Collection statistics:")
            for collection, count in stats.items():
                logger.info(f"  {collection}: {count} entries")
            
        except Exception as e:
            logger.error(f"Error during data loading: {e}")
            raise

def main():
    """Main entry point."""
    loader = EnhancedDataLoader()
    loader.run()

if __name__ == "__main__":
    main() 