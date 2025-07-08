# 🎮 BeTheMC - Simple Guide

## 🎯 What This Is

BeTheMC is a **simple Pokémon adventure game API** where players make choices that shape their journey through the Pokémon world. This guide explains how the **SIMPLIFIED** version works.

## 🚀 Quick Start

### Running the Game
```bash
# Start the API server
python main.py

# Visit the API docs
http://localhost:8000/docs
```

### Playing the Game
1. **Start a new game**: `POST /api/v1/game/start`
2. **Make choices**: `POST /api/v1/game/choice`
3. **Save progress**: `POST /api/v1/game/save`
4. **Load saves**: `POST /api/v1/game/load`

## 📁 Simple File Structure

```
src/bethemc/
├── 📂 api/
│   ├── app.py                    # Main FastAPI app (simplified)
│   ├── simple_routes.py          # API endpoints (6 simple routes)
│   └── simple_game_manager.py    # Game logic (everything in one class)
├── 📂 database/
│   ├── connection.py             # MongoDB connection
│   └── simple_service.py         # Database operations (simplified)
├── 📂 models/
│   └── simple_models.py          # All data models in one file
└── 📂 config/
    └── settings.py               # Configuration
```

## 🎮 How the Game Works

### 1. Game Flow
```
Player starts game → Gets story + choices → Makes choice → Gets new story + choices → Repeat
```

### 2. Core Concepts

**Player**: Someone playing the game
- Has a name (like "Ash")
- Has personality traits (friendship, courage, curiosity, wisdom, determination)
- Traits change based on choices made

**Story**: A segment of the adventure
- Has a title and content (the text the player reads)
- Takes place in a location (like "Pallet Town")

**Choice**: Something the player can do
- Has text describing the action
- Has effects on personality traits
- Leads to new story content

**Memory**: Something the player remembers
- Important events, promises, relationships
- Used to maintain story consistency

**GameState**: Everything about the player's current game
- Contains player, current story, available choices, memories, progression

## 🏗️ Architecture

### Simple 3-Layer Design

```
🌐 API Layer (simple_routes.py)
    ↓ Handles HTTP requests
🎮 Game Logic (simple_game_manager.py)  
    ↓ Processes game rules
💾 Database (simple_service.py)
    ↓ Saves/loads data
```

### No Complex Stuff!
- ❌ No adapters or interfaces
- ❌ No complex dependency injection
- ❌ No summarization or AI features (for now)
- ✅ Just simple, clear code that works

## 📋 API Endpoints

### 1. Start New Game
```http
POST /api/v1/game/start
{
  "player_name": "Ash"
}
```
**Returns**: Complete game state with opening story and choices

### 2. Make Choice
```http
POST /api/v1/game/choice
{
  "player_id": "123-456-789",
  "choice_id": "choice-abc-def"
}
```
**Returns**: Updated story and new choices after the choice

### 3. Get Current Game
```http
GET /api/v1/game/state/123-456-789
```
**Returns**: Current game state (useful for refreshing)

### 4. Save Game
```http
POST /api/v1/game/save
{
  "player_id": "123-456-789",
  "save_name": "Before choosing starter"
}
```
**Returns**: Save confirmation with save ID

### 5. Load Game
```http
POST /api/v1/game/load
{
  "player_id": "123-456-789",
  "save_id": "save-xyz-123"
}
```
**Returns**: Loaded game state

### 6. List Saves
```http
GET /api/v1/game/saves/123-456-789
```
**Returns**: List of all save files for the player

## 🗄️ Database Structure

### Collections Used

**players**: Player information
```json
{
  "player_id": "123-456-789",
  "name": "Ash",
  "personality_traits": {
    "friendship": 7,
    "courage": 8,
    "curiosity": 6,
    "wisdom": 5,
    "determination": 7
  }
}
```

**games**: Current game states
```json
{
  "player_id": "123-456-789",
  "current_story": {
    "title": "Professor Oak's Laboratory",
    "content": "You enter the lab...",
    "location": "Oak's Laboratory"
  },
  "available_choices": [
    {
      "id": "choice-1",
      "text": "Choose Bulbasaur",
      "effects": {"wisdom": 1}
    }
  ],
  "memories": [],
  "progression": {
    "current_location": "Oak's Laboratory",
    "completed_events": ["Met Professor Oak"],
    "relationships": {},
    "inventory": []
  }
}
```

**saves**: Saved game files
```json
{
  "save_id": "save-abc-123",
  "player_id": "123-456-789",
  "save_name": "Before choosing starter",
  "created_at": "2024-01-01T12:00:00Z",
  // ... complete game state data
}
```

## 🎯 How Each Part Works

### SimpleGameManager (`simple_game_manager.py`)
**Main class that handles ALL game logic**

Key methods:
- `start_new_game()` - Creates new player and opening story
- `make_choice()` - Processes player choices and generates new content
- `save_game()` / `load_game()` - Handles save/load functionality
- `_generate_story_from_choice()` - Creates new story based on player choice
- `_generate_new_choices()` - Creates appropriate choices for each situation

### SimpleDatabaseService (`simple_service.py`)
**Handles ALL database operations**

Key methods:
- `save_game_state()` / `get_game_state()` - Current game persistence
- `save_player()` / `get_player()` - Player data management
- `save_game()` / `load_game()` - Save file management
- `get_player_saves()` - List all saves for a player

### Simple Routes (`simple_routes.py`)
**6 simple API endpoints that map HTTP requests to game manager methods**

Each route:
1. Receives HTTP request
2. Calls appropriate game manager method
3. Returns formatted response

### Simple Models (`simple_models.py`)
**All data structures in one file with clear explanations**

Two types:
- **Core Models**: Game data (Player, Story, Choice, etc.)
- **API Models**: Request/response formats (StartGameRequest, GameResponse, etc.)

## 🔧 Configuration

### Environment Variables
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=bethemc
MONGODB_COLLECTION_PLAYERS=players
MONGODB_COLLECTION_GAMES=games  
MONGODB_COLLECTION_SAVES=saves
```

### Default Settings
- All personality traits start at 5 (scale of 0-10)
- Players start in "Pallet Town"
- Stories are generated based on simple keyword matching
- Each choice affects 1-2 personality traits

## 🎮 Example Game Session

1. **Player starts**: "I want to play as Ash"
2. **System creates**: Player with default personality, opening story in Pallet Town
3. **Player sees**: "Welcome Ash! You wake up in Pallet Town... What do you want to do?"
4. **Choices offered**: "Go to Oak's lab", "Explore town", "Talk to mom"
5. **Player chooses**: "Go to Oak's lab" (increases curiosity +1)
6. **System generates**: New story about entering the lab, new choices about starter Pokémon
7. **Process repeats**: Each choice shapes personality and story direction

## 🚀 Adding New Features

### Adding New Story Content
Edit `_generate_story_from_choice()` in `simple_game_manager.py`:
```python
if "new_keyword" in choice_text:
    title = "New Story Title"
    content = "New story content..."
    new_location = "New Location"
```

### Adding New Choice Types
Edit `_generate_new_choices()` in `simple_game_manager.py`:
```python
if "new_situation" in story_title:
    return [
        Choice(text="New choice option", effects={"trait": 1})
    ]
```

### Adding New Personality Traits
1. Update default traits in `Player` model (`simple_models.py`)
2. Add trait effects to choices in game manager
3. Update any trait validation logic

## 🐛 Troubleshooting

### Common Issues

**"No game found for player"**
- Player hasn't started a game yet
- Use `POST /game/start` first

**"Invalid choice ID"**
- Choice ID doesn't match available choices
- Get current state with `GET /game/state/{player_id}` to see valid choices

**Database connection errors**
- Check MongoDB is running
- Verify connection string in settings

**Import errors**
- Make sure all files are using `simple_models` imports
- Check file paths in import statements

## 🎯 Summary

This simplified BeTheMC codebase:

✅ **Is easy to understand** - Clear file structure and comments
✅ **Does everything needed** - Complete game functionality
✅ **Is easy to modify** - Simple code structure
✅ **Has no complex dependencies** - Just FastAPI, MongoDB, and Pydantic
✅ **Is well documented** - Every part explained

The complexity has been removed while keeping all the core functionality. You can now easily understand how every part works and modify it as needed!

## 🔗 Quick Reference

- **Main app**: `src/bethemc/api/app.py`
- **Game logic**: `src/bethemc/api/simple_game_manager.py`
- **API routes**: `src/bethemc/api/simple_routes.py`
- **Database**: `src/bethemc/database/simple_service.py`
- **Models**: `src/bethemc/models/simple_models.py`
- **Docs**: `http://localhost:8000/docs`

Happy coding! 🎮 