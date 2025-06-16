"""
Script to load Kanto region data into Qdrant vector store.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.bethemc.data.vector_store import KantoKnowledgeBase
from src.bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Load Kanto data into Qdrant."""
    logger.info("Starting data loading process...")
    
    try:
        # Initialize knowledge base
        kb = KantoKnowledgeBase()
        
        # Load data from JSON files
        kb.load_kanto_data()
        
        logger.info("Data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 