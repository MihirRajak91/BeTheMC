from qdrant_client import QdrantClient
from qdrant_client.http import models
import time

def test_qdrant_connection():
    """Test the connection to Qdrant and basic functionality."""
    try:
        # Initialize client
        client = QdrantClient("localhost", port=6333)
        
        # Create a test collection
        collection_name = "test_collection"
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if collection_name not in collection_names:
            # Create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=4,  # Small size for testing
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection {collection_name} already exists")
        
        # Test adding a point
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=1,
                    vector=[0.1, 0.2, 0.3, 0.4],
                    payload={"text": "test point"}
                )
            ]
        )
        print("Successfully added test point")
        
        # Test search
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=1
        )
        print(f"Search result: {search_result}")
        
        print("\nQdrant connection and basic functionality test passed! ✅")
        return True
        
    except Exception as e:
        print(f"Error testing Qdrant: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Qdrant connection...")
    # Give Qdrant a moment to start up if it was just launched
    time.sleep(2)
    test_qdrant_connection() 