# BeTheMC - Dynamic Pokémon Adventure

A choice-based Pokémon adventure game set in the Kanto region, featuring dynamic story generation powered by LLMs and vector databases.

## Project Structure

```
betheMC/
├── src/                    # Source code
│   ├── bethemc/           # Main package
│   │   ├── core/          # Core game mechanics
│   │   │   ├── game.py    # Game state management
│   │   │   ├── player.py  # Player state and traits
│   │   │   └── world.py   # World state management
│   │   ├── ai/            # AI and LLM integration
│   │   │   ├── narrator.py    # Story narration
│   │   │   ├── generator.py   # Content generation
│   │   │   └── prompts.py     # LLM prompts
│   │   ├── data/          # Data management
│   │   │   ├── vector_store.py    # Qdrant integration
│   │   │   ├── knowledge_base.py  # Knowledge management
│   │   │   └── loaders.py         # Data loading utilities
│   │   └── utils/         # Utility functions
│   │       ├── config.py  # Configuration management
│   │       └── logger.py  # Logging setup
│   └── scripts/           # Utility scripts
│       ├── setup_db.py    # Database setup
│       └── load_data.py   # Data loading
├── data/                  # Game data
│   ├── raw/              # Raw data files
│   │   └── kanto/        # Kanto region data
│   │       ├── locations.json
│   │       ├── characters.json
│   │       ├── pokemon.json
│   │       └── story_elements.json
│   └── processed/        # Processed data
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── docs/                # Documentation
│   ├── api/            # API documentation
│   ├── guides/         # User guides
│   └── design/         # Design documents
├── config/             # Configuration files
│   └── default.yaml    # Default configuration
├── scripts/            # Development scripts
│   ├── setup.sh        # Setup script
│   └── test.sh         # Test script
├── .env               # Environment variables
├── .gitignore        # Git ignore file
├── docker-compose.yml # Docker configuration
├── pyproject.toml    # Project metadata
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Features

- Dynamic story generation using LLMs
- Vector database integration for Kanto world knowledge
- Personalized narrative based on player choices
- Rich character development and relationships
- Immersive Kanto region exploration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start Qdrant:
```bash
docker-compose up -d
```

4. Load Kanto data:
```bash
python -m src.scripts.load_data
```

5. Run the game:
```bash
python -m src.bethemc.core.game
```

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use type hints and docstrings

## License

MIT License - see LICENSE file for details