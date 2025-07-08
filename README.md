# BeTheMC - Dynamic Pokémon Adventure

A choice-based Pokémon adventure game set in the Kanto region, featuring dynamic story generation powered by LLMs and vector databases.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- 🎮 Dynamic story generation using LLMs
- 🔍 Vector database integration for Kanto world knowledge
- 🔐 Secure JWT-based authentication
- 👤 User profiles and progress tracking
- 🗺️ Immersive Kanto region exploration
- 🤖 AI-powered NPC interactions
- 📱 RESTful API for game interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- [Poetry](https://python-poetry.org/) (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BeTheMC.git
   cd BeTheMC
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start services:
   ```bash
   docker-compose up -d
   ```

5. Choose your version to run:

   **Simple Version (Recommended for learning):**
   ```bash
   python main.py
   # Visit: http://localhost:8001/docs
   ```

   **Complex Version (For studying enterprise patterns):**
   ```bash
   python main_complex.py
   # Visit: http://localhost:8002/docs
   ```

## 📚 Documentation

- **[Architecture Comparison Guide](ARCHITECTURE_COMPARISON.md)** - Complete guide to both versions
- **[Simple Guide](SIMPLE_GUIDE.md)** - How the simplified version works
- **Simple API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Complex API Docs**: [http://localhost:8002/docs](http://localhost:8002/docs)
- [API Reference](/docs/api/README.md)
- [Development Guide](/docs/development.md)

### 🎓 Study Path
1. **Start with Simple Version** - Easy to understand
2. **Read Architecture Comparison** - Understand the differences  
3. **Study Complex Version** - Learn enterprise patterns
4. **Compare Side by Side** - Run both and see the differences

## 🔧 Project Structure

This project includes **two complete implementations** to demonstrate different architectural approaches:

### Simple Version (`src/bethemc/`)
**Easy to understand, perfect for learning:**
```
src/bethemc/
├── api/
│   ├── app.py              # FastAPI setup
│   ├── routes.py           # All 6 API endpoints  
│   └── game_manager.py     # ALL game logic in one class
├── models/
│   └── models.py           # ALL models in one file
├── database/
│   └── service.py          # ALL database operations
└── config/
    └── settings.py         # Configuration
```

### Complex Version (`src/bethemc_complex/`)
**Enterprise patterns, perfect for studying advanced architecture:**
```
src/bethemc_complex/
├── api/
│   ├── app.py              # FastAPI setup
│   ├── routes.py           # API endpoints with dependency injection
│   ├── game_manager.py     # Coordinates between services
│   └── dependencies.py     # Dependency injection setup
├── models/
│   ├── api.py              # API request/response models
│   └── core.py             # Core business models
├── services/
│   ├── game_service.py     # Core game logic
│   ├── save_service.py     # Save/load functionality
│   └── summarization_service.py # AI features
├── database/
│   ├── service.py          # Database abstraction layer
│   └── connection.py       # Database connection
├── core/
│   ├── game.py             # Core game entities
│   └── interfaces.py       # Abstract interfaces
└── config/
    └── settings.py         # Configuration
```

### Additional Files
```
├── main.py                 # Run simple version (port 8001)
├── main_complex.py         # Run complex version (port 8002)
├── ARCHITECTURE_COMPARISON.md # Detailed comparison guide
├── tests/                  # Test suite
├── docs/                   # Documentation
└── docker-compose.yml      # Docker configuration
```

## 🌐 API Usage

### Authentication

1. Register a new user:
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"securepass","username":"trainer"}'
   ```

2. Get access token:
   ```bash
   curl -X POST http://localhost:8000/auth/token \
     -d "username=user@example.com" \
     -d "password=securepass" \
     -d "grant_type=password"
   ```

3. Use the token for authenticated requests:
   ```bash
   curl -X GET http://localhost:8000/api/v1/game/start \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## 🛠 Development

### Running Tests

```bash
poetry run pytest
```

### Code Style

We use:
- Black for code formatting
- isort for import sorting
- mypy for type checking

```bash
poetry run black .
poetry run isort .
poetry run mypy .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Pokémon and all related content © Nintendo, Game Freak, and The Pokémon Company
- Built with FastAPI, MongoDB, and Qdrant
- Inspired by classic Pokémon games