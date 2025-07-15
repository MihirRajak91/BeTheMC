#!/usr/bin/env python3
"""
Simple launcher for BeTheMC Terminal Game

This script checks that all requirements are met and launches the game.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        'langchain',
        'qdrant-client', 
        'sentence-transformers',
        'pydantic',
        'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_qdrant():
    """Check if Qdrant is running."""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333, check_compatibility=False)
        client.get_collections()
        return True
    except Exception:
        return False

def main():
    """Main launcher function."""
    print("🚀 BeTheMC Game Launcher")
    print("=" * 40)
    
    # Check Python version
    print("🐍 Checking Python version...")
    if not check_python_version():
        return 1
    print("✅ Python version OK")
    
    # Check requirements
    print("📦 Checking required packages...")
    if not check_requirements():
        return 1
    print("✅ All packages installed")
    
    # Check Qdrant
    print("🔍 Checking Qdrant vector database...")
    if not check_qdrant():
        print("❌ Qdrant is not running or not accessible")
        print("\nTo start Qdrant:")
        print("1. If using Docker: docker-compose up -d")
        print("2. Or install locally: https://qdrant.tech/documentation/quick-start/")
        print("3. Make sure it's running on localhost:6333")
        return 1
    print("✅ Qdrant is running")
    
    # Check if data exists
    data_dir = Path("data/raw/kanto")
    if not data_dir.exists() or not any(data_dir.glob("*.json")):
        print("⚠️  Kanto data not found. Fetching now...")
        try:
            subprocess.run([sys.executable, "scripts/fetch_kanto_data.py"], check=True)
            print("✅ Kanto data fetched")
        except subprocess.CalledProcessError:
            print("❌ Failed to fetch Kanto data")
            print("You can try running: python scripts/fetch_kanto_data.py")
            return 1
    else:
        print("✅ Kanto data found")
    
    print("\n🎮 Launching BeTheMC Terminal Game...")
    print("=" * 40)
    
    # Launch the game
    try:
        subprocess.run([sys.executable, "terminal_game.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Game crashed with error code: {e.returncode}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Game launcher interrupted")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 