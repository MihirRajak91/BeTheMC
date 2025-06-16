"""
Vector store interface for Kanto world knowledge and story elements.
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.embeddings import OpenAIEmbeddings
import json
from pathlib import Path

class KantoKnowledgeBase:
    def __init__(self, collection_name: str = "kanto_knowledge"):
        """Initialize the Kanto knowledge base."""
        self.client = QdrantClient("localhost", port=6333)
        self.embeddings = OpenAIEmbeddings()
        self.collection_name = collection_name
        self._setup_collection()

    def _setup_collection(self):
        """Set up the Qdrant collection for Kanto knowledge."""
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=models.Distance.COSINE
                )
            )

    def add_knowledge(self, knowledge_type: str, content: str, metadata: Dict[str, Any]):
        """Add a piece of Kanto knowledge to the vector store."""
        # Generate embedding for the content
        embedding = self.embeddings.embed_query(content)
        
        # Add to vector store
        self.client.upsert(
            collection_name=self.collection_name,
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
            collection_name=self.collection_name,
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