# 🎮 BeTheMC Terminal Pokemon Adventure

A rich, interactive terminal-based Pokemon adventure game featuring anime-style storytelling, personality-driven choices, and AI-powered narrative generation.

## ✨ Features

- **🤖 AI-Powered Storytelling**: Dynamic stories generated using Large Language Models
- **📚 Rich Pokemon World**: 151 Kanto Pokemon with detailed anime-style personalities
- **🎭 Personality System**: Your traits affect story paths and available choices
- **🌟 Dynamic Character Encounters**: May naturally meet Ash, Brock, Misty, and others through your journey
- **💾 MongoDB Save System**: Persistent game saves with cloud storage capabilities
- **🔍 Qdrant Vector Search**: Intelligent story reference and Pokemon knowledge retrieval
- **🎨 Clean Narrative Display**: Pure storytelling without technical formatting
- **📈 Progression Tracking**: Memories, relationships, and character growth

## 🚀 Quick Start

### Easy Way (Recommended)
```bash
python play_game.py
```

The launcher will check all requirements and start the game automatically!

### Manual Way
```bash
python terminal_game.py
```

## 📋 Requirements

- **Python 3.8+**
- **Qdrant Vector Database** (running on localhost:6333)
- **Required Python packages**:
  - langchain
  - qdrant-client
  - sentence-transformers
  - pydantic
  - pyyaml

### Install Requirements
```bash
pip install langchain qdrant-client sentence-transformers pydantic pyyaml
```

### Start Qdrant
Using Docker (recommended):
```bash
docker-compose up -d
```

Or install locally from: https://qdrant.tech/documentation/quick-start/

## 🎮 How to Play

### 1. **Character Creation**
- Choose your trainer name
- Set your personality traits (1-10):
  - **Friendship**: How easily you bond with Pokemon and people
  - **Courage**: Your willingness to face challenges
  - **Curiosity**: Your desire to explore and discover
  - **Wisdom**: Your ability to make thoughtful decisions  
  - **Determination**: Your persistence when facing obstacles

### 2. **Making Choices**
- Read the AI-generated story segments
- Choose from available actions (numbered options)
- Your personality affects what choices are available
- Choices can change your personality traits over time

### 3. **Special Commands**
- **📊 Check Status**: View your traits, location, and progress
- **💾 Save Game**: Save your current progress
- **🚪 Main Menu**: Return to main menu
- **q/quit/exit**: Quick exit to main menu

### 4. **Game Features**
- Stories adapt to your personality and past choices
- Meet Pokemon with unique personalities and behaviors
- Explore iconic Kanto locations with rich descriptions
- Build relationships that matter in the story
- Experience seasonal events and atmosphere

## 🎯 Gameplay Tips

1. **Try Different Personalities**: Each combination creates unique story experiences
2. **Save Often**: Your choices matter, so experiment with different paths
3. **Pay Attention to Personality Changes**: Choices gradually shape your character
4. **Build Relationships**: Bonds with Pokemon and characters unlock new story paths
5. **Explore Thoroughly**: Each location has unique encounters and secrets

## 🛠️ Troubleshooting

### Game Won't Start
- Check that Qdrant is running: `docker-compose up -d`
- Verify all requirements are installed
- Run the launcher: `python play_game.py` for automatic checks

### Missing Pokemon Data
- The game will automatically fetch Kanto data on first run
- If it fails, manually run: `python scripts/fetch_kanto_data.py`

### AI Not Responding
- Check your LLM configuration in `config/default.yaml`
- Ensure the AI model (default: local Ollama) is running
- For Ollama: Make sure it's accessible at the configured API endpoint

### Vector Search Issues  
- Delete and recreate the Qdrant collection if data seems corrupted
- Restart Qdrant: `docker-compose restart`

## 🎨 Game Mechanics

### Personality System
Your five core traits influence:
- Available story choices
- How NPCs react to you
- Pokemon encounter outcomes
- Relationship building speed
- Special event accessibility

### Anime-Style Storytelling
Unlike traditional Pokemon games, this focuses on:
- Emotional bonds and friendships
- Character development and growth
- Fluid, story-driven encounters
- Meaningful choices over combat mechanics
- Atmospheric world-building

### Dynamic Content
- **AI Story Generation**: Each playthrough is unique
- **Contextual Choices**: Options change based on personality and history
- **Adaptive NPCs**: Characters remember your interactions
- **Seasonal Events**: World changes over time
- **Rich Pokemon Personalities**: Each Pokemon has unique traits and behaviors

## 💡 Advanced Features

### Save System
- Multiple save slots per player
- Automatic timestamping
- Full game state preservation
- Cross-session continuity

### Vector Database Integration
- Semantic search through game content
- Context-aware story generation
- Dynamic content retrieval
- Enhanced world knowledge

### Configuration
Customize your experience in `config/default.yaml`:
- AI model settings
- Story generation parameters
- Personality system weights
- Vector database configuration

## 🤝 Contributing

This is an open-source project! Contributions welcome:
- Report bugs via GitHub issues
- Suggest new features or story elements
- Improve AI prompts and personality mechanics
- Add new Pokemon personality data
- Enhance the terminal UI

## 📜 License

Open source - see project license for details.

---

**Enjoy your Pokemon adventure!** 🎉

*Experience the world of Pokemon like never before - through the power of AI storytelling and your unique personality.* 