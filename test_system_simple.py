#!/usr/bin/env python3
"""
Simple System Test - Tests core functionality without external dependencies
"""
import sys
import os

def test_imports():
    """Test that all core modules can be imported."""
    print("🧪 Testing Module Imports...")
    
    modules_to_test = [
        ("src.bethemc.api.app", "Simple API App"),
        ("src.bethemc_complex.api.app", "Complex API App"),
        ("src.bethemc.config.settings", "Settings"),
        ("src.bethemc.utils.logger", "Logger"),
        ("src.bethemc.models.api", "API Models"),
        ("src.bethemc.models.core", "Core Models"),
        ("src.bethemc.ai.story_generator", "Story Generator"),
        ("src.bethemc.ai.prompts", "Prompts"),
        ("src.bethemc.ai.generator", "AI Generator"),
        ("src.bethemc.data.vector_store", "Vector Store"),
        ("src.bethemc.database.connection", "Database Connection"),
        ("src.bethemc.services.game_service", "Game Service"),
        ("src.bethemc.services.save_service", "Save Service"),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except Exception as e:
            print(f"  ❌ {description}: {e}")
            failed_imports.append((module_name, str(e)))
    
    if failed_imports:
        print(f"\n⚠️ {len(failed_imports)} imports failed:")
        for module, error in failed_imports:
            print(f"  • {module}: {error}")
    else:
        print("\n✅ All core modules imported successfully!")
    
    return len(failed_imports) == 0

def test_app_creation():
    """Test that both API apps can be created."""
    print("\n🏗️ Testing App Creation...")
    
    try:
        from src.bethemc.api.app import create_app
        app = create_app()
        print("  ✅ Simple API app created successfully")
    except Exception as e:
        print(f"  ❌ Simple API app creation failed: {e}")
        return False
    
    try:
        from src.bethemc_complex.api.app import create_app as create_complex_app
        app = create_complex_app()
        print("  ✅ Complex API app created successfully")
    except Exception as e:
        print(f"  ❌ Complex API app creation failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from src.bethemc.config.settings import settings
        print(f"  ✅ Settings loaded: {settings.PROJECT_NAME} v{settings.VERSION}")
        print(f"  📊 MongoDB URL: {settings.MONGODB_URL}")
        print(f"  🎮 Default Location: {settings.DEFAULT_STARTING_LOCATION}")
        return True
    except Exception as e:
        print(f"  ❌ Configuration loading failed: {e}")
        return False

def test_models():
    """Test model creation."""
    print("\n📋 Testing Models...")
    
    try:
        from src.bethemc.models.core import Player, Story, Choice, GameState
        from src.bethemc.models.api import StartGameRequest, GameResponse
        
        # Test core models
        player = Player(id="test-123", name="TestPlayer", personality_traits={"courage": 5})
        story = Story(id="story-1", title="Test Story", content="Test content", location="Pallet Town")
        choice = Choice(id="choice-1", text="Test choice", effects={"courage": 1})
        
        print("  ✅ Core models created successfully")
        
        # Test API models
        start_request = StartGameRequest(player_name="TestPlayer", personality_traits={"courage": 5})
        game_response = GameResponse(
            player_id="test-123",
            player_name="TestPlayer",
            current_story={"id": "story-1", "title": "Test", "content": "Test", "location": "Pallet Town"},
            available_choices=[],
            personality_traits={"courage": 5},
            memories=[],
            game_progress={"current_location": "Pallet Town", "completed_events": []}
        )
        
        print("  ✅ API models created successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Model creation failed: {e}")
        return False

def test_ai_components():
    """Test AI components."""
    print("\n🤖 Testing AI Components...")
    
    try:
        from src.bethemc.ai.story_generator import StoryGenerator
        from src.bethemc.ai.prompts import get_story_prompt
        
        # Test prompts (this doesn't require config)
        prompt = get_story_prompt("Pallet Town", {"courage": 5}, [])
        print("  ✅ Story prompts working")
        
        # Test story generator with a simple config
        try:
            # Create a simple config for testing
            class TestConfig:
                def get(self, key, default=None):
                    if key == "ai.embedder":
                        return {"provider": "sentence-transformers", "model": "all-MiniLM-L6-v2"}
                    elif key == "vector_store":
                        return {"host": "localhost", "port": 6333}
                    return default
            
            config = TestConfig()
            story_gen = StoryGenerator(config)
            print("  ✅ Story generator initialized")
        except Exception as e:
            print(f"  ⚠️ Story generator failed (expected without proper config): {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI components failed: {e}")
        return False

def test_data_components():
    """Test data components."""
    print("\n📚 Testing Data Components...")
    
    try:
        from src.bethemc.data.vector_store import VectorStore
        from src.bethemc.config.settings import settings
        
        vector_store = VectorStore()
        print("  ✅ Vector store initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data components failed: {e}")
        return False

def test_services():
    """Test service components."""
    print("\n🔧 Testing Services...")
    
    try:
        from src.bethemc.services.game_service import GameService
        from src.bethemc.services.save_service import SaveService
        
        game_service = GameService()
        save_service = SaveService()
        
        print("  ✅ Services initialized")
        return True
        
    except Exception as e:
        print(f"  ❌ Services failed: {e}")
        return False

def test_scripts():
    """Test script imports."""
    print("\n📜 Testing Scripts...")
    
    scripts_to_test = [
        ("scripts/load_simple_data.py", "Data Loading Script"),
        ("scripts/integration_summary.py", "Integration Summary"),
        ("scripts/fetch_kanto_data.py", "Kanto Data Script"),
        ("scripts/load_enhanced_data.py", "Enhanced Data Script"),
    ]
    
    failed_scripts = []
    
    for script_path, description in scripts_to_test:
        if os.path.exists(script_path):
            print(f"  ✅ {description} exists")
        else:
            print(f"  ⚠️ {description} not found")
            failed_scripts.append(script_path)
    
    return len(failed_scripts) == 0

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("motor", "Motor (MongoDB)"),
        ("qdrant_client", "Qdrant Client"),
        ("langchain", "LangChain"),
        ("sentence_transformers", "Sentence Transformers"),
        ("requests", "Requests"),
        ("yaml", "PyYAML"),
    ]
    
    failed_deps = []
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ❌ {description} not available")
            failed_deps.append(module_name)
    
    if failed_deps:
        print(f"\n⚠️ Missing dependencies: {', '.join(failed_deps)}")
    else:
        print("\n✅ All dependencies available!")
    
    return len(failed_deps) == 0

def main():
    """Run all tests."""
    print("🚀 BeTheMC System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Configuration", test_configuration),
        ("Models", test_models),
        ("AI Components", test_ai_components),
        ("Data Components", test_data_components),
        ("Services", test_services),
        ("Scripts", test_scripts),
        ("Dependencies", test_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready for development.")
        print("\n🔧 Next steps:")
        print("  1. Set up MongoDB authentication")
        print("  2. Start Qdrant vector database")
        print("  3. Configure AI model endpoints")
        print("  4. Run the servers: python main.py and python main_complex.py")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 