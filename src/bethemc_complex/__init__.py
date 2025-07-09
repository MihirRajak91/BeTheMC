"""
🎮 BeTheMC Complex Architecture - Dynamic Pokémon Adventure Game

A sophisticated text-based Pokémon adventure game with AI-driven storytelling,
dynamic personality systems, and persistent game state management.

🏗️ Architecture Overview:
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   API Layer     │    │  Service Layer  │    │   Core Models   │
    │  (FastAPI)      │◄──►│  (Business      │◄──►│  (Domain        │
    │                 │    │   Logic)        │    │   Models)       │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  Database       │    │   AI/ML         │    │   Utilities     │
    │  (MongoDB)      │    │  (Story Gen)    │    │  (Config/Log)   │
    └─────────────────┘    └─────────────────┘    └─────────────────┘

📦 Package Structure:
    bethemc_complex/
    ├── api/          # FastAPI routes and request/response models
    ├── core/         # Domain models and game logic
    ├── services/     # Business logic and orchestration
    ├── database/     # Data persistence and MongoDB integration
    ├── ai/           # AI story generation and personality systems
    ├── models/       # Pydantic schemas for API validation
    ├── config/       # Configuration management
    ├── utils/        # Shared utilities and helpers
    └── data/         # Data loading and vector storage

🎯 Key Features:
    • AI-powered dynamic storytelling
    • Personality-driven choice systems
    • Persistent game state management
    • MongoDB integration for data storage
    • Vector-based memory and context systems
    • RESTful API with comprehensive validation

🚀 Quick Start:
    from bethemc_complex.api.app import app
    from bethemc_complex.services.game_service import GameService
    
    # Start a new game
    game_service = GameService()
    game_state = await game_service.start_new_game("Ash Ketchum")
    
    # Make choices and progress through the story
    updated_state = await game_service.make_choice(game_state, "choice-1")

📚 Documentation:
    • API Guide: docs/api/README.md
    • Architecture: docs/design/
    • Testing: docs/api_testing_guide.md
    • Performance: docs/performance/
"""

__version__ = "0.1.0" 