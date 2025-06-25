# 🎮 BeTheMC API Testing Guide

## 🚀 Quick Start

Your enhanced Swagger documentation is now available at: **http://localhost:8000/docs**

## 📋 What's New in the Enhanced Documentation

### ✨ **Improved User Experience**
- **Detailed Descriptions**: Each endpoint now has comprehensive explanations
- **Practical Examples**: Real-world examples for all request/response models
- **Organized Tags**: Endpoints grouped into logical categories:
  - 🎯 **Game Flow**: Core game progression
  - 💾 **Save System**: Save/load functionality  
  - 👤 **Character Development**: Memories and personality
  - 📊 **Game State**: Current game information

### 🎯 **Enhanced Features**
- **Interactive Testing**: Click "Try it out" on any endpoint
- **Validation**: Built-in validation with helpful error messages
- **Examples**: Pre-filled example data for quick testing
- **Response Schemas**: Complete documentation of all response formats

## 🧪 Testing Workflow

### 1. **Start Your Adventure**
```
POST /api/v1/game/start
```
- **Parameters**: 
  - `player_name`: Your character's name (e.g., "Ash Ketchum")
  - `personality_traits`: Optional custom traits (0-10 scale)
- **What to expect**: Complete game state with story and choices

### 2. **Make Choices**
```
POST /api/v1/game/choice
```
- **Body**: 
  ```json
  {
    "player_id": "your-player-id-from-step-1",
    "choice_id": "choice-id-from-available-choices"
  }
  ```
- **What to expect**: New story content and updated choices

### 3. **Check Your Progress**
```
GET /api/v1/game/state/{player_id}
```
- **Parameters**: `player_id` from your game
- **What to expect**: Complete current game state

## 🎮 **Complete Game Session Example**

### Step 1: Start a Game
1. Go to **Game Flow** section
2. Click on **POST /api/v1/game/start**
3. Click **"Try it out"**
4. Enter your player name: `"TestPlayer"`
5. Click **"Execute"**
6. **Save the `player_id`** from the response

### Step 2: Make Your First Choice
1. Go to **POST /api/v1/game/choice**
2. Click **"Try it out"**
3. Enter the request body:
   ```json
   {
     "player_id": "your-player-id-from-step-1",
     "choice_id": "choice-id-from-step-1-response"
   }
   ```
4. Click **"Execute"**
5. Read the new story and note the new choice IDs

### Step 3: Continue Your Adventure
- Repeat Step 2 with new choice IDs
- Watch how your story evolves
- See how choices affect your personality traits

## 🛠️ **Advanced Testing Features**

### **Save System Testing**
1. **Save your game**: Use `POST /api/v1/game/save`
2. **List your saves**: Use `GET /api/v1/game/saves/{player_id}`
3. **Load a save**: Use `POST /api/v1/game/load`

### **Character Development Testing**
1. **Add memories**: Use `POST /api/v1/game/memory`
   ```json
   {
     "player_id": "your-player-id",
     "memory_text": "I remember meeting Professor Oak for the first time",
     "memory_type": "relationship"
   }
   ```

2. **Update personality**: Use `POST /api/v1/game/personality`
   ```json
   {
     "player_id": "your-player-id",
     "trait": "courage",
     "value": 8
   }
   ```

## 📊 **Understanding Responses**

### **Game Response Structure**
```json
{
  "player_id": "unique-player-id",
  "player_name": "Your Name",
  "current_story": {
    "id": "story-id",
    "title": "Story Title",
    "content": "Story content...",
    "location": "Current Location"
  },
  "available_choices": [
    {
      "id": "choice-id",
      "text": "Choice description",
      "effects": {"trait": value}
    }
  ],
  "personality_traits": {
    "courage": 5,
    "curiosity": 6,
    "wisdom": 5,
    "determination": 5,
    "friendship": 5
  },
  "memories": [],
  "game_progress": {
    "current_location": "Pallet Town",
    "completed_events": [],
    "relationships": {},
    "inventory": []
  }
}
```

## 🔍 **Troubleshooting**

### **Common Issues**
1. **"Game not found"**: Make sure you're using the correct `player_id`
2. **"Choice not found"**: Use choice IDs from the most recent response
3. **Validation errors**: Check field requirements and data types

### **Testing Tips**
- **Keep track of IDs**: Save `player_id` and `choice_id` values
- **Test incrementally**: Start with basic game flow before advanced features
- **Use examples**: The provided examples are ready to use
- **Check responses**: Always verify the response structure

## 🎯 **API Organization**

### **Game Flow** (Core Gameplay)
- `POST /api/v1/game/start` - Begin your adventure
- `POST /api/v1/game/choice` - Make story decisions

### **Save System** (Progress Management)
- `POST /api/v1/game/save` - Save your progress
- `POST /api/v1/game/load` - Load a saved game
- `GET /api/v1/game/saves/{player_id}` - List all saves

### **Character Development** (Roleplay Features)
- `POST /api/v1/game/memory` - Add character memories
- `POST /api/v1/game/personality` - Update personality traits

### **Game State** (Information)
- `GET /api/v1/game/state/{player_id}` - Get current game state

## 🌟 **Happy Testing!**

Your BeTheMC API now has a comprehensive, user-friendly documentation interface that makes testing and development much easier. The enhanced Swagger UI provides:

- **Clear explanations** of what each endpoint does
- **Practical examples** for all data structures
- **Organized layout** with logical grouping
- **Interactive testing** capabilities
- **Comprehensive validation** and error handling

Enjoy exploring your Pokémon adventure! 🎮✨ 