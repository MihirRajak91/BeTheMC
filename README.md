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
- Qdrant (for vector search)
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

5. Run database migrations:
   ```bash
   poetry run python -m src.scripts.setup_db
   ```

6. Start the development server:
   ```bash
   poetry run uvicorn src.bethemc.api.app:app --reload
   ```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) (available after starting the server)
- [Authentication Guide](/docs/authentication.md)
- [API Reference](/docs/api/README.md)
- [Development Guide](/docs/development.md)

## 🔧 Project Structure

```
betheMC/
├── src/
│   ├── bethemc/
│   │   ├── api/            # FastAPI application and routes
│   │   │   ├── app.py      # Main FastAPI app
│   │   │   └── routes.py   # API route definitions
│   │   ├── auth/           # Authentication system
│   │   │   ├── __init__.py
│   │   │   ├── models.py   # Pydantic models
│   │   │   ├── routes.py   # Auth endpoints
│   │   │   └── service.py  # Auth business logic
│   │   ├── core/           # Core game logic
│   │   ├── ai/             # AI integration
│   │   └── utils/          # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Utility scripts
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