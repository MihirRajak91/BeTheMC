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

logger = setup_logger(__name__)

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
        client = QdrantClient(host=vector_store_config.get("host", "localhost"), port=vector_store_config.get("port", 6333))
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
            content = json.dumps(location, ensure_ascii=False)
            metadata = {
                "type": "location",
                "name": location["name"],
                "display_name": location.get("display_name", location["name"])
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
            content = json.dumps(pokemon, ensure_ascii=False)
            metadata = {
                "type": "pokemon",
                "name": pokemon["name"],
                "display_name": pokemon.get("display_name", pokemon["name"]),
                "types": pokemon.get("types", [])
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
            content = json.dumps(character, ensure_ascii=False)
            metadata = {
                "type": "character",
                "name": character["name"],
                "role": character.get("role", ""),
                "location": character.get("location", "")
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
            content = json.dumps(element, ensure_ascii=False)
            metadata = {
                "type": "story_element",
                "name": element["name"],
                "element_type": element.get("type", "")
            }
            self.add_knowledge(content, metadata)
        
        logger.info(f"Loaded {len(story_elements)} story elements") 