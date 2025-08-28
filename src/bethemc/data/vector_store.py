"""
Vector store for Kanto knowledge and story context.
"""
from typing import List, Dict, Any
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..ai.providers import get_embedder_provider
import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from datetime import datetime
import calendar

logger = setup_logger(__name__)

class VectorStore:
    """
    Simple vector store wrapper for the Kanto knowledge base.
    """
    def __init__(self, config=None):
        """Initialize the vector store."""
        self.knowledge_base = KantoKnowledgeBase(config)
    
    def initialize_collections(self):
        """Initialize vector store collections."""
        # This is handled by KantoKnowledgeBase
        pass
    
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get location information."""
        return self.knowledge_base.get_location_info(location)
    
    def get_story_context(self, query: str) -> List[Dict[str, Any]]:
        """Get story context."""
        return self.knowledge_base.get_story_context(query)


class KantoKnowledgeBase:
    def __init__(self, config=None):
        """Initialize the Kanto knowledge base."""
        self.config = config if config is not None else Config()
        # Support both Config object and dict
        if hasattr(self.config, '__class__') and 'Config' in self.config.__class__.__name__:
            embedder_config = self.config.get("ai.embedder")
        else:
            try:
                embedder_config = self.config["ai"]["embedder"]
            except Exception as e:
                import pprint
                print("[KantoKnowledgeBase] ERROR: Could not find 'ai.embedder' in config. Config structure:")
                pprint.pprint(self.config)
                raise ValueError("Missing 'ai.embedder' configuration in config.") from e
        if embedder_config is None:
            import pprint
            print("[KantoKnowledgeBase] ERROR: Could not find 'ai.embedder' in config. Config structure:")
            pprint.pprint(self.config)
            raise ValueError("Missing 'ai.embedder' configuration in config.")
        self.embedder = get_embedder_provider(embedder_config["provider"]).get_embedder(embedder_config)
        
        # Get vector store configuration
        vector_store_config = self.config.get("vector_store")
        collection_name = "kanto_knowledge"
        vector_size = 384  # Default, or get from config if needed
        if "story_segments" in vector_store_config.get("collections", {}):
            vector_size = vector_store_config["collections"]["story_segments"].get("vector_size", 384)
        client = QdrantClient(
            host=vector_store_config.get("host", "localhost"), 
            port=vector_store_config.get("port", 6333),
            prefer_grpc=False,
            check_compatibility=False  # Disable version compatibility check
        )
        # Create collection if it doesn't exist
        if collection_name not in [c.name for c in client.get_collections().collections]:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
        self.client = client
        self.collection_name = collection_name
        # Initialize vector store with Qdrant
        self.vector_store = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embedder
        )
        # Check if collection is empty
        collection_count = self.client.count(collection_name=self.collection_name, exact=True).count
        # Load initial knowledge if needed
        if collection_count == 0:
            self._load_initial_knowledge()

    # ====== ENHANCED METHODS FOR RICH DATA ======

    def get_enhanced_location_info(self, location: str) -> Dict[str, Any]:
        """Get enhanced location information including atmosphere, encounters, and seasonal effects."""
        # Search for location-specific documents with enhanced data
        docs = self.vector_store.similarity_search(
            f"{location} location atmosphere encounters weather seasonal",
            k=5
        )
        
        location_info = {
            "name": location,
            "description": "",
            "atmosphere": "",
            "encounters": [],
            "seasonal_effects": {},
            "weather_patterns": {},
            "notable_features": [],
            "connected_locations": []
        }
        
        for doc in docs:
            metadata = doc.metadata
            if metadata.get("type") == "location" and metadata.get("name", "").lower().replace("-", " ") == location.lower().replace("-", " "):
                try:
                    # Try to parse as JSON first (enhanced data format)
                    if doc.page_content.strip().startswith('{'):
                        data = json.loads(doc.page_content)
                    else:
                        # Parse from text format
                        data = self._parse_location_text(doc.page_content)
                    
                    location_info.update({
                        "description": data.get("description", ""),
                        "atmosphere": data.get("atmosphere", ""),
                        "encounters": data.get("encounters", []),
                        "seasonal_effects": data.get("seasonal_effects", {}),
                        "weather_patterns": data.get("weather_patterns", {}),
                        "notable_features": data.get("notable_features", []),
                        "connected_locations": data.get("connected_locations", [])
                    })
                except (json.JSONDecodeError, Exception):
                    # Fallback to original method
                    location_info["description"] = doc.page_content
                break
        
        return location_info

    def get_character_personality(self, character_name: str) -> Dict[str, Any]:
        """Get detailed character personality and relationship information."""
        docs = self.vector_store.similarity_search(
            f"{character_name} character personality traits relationships",
            k=3
        )
        
        character_info = {
            "name": character_name,
            "core_traits": [],
            "relationships": {},
            "backstory": "",
            "goals": [],
            "fears": [],
            "growth_potential": [],
            "dialogue_style": {}
        }
        
        for doc in docs:
            metadata = doc.metadata
            if metadata.get("type") == "character" and metadata.get("name", "").lower() == character_name.lower():
                try:
                    if doc.page_content.strip().startswith('{'):
                        data = json.loads(doc.page_content)
                    else:
                        data = self._parse_character_text(doc.page_content)
                    
                    character_info.update({
                        "core_traits": data.get("personality", {}).get("core_traits", []),
                        "relationships": data.get("relationships", {}),
                        "backstory": data.get("backstory", ""),
                        "goals": data.get("personality", {}).get("goals", []),
                        "fears": data.get("personality", {}).get("fears", []),
                        "growth_potential": data.get("personality", {}).get("growth_potential", []),
                        "dialogue_style": data.get("dialogue_style", {})
                    })
                except (json.JSONDecodeError, Exception):
                    character_info["backstory"] = doc.page_content
                break
        
        return character_info

    def get_pokemon_personality(self, pokemon_name: str) -> Dict[str, Any]:
        """Get Pokémon personality and behavioral information."""
        docs = self.vector_store.similarity_search(
            f"{pokemon_name} pokemon personality temperament behavior",
            k=3
        )
        
        pokemon_info = {
            "name": pokemon_name,
            "personality_traits": [],
            "temperament": "",
            "behavior_patterns": [],
            "evolution_emotions": {},
            "training_preferences": [],
            "bond_building": []
        }
        
        for doc in docs:
            metadata = doc.metadata
            if metadata.get("type") == "pokemon" and metadata.get("name", "").lower() == pokemon_name.lower():
                try:
                    if doc.page_content.strip().startswith('{'):
                        data = json.loads(doc.page_content)
                    else:
                        data = self._parse_pokemon_text(doc.page_content)
                    
                    pokemon_info.update({
                        "personality_traits": data.get("personality", "").split(", ") if isinstance(data.get("personality"), str) else data.get("personality", []),
                        "temperament": data.get("temperament", ""),
                        "behavior_patterns": data.get("behavior_patterns", []),
                        "evolution_emotions": data.get("evolution_emotions", {}),
                        "training_preferences": data.get("training_preferences", []),
                        "bond_building": data.get("bond_building", [])
                    })
                except (json.JSONDecodeError, Exception):
                    pokemon_info["temperament"] = doc.page_content
                break
        
        return pokemon_info

    def get_seasonal_context(self, current_month: int = None) -> Dict[str, Any]:
        """Get seasonal events and atmosphere for storytelling."""
        if current_month is None:
            current_month = datetime.now().month
        
        season = self._get_season_from_month(current_month)
        month_name = calendar.month_name[current_month].lower()
        
        docs = self.vector_store.similarity_search(
            f"seasonal events {season} {month_name} festival calendar",
            k=5
        )
        
        seasonal_info = {
            "season": season,
            "month": month_name,
            "events": [],
            "pokemon_behavior": {},
            "atmosphere": "",
            "weather_effects": {}
        }
        
        for doc in docs:
            if "seasonal" in doc.page_content.lower() or season in doc.page_content.lower():
                try:
                    if doc.page_content.strip().startswith('{'):
                        data = json.loads(doc.page_content)
                        if season in data:
                            seasonal_info.update({
                                "events": data[season].get("events", []),
                                "pokemon_behavior": data[season].get("pokemon_behavior", {}),
                                "atmosphere": data[season].get("atmosphere", ""),
                                "weather_effects": data[season].get("weather_effects", {})
                            })
                except (json.JSONDecodeError, Exception):
                    if season in doc.page_content.lower():
                        seasonal_info["atmosphere"] = doc.page_content
        
        return seasonal_info

    def get_character_driven_choices(self, situation: str, available_characters: List[str]) -> List[Dict[str, Any]]:
        """Generate character-driven choice options based on their personalities."""
        choices = []
        
        for character_name in available_characters:
            character_info = self.get_character_personality(character_name)
            
            # Generate choices based on character traits
            if character_info["core_traits"]:
                choice_type = self._determine_choice_type(character_info["core_traits"])
                choice = {
                    "text": f"Ask {character_name} for help",
                    "character": character_name,
                    "type": choice_type,
                    "personality_driven": True,
                    "traits": character_info["core_traits"][:3],  # Top 3 traits
                    "expected_response": self._predict_character_response(character_info, situation)
                }
                choices.append(choice)
        
        return choices

    def get_enhanced_story_context(self, query: str, include_seasonal: bool = True) -> Dict[str, Any]:
        """Get comprehensive story context including characters, locations, and seasonal elements."""
        base_context = self.get_story_context(query)
        
        # Get seasonal context if requested
        seasonal_context = self.get_seasonal_context() if include_seasonal else {}
        
        # Categorize context by type
        characters = []
        locations = []
        pokemon = []
        items = []
        
        for context_item in base_context:
            metadata = context_item.get("metadata", {})
            item_type = metadata.get("type", "unknown")
            
            if item_type == "character":
                character_name = metadata.get("name", "")
                if character_name:
                    characters.append(self.get_character_personality(character_name))
            elif item_type == "location":
                location_name = metadata.get("name", "")
                if location_name:
                    locations.append(self.get_enhanced_location_info(location_name))
            elif item_type == "pokemon":
                pokemon_name = metadata.get("name", "")
                if pokemon_name:
                    pokemon.append(self.get_pokemon_personality(pokemon_name))
            elif item_type == "item":
                items.append(context_item)
        
        return {
            "characters": characters,
            "locations": locations,
            "pokemon": pokemon,
            "items": items,
            "seasonal": seasonal_context,
            "raw_context": base_context
        }

    # ====== HELPER METHODS ======

    def _get_season_from_month(self, month: int) -> str:
        """Get season from month number."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    def _parse_location_text(self, text: str) -> Dict[str, Any]:
        """Parse location information from text format."""
        # Simple parser for location text
        lines = text.split('\n')
        data = {}
        
        for line in lines:
            if 'Description:' in line:
                data['description'] = line.split('Description:', 1)[1].strip()
            elif 'Atmosphere:' in line:
                data['atmosphere'] = line.split('Atmosphere:', 1)[1].strip()
        
        return data

    def _parse_character_text(self, text: str) -> Dict[str, Any]:
        """Parse character information from text format."""
        # Simple parser for character text
        lines = text.split('\n')
        data = {"personality": {}}
        
        for line in lines:
            if 'Personality:' in line or 'Core Traits:' in line:
                traits_text = line.split(':', 1)[1].strip()
                data['personality']['core_traits'] = [trait.strip() for trait in traits_text.split(',')]
        
        return data

    def _parse_pokemon_text(self, text: str) -> Dict[str, Any]:
        """Parse Pokemon information from text format."""
        # Simple parser for Pokemon text
        lines = text.split('\n')
        data = {}
        
        for line in lines:
            if 'Personality:' in line:
                data['personality'] = line.split('Personality:', 1)[1].strip()
            elif 'Temperament:' in line:
                data['temperament'] = line.split('Temperament:', 1)[1].strip()
        
        return data

    def _determine_choice_type(self, traits: List[str]) -> str:
        """Determine choice type based on character traits."""
        trait_text = ' '.join(traits).lower()
        
        if any(word in trait_text for word in ['helpful', 'caring', 'nurturing']):
            return "supportive"
        elif any(word in trait_text for word in ['competitive', 'ambitious', 'strong']):
            return "challenging"
        elif any(word in trait_text for word in ['wise', 'knowledgeable', 'experienced']):
            return "advisory"
        elif any(word in trait_text for word in ['mysterious', 'secretive', 'enigmatic']):
            return "mysterious"
        else:
            return "friendly"

    def _predict_character_response(self, character_info: Dict[str, Any], situation: str) -> str:
        """Predict how a character would respond based on their personality."""
        traits = character_info.get("core_traits", [])
        if not traits:
            return "responds in their typical manner"
        
        primary_trait = traits[0].lower() if traits else "friendly"
        
        responses = {
            "helpful": "offers practical assistance and encouragement",
            "caring": "shows concern and emotional support",
            "competitive": "suggests a challenge or contest to overcome the situation",
            "wise": "provides thoughtful advice and guidance",
            "mysterious": "gives cryptic hints and makes you think",
            "energetic": "brings enthusiasm and energy to help solve the problem",
            "shy": "offers quiet support and gentle suggestions"
        }
        
        return responses.get(primary_trait, "responds according to their personality")

    # ====== ORIGINAL METHODS (PRESERVED) ======

    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get information about a specific location."""
        # Search for location-specific documents
        docs = self.vector_store.similarity_search(
            f"Information about {location} in Kanto region",
            k=3
        )
        
        # Combine and format location information
        location_info = {
            "name": location,
            "description": "",
            "notable_features": [],
            "related_events": []
        }
        
        for doc in docs:
            if doc.metadata.get("type") == "location" and doc.metadata.get("name", "").lower() == location.lower():
                # Parse location data from document
                try:
                    data = json.loads(doc.page_content)
                    location_info.update({
                        "description": data.get("description", ""),
                        "notable_features": data.get("notable_features", []),
                        "services": data.get("services", []),
                        "connected_locations": data.get("connected_locations", [])
                    })
                except json.JSONDecodeError:
                    # Fallback to raw content
                    location_info["description"] = doc.page_content
                break
        
        return location_info

    def get_story_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant story context for a given query."""
        # Search for relevant documents
        docs = self.vector_store.similarity_search(
            query,
            k=5
        )
        
        # Format and return context
        context = []
        for doc in docs:
            context.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return context

    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None):
        """Add new knowledge to the vector store."""
        doc = Document(
            page_content=content,
            metadata=metadata or {}
        )
        self.vector_store.add_documents([doc])

    def add_memory(self, memory: Dict[str, Any]) -> str:
        """Add a memory to the vector store."""
        content = f"Memory: {memory['memory_type']} - {memory['content']}"
        metadata = {
            "type": "memory",
            "memory_type": memory["memory_type"],
            "timestamp": memory["timestamp"],
            **memory.get("metadata", {})
        }
        
        self.add_knowledge(content, metadata)
        return memory["memory_type"]

    def get_memories_by_type(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories by type."""
        docs = self.vector_store.similarity_search(
            f"memory {memory_type}",
            k=limit,
            filter={"type": "memory", "memory_type": memory_type}
        )
        
        memories = []
        for doc in docs:
            memories.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return memories

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get memories relevant to the current context."""
        docs = self.vector_store.similarity_search(
            query,
            k=limit,
            filter={"type": "memory"}
        )
        
        memories = []
        for doc in docs:
            memories.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return memories

    def get_memories_by_character(self, character: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a specific character."""
        docs = self.vector_store.similarity_search(
            f"character {character}",
            k=limit,
            filter={"type": "memory"}
        )
        
        memories = []
        for doc in docs:
            if character.lower() in doc.page_content.lower():
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        
        return memories

    def get_memories_by_location(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a specific location."""
        docs = self.vector_store.similarity_search(
            f"location {location}",
            k=limit,
            filter={"type": "memory"}
        )
        
        memories = []
        for doc in docs:
            if location.lower() in doc.page_content.lower():
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        
        return memories

    def _load_initial_knowledge(self):
        """Load initial Kanto knowledge into the vector store."""
        logger.info("Loading initial Kanto knowledge...")
        
        data_dir = Path("data/raw/kanto")
        if not data_dir.exists():
            logger.warning("Kanto data directory not found. Please run the data fetching script first.")
            return
        
        # Load locations
        self._load_locations(data_dir / "locations.json")
        
        # Load Pokémon
        self._load_pokemon(data_dir / "pokemon.json")
        
        # Load characters
        self._load_characters(data_dir / "characters.json")
        
        # Load story elements
        self._load_story_elements(data_dir / "story_elements.json")
        
        logger.info(f"Loaded {self.client.count(collection_name=self.collection_name, exact=True).count} knowledge items")

    def _load_locations(self, filepath: Path):
        """Load location data into vector store."""
        if not filepath.exists():
            logger.warning(f"Location file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        for location in locations:
            # Create structured content for better searchability
            location_name = location.get('name', location.get('display_name', 'Unknown Location'))
            content_parts = [
                f"Location: {location.get('display_name', location_name)}",
                f"Description: {location.get('description', 'A location in the Kanto region.')}"
            ]
            
            # Add services if available
            services = location.get('services', [])
            if services:
                content_parts.append(f"Services: {', '.join(services)}")
            
            # Add notable features
            notable_features = location.get('notable_features', [])
            if notable_features:
                content_parts.append(f"Features: {', '.join(notable_features)}")
            
            # Add connected locations
            connected = location.get('connected_locations', [])
            if connected:
                content_parts.append(f"Connected to: {', '.join(connected)}")
            
            content = "\n".join(content_parts)
            
            metadata = {
                "type": "location",
                "name": location_name,
                "display_name": location.get("display_name", location_name),
                "full_data": json.dumps(location, ensure_ascii=False)
            }
            self.add_knowledge(content, metadata)
        
        logger.info(f"Loaded {len(locations)} locations")

    def _load_pokemon(self, filepath: Path):
        """Load Pokémon data into vector store."""
        if not filepath.exists():
            logger.warning(f"Pokémon file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            pokemon_list = json.load(f)
        
        for pokemon in pokemon_list:
            # Create structured content for better searchability
            content_parts = [
                f"Pokemon: {pokemon.get('display_name', pokemon['name'])}",
                f"Types: {', '.join(pokemon.get('types', []))}",
            ]
            
            # Add anime personality if available
            anime_personality = pokemon.get('anime_personality', {})
            if anime_personality:
                content_parts.extend([
                    f"Personality: {', '.join(anime_personality.get('core_traits', []))}",
                    f"Temperament: {anime_personality.get('temperament', '')}",
                    f"Behavior: {anime_personality.get('behavioral_notes', '')}"
                ])
                
                # Add emotional triggers
                emotional_triggers = anime_personality.get('emotional_triggers', {})
                if emotional_triggers:
                    content_parts.append(f"Emotions: Happy when {emotional_triggers.get('happy', '')}, Angry when {emotional_triggers.get('angry', '')}")
            
            # Add stats for context
            stats = pokemon.get('stats', {})
            if stats:
                content_parts.append(f"Stats: HP {stats.get('hp', 0)}, Attack {stats.get('attack', 0)}, Defense {stats.get('defense', 0)}")
            
            content = "\n".join(content_parts)
            
            # Store the full JSON as well for detailed retrieval
            metadata = {
                "type": "pokemon",
                "name": pokemon["name"],
                "display_name": pokemon.get("display_name", pokemon["name"]),
                "types": pokemon.get("types", []),
                "full_data": json.dumps(pokemon, ensure_ascii=False)
            }
            self.add_knowledge(content, metadata)
        
        logger.info(f"Loaded {len(pokemon_list)} Pokémon")

    def _load_characters(self, filepath: Path):
        """Load character data into vector store."""
        if not filepath.exists():
            logger.warning(f"Character file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        
        for character in characters:
            # Create structured content for better searchability
            content_parts = [
                f"Character: {character.get('name', 'Unknown')}",
                f"Role: {character.get('role', character.get('title', 'Unknown'))}",
                f"Description: {character.get('description', 'A character in the Kanto region.')}"
            ]
            
            # Add personality if available
            personality = character.get('personality')
            if personality:
                content_parts.append(f"Personality: {personality}")
            
            # Add location if available
            location = character.get('location')
            if location:
                content_parts.append(f"Location: {location}")
            
            content = "\n".join(content_parts)
            
            metadata = {
                "type": "character",
                "name": character.get("name", "Unknown"),
                "role": character.get("role", character.get("title", "")),
                "location": character.get("location", ""),
                "full_data": json.dumps(character, ensure_ascii=False)
            }
            self.add_knowledge(content, metadata)
        
        logger.info(f"Loaded {len(characters)} characters")

    def _load_story_elements(self, filepath: Path):
        """Load story elements into vector store."""
        if not filepath.exists():
            logger.warning(f"Story elements file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            story_elements = json.load(f)
        
        for element in story_elements:
            # Create structured content for better searchability
            element_name = element.get('name', element.get('id', 'Unknown Story Element'))
            content_parts = [
                f"Story Element: {element_name}",
                f"Description: {element.get('description', 'A story element in the Kanto region.')}"
            ]
            
            # Add element type if available
            element_type = element.get('type', '')
            if element_type:
                content_parts.append(f"Type: {element_type}")
            
            # Add locations if available
            locations = element.get('locations', [])
            if locations:
                content_parts.append(f"Locations: {', '.join(locations)}")
            
            # Add characters if available
            characters = element.get('characters', [])
            if characters:
                content_parts.append(f"Characters: {', '.join(characters)}")
            
            content = "\n".join(content_parts)
            
            metadata = {
                "type": "story_element",
                "name": element_name,
                "element_type": element_type,
                "full_data": json.dumps(element, ensure_ascii=False)
            }
            self.add_knowledge(content, metadata)
        
        logger.info(f"Loaded {len(story_elements)} story elements") 