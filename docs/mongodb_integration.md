# MongoDB Integration for BeTheMC

## Overview

BeTheMC now uses MongoDB as the primary storage backend for player IDs, game states, and save data. This replaces the previous in-memory storage system, providing persistent, scalable, and reliable data storage.

## Architecture Changes

### Before (In-Memory Storage)
- Player IDs and game states stored in `GameManager.active_games` class variable
- Data lost on server restart
- No persistence across sessions
- Limited to single server instance

### After (MongoDB Storage)
- Player IDs and game states stored in MongoDB collections
- Data persists across server restarts
- Scalable across multiple server instances
- Automatic backup and recovery capabilities

## Database Schema

### Collections

#### 1. **players** - Player Information
```json
{
  "_id": ObjectId,
  "player_id": "uuid-string",
  "name": "Player Name",
  "personality_traits": {
    "friendship": 5,
    "courage": 5,
    "curiosity": 5,
    "wisdom": 5,
    "determination": 5
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### 2. **game_states** - Current Game State
```json
{
  "_id": ObjectId,
  "player_id": "uuid-string",
  "current_story": {
    "id": "story-uuid",
    "title": "Story Title",
    "content": "Story content...",
    "location": "Pallet Town"
  },
  "available_choices": [
    {
      "id": "choice-uuid",
      "text": "Visit Professor Oak's lab",
      "effects": {"curiosity": 1}
    }
  ],
  "memories": [
    {
      "id": "memory-uuid",
      "content": "Important memory...",
      "memory_type": "friendship",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "progression": {
    "current_location": "Pallet Town",
    "completed_events": [],
    "relationships": {},
    "inventory": []
  },
  "last_updated": "2024-01-01T12:00:00Z"
}
```

#### 3. **saves** - Save Game Data
```json
{
  "_id": ObjectId,
  "save_id": "save-uuid",
  "player_id": "uuid-string",
  "save_name": "My Adventure Save",
  "game_state": {/* Full game state object */},
  "save_type": "full",
  "created_at": "2024-01-01T12:00:00Z",
  "file_size_bytes": 12345
}
```

## Installation & Setup

### 1. Install Dependencies

The MongoDB dependencies are already added to `pyproject.toml`:

```bash
poetry install
```

Dependencies added:
- `motor ^3.3.0` - Async MongoDB driver
- `pymongo ^4.6.0` - MongoDB Python driver

### 2. Start MongoDB with Docker

```bash
# Start MongoDB and Qdrant services
docker-compose up -d

# Verify MongoDB is running
docker ps
```

The MongoDB service includes:
- **Port**: 27017
- **Username**: admin
- **Password**: password
- **Database**: bethemc
- **Data Volume**: `./mongodb_data`

### 3. Configuration

MongoDB settings in `src/bethemc/config/settings.py`:

```python
# MongoDB Settings
MONGODB_URL: str = "mongodb://admin:password@localhost:27017/bethemc?authSource=admin"
MONGODB_DATABASE: str = "bethemc"
MONGODB_COLLECTION_PLAYERS: str = "players"
MONGODB_COLLECTION_GAMES: str = "game_states"
MONGODB_COLLECTION_SAVES: str = "saves"
```

### 4. Environment Variables (Optional)

You can override settings using environment variables:

```bash
# .env file
MONGODB_URL=mongodb://admin:password@localhost:27017/bethemc?authSource=admin
MONGODB_DATABASE=bethemc
```

## How Player IDs Are Now Stored

### Player ID Lifecycle

1. **Game Start**: 
   ```python
   # Generate UUID for new player
   player = Player(id=str(uuid4()), name=player_name, ...)
   
   # Save to MongoDB players collection
   await db_service.save_player(player)
   
   # Save initial game state to game_states collection
   await db_service.save_game_state(game_state)
   ```

2. **Choice Processing**:
   ```python
   # Retrieve game state from MongoDB
   game_state = await db_service.get_game_state(player_id)
   
   # Process choice and update state
   updated_state = await game_service.process_choice(game_state, choice_id)
   
   # Save updated state back to MongoDB
   await db_service.save_game_state(updated_state)
   ```

3. **Save/Load Operations**:
   ```python
   # Save game to saves collection
   save_id = await db_service.save_game(game_state, save_name)
   
   # Load game from saves collection
   game_state = await db_service.load_game(player_id, save_id)
   ```

### Database Service Methods

The `DatabaseService` class provides all MongoDB operations:

```python
# Player operations
await db_service.save_player(player)
player = await db_service.get_player(player_id)
exists = await db_service.player_exists(player_id)

# Game state operations
await db_service.save_game_state(game_state)
game_state = await db_service.get_game_state(player_id)

# Save/load operations
save_id = await db_service.save_game(game_state, save_name)
game_state = await db_service.load_game(player_id, save_id)
saves = await db_service.get_player_saves(player_id)
await db_service.delete_save(save_id)
```

## API Changes

### No Breaking Changes
All existing API endpoints work the same way:
- `POST /api/v1/game/start`
- `POST /api/v1/game/choice`
- `GET /api/v1/game/state/{player_id}`
- `POST /api/v1/game/save`
- `POST /api/v1/game/load`
- `GET /api/v1/game/saves/{player_id}`

### Enhanced Health Check
The health check endpoint now includes database status:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "database": "connected"
}
```

## Testing

### 1. Test MongoDB Integration

Run the test script to verify everything works:

```bash
python scripts/test_mongodb.py
```

Expected output:
```
🚀 Starting MongoDB integration tests...
✅ Connected to MongoDB
✅ Database health check passed
✅ Player saved successfully
✅ Player retrieved successfully
✅ Game state saved successfully
✅ Game state retrieved successfully
✅ Game saved successfully with save_id: abc123...
✅ Game loaded successfully
✅ Retrieved 1 saves for player
✅ All database operations completed successfully
🎉 All MongoDB integration tests passed!
```

### 2. Test API Endpoints

```bash
# Start the API server
python run_api.py

# Test game start
curl -X POST "http://localhost:8000/api/v1/game/start" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "TestPlayer"}'

# Test choice (use player_id from start response)
curl -X POST "http://localhost:8000/api/v1/game/choice" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "YOUR_PLAYER_ID", "choice_id": "CHOICE_ID"}'
```

## Benefits of MongoDB Integration

### 1. **Persistence**
- Game states survive server restarts
- Players can resume games anytime
- Data is safely stored and backed up

### 2. **Scalability**
- Multiple server instances can share the same database
- Horizontal scaling capabilities
- No memory limitations for game states

### 3. **Performance**
- Indexed queries for fast player lookups
- Efficient storage and retrieval
- Async operations don't block the API

### 4. **Reliability**
- ACID transactions for data consistency
- Automatic failover and replication (in production)
- Backup and restore capabilities

### 5. **Analytics**
- Query player behavior patterns
- Analyze choice statistics
- Monitor game progression

## Development Notes

### Database Lifecycle
- **Startup**: FastAPI connects to MongoDB automatically
- **Runtime**: All operations use async MongoDB client
- **Shutdown**: FastAPI disconnects gracefully

### Error Handling
- Connection failures are logged and handled gracefully
- Database errors return proper HTTP status codes
- Health check endpoint monitors database status

### Performance Considerations
- Uses connection pooling for efficiency
- Indexes on `player_id` fields for fast lookups
- Async operations prevent blocking

## Migration from In-Memory Storage

The migration is seamless:
1. Old in-memory `GameManager.active_games` is removed
2. All operations now use `DatabaseService`
3. No changes to API contracts
4. Existing clients continue to work

## Monitoring & Maintenance

### 1. **Database Health**
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check MongoDB directly
docker exec -it $(docker ps -q -f name=mongodb) mongosh -u admin -p password
```

### 2. **Data Backup**
```bash
# Backup MongoDB data
docker exec $(docker ps -q -f name=mongodb) mongodump -u admin -p password --authenticationDatabase admin --out /backup

# Copy backup from container
docker cp $(docker ps -q -f name=mongodb):/backup ./mongodb_backup
```

### 3. **Performance Monitoring**
```bash
# View MongoDB logs
docker logs $(docker ps -q -f name=mongodb)

# Monitor database operations
# Use MongoDB Compass or similar tools
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: pymongo.errors.ServerSelectionTimeoutError
   ```
   - Ensure MongoDB container is running: `docker-compose up -d`
   - Check connection string in settings

2. **Authentication Failed**
   ```
   Error: pymongo.errors.OperationFailure: Authentication failed
   ```
   - Verify username/password in connection string
   - Ensure authSource=admin is included

3. **Database Not Found**
   ```
   Error: Database 'bethemc' not found
   ```
   - MongoDB creates databases automatically
   - Check database name in settings

### Debug Commands

```bash
# Check MongoDB container status
docker ps | grep mongodb

# View MongoDB logs
docker logs $(docker ps -q -f name=mongodb)

# Connect to MongoDB shell
docker exec -it $(docker ps -q -f name=mongodb) mongosh -u admin -p password

# List databases
show databases

# Use bethemc database
use bethemc

# List collections
show collections

# Count documents
db.players.countDocuments()
db.game_states.countDocuments()
db.saves.countDocuments()
```

## Next Steps

1. **Production Deployment**: 
   - Use MongoDB Atlas or dedicated MongoDB server
   - Enable authentication and SSL
   - Set up replication and backups

2. **Optimization**:
   - Add database indexes for better performance
   - Implement caching for frequently accessed data
   - Monitor and optimize query performance

3. **Features**:
   - Add player analytics and statistics
   - Implement data migration tools
   - Add admin tools for game management 