# BeTheMC API Documentation

## Overview

The BeTheMC API provides a RESTful interface for the AI-powered Pokémon adventure game. It allows you to create game sessions, make choices, save/load games, and manage the story progression.

## Quick Start

### 1. Start the API Server

```bash
# Install dependencies
poetry install

# Start the server
poetry run python run_api.py
```

The server will start on `http://localhost:8000`

### 2. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## API Endpoints

### Game Management

#### Create New Game
```http
POST /api/v1/game/new
Content-Type: application/json

{
  "starting_location": "Pallet Town",
  "personality": {
    "friendship": 0.7,
    "courage": 0.6,
    "curiosity": 0.8,
    "wisdom": 0.5,
    "determination": 0.9
  }
}
```

#### Get Game State
```http
GET /api/v1/game/{session_id}/state
```

#### Make a Choice
```http
POST /api/v1/game/{session_id}/choice
Content-Type: application/json

{
  "choice_index": 0
}
```

### Save/Load System

#### Save Game
```http
POST /api/v1/game/{session_id}/save
Content-Type: application/json

{
  "save_name": "my_save"
}
```

#### Load Game
```http
POST /api/v1/game/{session_id}/load
Content-Type: application/json

{
  "save_name": "my_save"
}
```

#### List Saves
```http
GET /api/v1/saves
```

#### Delete Save
```http
DELETE /api/v1/saves/{save_name}
```

### Memory System

#### Add Memory
```http
POST /api/v1/game/{session_id}/memory
Content-Type: application/json

{
  "memory_type": "friendship",
  "content": "Became friends with a local trainer",
  "location": "Pallet Town",
  "metadata": {
    "trainer_name": "Ash"
  }
}
```

#### Get Compressed Context
```http
GET /api/v1/game/{session_id}/context
```

### Personality Management

#### Get Personality
```http
GET /api/v1/game/{session_id}/personality
```

#### Update Personality
```http
PUT /api/v1/game/{session_id}/personality
Content-Type: application/json

{
  "friendship": 0.8,
  "courage": 0.7,
  "curiosity": 0.9,
  "wisdom": 0.6,
  "determination": 0.8
}
```

## Data Models

### Personality Traits
```json
{
  "friendship": 0.7,      // Ability to form bonds (0.0-1.0)
  "courage": 0.6,         // Willingness to face challenges (0.0-1.0)
  "curiosity": 0.8,       // Desire to explore and learn (0.0-1.0)
  "wisdom": 0.5,          // Ability to make good decisions (0.0-1.0)
  "determination": 0.9    // Persistence in achieving goals (0.0-1.0)
}
```

### Choice
```json
{
  "text": "Help the injured Pokémon",
  "effects": {
    "friendship": 0.1,
    "courage": 0.05
  }
}
```

### Narrative Response
```json
{
  "narrative": "You find yourself in Pallet Town...",
  "choices": [
    {
      "text": "Visit Professor Oak",
      "effects": {"curiosity": 0.1}
    }
  ],
  "location": "Pallet Town",
  "personality": {
    "friendship": 0.7,
    "courage": 0.6,
    "curiosity": 0.8,
    "wisdom": 0.5,
    "determination": 0.9
  },
  "active_promises": ["Help Professor Oak with research"],
  "key_relationships": ["Professor Oak - mentor"],
  "story_context": {}
}
```

## Example Usage

### Complete Game Session

```bash
# 1. Create a new game
curl -X POST http://localhost:8000/api/v1/game/new \
  -H "Content-Type: application/json" \
  -d '{
    "starting_location": "Pallet Town",
    "personality": {
      "friendship": 0.7,
      "courage": 0.6,
      "curiosity": 0.8,
      "wisdom": 0.5,
      "determination": 0.9
    }
  }'

# Response will include session_id
SESSION_ID="your_session_id_here"

# 2. Get current state
curl http://localhost:8000/api/v1/game/$SESSION_ID/state

# 3. Make a choice
curl -X POST http://localhost:8000/api/v1/game/$SESSION_ID/choice \
  -H "Content-Type: application/json" \
  -d '{"choice_index": 0}'

# 4. Save the game
curl -X POST http://localhost:8000/api/v1/game/$SESSION_ID/save \
  -H "Content-Type: application/json" \
  -d '{"save_name": "my_adventure"}'
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (session/save not found)
- `500`: Internal Server Error

## Testing

Run the test script to verify all endpoints:

```bash
poetry run python test_api.py
```

## Configuration

The API uses the same configuration as the main game. Key settings in `config/default.yaml`:

- `save_dir`: Directory for save files
- `ai.llm`: LLM configuration
- `vector_store`: Vector database settings

## Development

### Adding New Endpoints

1. Add models to `src/bethemc/api/models.py`
2. Add logic to `src/bethemc/api/game_manager.py`
3. Add routes to `src/bethemc/api/routes.py`
4. Update this documentation

### Running in Development

```bash
# Start with auto-reload
poetry run python run_api.py

# Or use uvicorn directly
poetry run uvicorn bethemc.api.app:app --reload --host 0.0.0.0 --port 8000
``` 