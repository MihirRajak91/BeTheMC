#!/usr/bin/env python3
"""
Test script to verify metadata storage.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bethemc_complex.data.vector_store import KantoKnowledgeBase
from bethemc_complex.utils.config import Config

def test_metadata():
    """Test metadata storage."""
    print("🧪 Testing metadata storage...")
    
    try:
        # Initialize knowledge base
        config = Config()
        kb = KantoKnowledgeBase(config)
        
        # Test adding a simple document with metadata
        print("\n📝 Adding test document with metadata...")
        test_content = "This is a test document about Pallet Town"
        test_metadata = {
            "type": "location",
            "name": "pallet-town",
            "display_name": "Pallet Town"
        }
        
        kb.add_knowledge(test_content, test_metadata)
        print("✅ Added test document")
        
        # Try to retrieve it
        print("\n🔍 Searching for test document...")
        docs = kb.vector_store.similarity_search("Pallet Town", k=5)
        
        print(f"Found {len(docs)} documents")
        for i, doc in enumerate(docs):
            print(f"Document {i+1}:")
            print(f"  Content: {doc.page_content[:50]}...")
            print(f"  Metadata: {doc.metadata}")
        
    except Exception as e:
        print(f"❌ Error testing metadata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metadata() 