"""
Vector store interface for Kanto world knowledge and story elements.
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.embeddings import OpenAIEmbeddings
import json
from pathlib import Path
import uuid

class KantoKnowledgeBase:
    def __init__(self, config: dict):
        self.config = config
        self.client = QdrantClient(
            url=config["vector_db"]["url"],
            api_key=config["vector_db"]["api_key"]
        )
        self.collections = {
            "story": config["vector_db"]["collections"]["story_segments"],
            "character": config["vector_db"]["collections"]["character_memories"],
            "choices": config["vector_db"]["collections"]["player_choices"],
            "memories": "story_memories"  # New collection for memories
        }
        self._initialize_collections()

    def _initialize_collections(self):
        """Initialize all required collections."""
        for collection_name in self.collections.values():
            try:
                self.client.get_collection(collection_name)
            except Exception:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.config["vector_db"]["vector_size"],
                        distance=models.Distance.COSINE
                    )
                )

    def add_memory(self, memory: dict) -> str:
        """Add a new memory to the vector store."""
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Create the memory document
        memory_doc = {
            "id": memory_id,
            "type": memory["memory_type"],
            "content": memory["content"],
            "timestamp": memory["timestamp"],
            "metadata": memory["metadata"]
        }
        
        # Generate embedding for the memory
        embedding = self._get_embedding(memory["content"])
        
        # Add to Qdrant
        self.client.upsert(
            collection_name=self.collections["memories"],
            points=[
                models.PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload=memory_doc
                )
            ]
        )
        
        return memory_id

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[dict]:
        """Retrieve memories relevant to the current context."""
        # Generate embedding for the query
        query_embedding = self._get_embedding(query)
        
        # Search for relevant memories
        results = self.client.search(
            collection_name=self.collections["memories"],
            query_vector=query_embedding,
            limit=limit
        )
        
        # Return the memories
        return [hit.payload for hit in results]

    def get_memories_by_type(self, memory_type: str, limit: int = 10) -> List[dict]:
        """Retrieve memories of a specific type."""
        results = self.client.scroll(
            collection_name=self.collections["memories"],
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=memory_type)
                    )
                ]
            ),
            limit=limit
        )
        
        return [hit.payload for hit in results[0]]

    def get_memories_by_character(self, character: str, limit: int = 10) -> List[dict]:
        """Retrieve memories related to a specific character."""
        results = self.client.scroll(
            collection_name=self.collections["memories"],
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.character",
                        match=models.MatchValue(value=character)
                    )
                ]
            ),
            limit=limit
        )
        
        return [hit.payload for hit in results[0]]

    def get_memories_by_location(self, location: str, limit: int = 10) -> List[dict]:
        """Retrieve memories related to a specific location."""
        results = self.client.scroll(
            collection_name=self.collections["memories"],
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.location",
                        match=models.MatchValue(value=location)
                    )
                ]
            ),
            limit=limit
        )
        
        return [hit.payload for hit in results[0]]

    def delete_memory(self, memory_id: str):
        """Delete a specific memory."""
        self.client.delete(
            collection_name=self.collections["memories"],
            points_selector=models.PointIdsList(
                points=[memory_id]
            )
        )

    def update_memory(self, memory_id: str, updates: dict):
        """Update a specific memory."""
        # Get the current memory
        current = self.client.retrieve(
            collection_name=self.collections["memories"],
            ids=[memory_id]
        )[0]
        
        # Update the payload
        current.payload.update(updates)
        
        # Update in Qdrant
        self.client.upsert(
            collection_name=self.collections["memories"],
            points=[
                models.PointStruct(
                    id=memory_id,
                    vector=current.vector,
                    payload=current.payload
                )
            ]
        )

    def add_knowledge(self, knowledge_type: str, content: str, metadata: Dict[str, Any]):
        """Add a piece of Kanto knowledge to the vector store."""
        # Generate embedding for the content
        embedding = self.embeddings.embed_query(content)
        
        # Add to vector store
        self.client.upsert(
            collection_name=self.collections["story"],
            points=[
                models.PointStruct(
                    id=hash(content),  # Simple hash as ID
                    vector=embedding,
                    payload={
                        "type": knowledge_type,
                        "content": content,
                        **metadata
                    }
                )
            ]
        )

    def search_knowledge(self, query: str, knowledge_type: Optional[str] = None, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant Kanto knowledge."""
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Prepare search parameters
        search_params = {
            "vector": query_embedding,
            "limit": limit
        }
        
        # Add type filter if specified
        if knowledge_type:
            search_params["filter"] = models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=knowledge_type)
                    )
                ]
            )
        
        # Perform search
        results = self.client.search(
            collection_name=self.collections["story"],
            **search_params
        )
        
        return [
            {
                "content": hit.payload["content"],
                "type": hit.payload["type"],
                "metadata": {k: v for k, v in hit.payload.items() 
                           if k not in ["content", "type"]},
                "score": hit.score
            }
            for hit in results
        ]

    def get_location_info(self, location_name: str) -> List[Dict[str, Any]]:
        """Get information about a specific location in Kanto."""
        return self.search_knowledge(
            f"Information about {location_name} in Kanto region",
            knowledge_type="location"
        )

    def get_character_info(self, character_name: str) -> List[Dict[str, Any]]:
        """Get information about a specific character in Kanto."""
        return self.search_knowledge(
            f"Information about {character_name} in Kanto region",
            knowledge_type="character"
        )

    def get_pokemon_info(self, pokemon_name: str) -> List[Dict[str, Any]]:
        """Get information about a specific Pokémon."""
        return self.search_knowledge(
            f"Information about {pokemon_name} Pokémon",
            knowledge_type="pokemon"
        )

    def get_story_context(self, current_situation: str) -> List[Dict[str, Any]]:
        """Get relevant story context for the current situation."""
        return self.search_knowledge(
            current_situation,
            knowledge_type="story_element"
        )

    def load_kanto_data(self, data_dir: str = "data/raw/kanto"):
        """Load Kanto world knowledge from JSON files."""
        data_path = Path(data_dir)
        
        # Load different types of knowledge
        knowledge_types = {
            "locations": "location",
            "characters": "character",
            "pokemon": "pokemon",
            "story_elements": "story_element"
        }
        
        for file_name, knowledge_type in knowledge_types.items():
            file_path = data_path / f"{file_name}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.add_knowledge(
                            knowledge_type=knowledge_type,
                            content=item["content"],
                            metadata=item.get("metadata", {})
                        ) 