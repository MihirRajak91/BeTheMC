"""
Main FastAPI application for BeTheMC.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .routes import router
from bethemc.utils.logger import setup_logger
from .game_manager import get_game_manager
from ..services.game_service import GameService
from ..services.save_service import SaveService
from ..utils.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="BeTheMC - AI Pokémon Adventure",
        description="""
        # 🎮 BeTheMC - AI-Powered Pokémon Adventure Game
        
        Welcome to BeTheMC, an interactive AI-powered Pokémon adventure game! 
        Experience a dynamic story that adapts to your choices and personality.
        
        ## 🚀 Quick Start
        
        1. **Start a Game**: Use `/api/v1/game/start` to begin your adventure
        2. **Make Choices**: Use `/api/v1/game/choice` to advance the story
        3. **Save Progress**: Use `/api/v1/game/save` to save your game
        4. **Load Games**: Use `/api/v1/game/load` to continue from a save point
        
        ## 🎯 How It Works
        
        - **Dynamic Storytelling**: The AI generates unique story content based on your choices
        - **Personality System**: Your character's traits (courage, curiosity, wisdom, etc.) affect the story
        - **Memory System**: Add memories that influence future story events
        - **Progressive Adventure**: Your choices build a unique adventure path
        
        ## 🛠️ Testing the API
        
        All endpoints include examples and detailed descriptions. You can:
        - Click "Try it out" on any endpoint
        - Use the provided examples as starting points
        - See the full request/response schemas
        
        ## 📚 API Endpoints
        
        ### Core Game Flow
        - `POST /api/v1/game/start` - Start a new adventure
        - `POST /api/v1/game/choice` - Make choices to advance the story
        - `GET /api/v1/game/state/{player_id}` - Get current game state
        
        ### Save System
        - `POST /api/v1/game/save` - Save your progress
        - `POST /api/v1/game/load` - Load a saved game
        - `GET /api/v1/game/saves/{player_id}` - List all saves
        
        ### Character Development
        - `POST /api/v1/game/memory` - Add memories to your character
        - `POST /api/v1/game/personality` - Update personality traits
        
        ## 🔧 Technical Details
        
        - **Framework**: FastAPI with automatic OpenAPI documentation
        - **State Management**: In-memory game state with class-level persistence
        - **Validation**: Pydantic models with comprehensive validation
        - **Error Handling**: Detailed error messages and proper HTTP status codes
        
        ## 🎮 Example Game Session
        
        1. Start a game with your name
        2. Read the story and available choices
        3. Make a choice to advance the story
        4. See how your personality traits change
        5. Continue making choices to build your unique adventure!
        
        Happy adventuring! 🌟
        """,
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={
            "name": "BeTheMC Development Team",
            "url": "https://github.com/your-repo/bethemc",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        tags_metadata=[
            {
                "name": "Game Flow",
                "description": "Core game progression endpoints for starting games and making choices.",
            },
            {
                "name": "Save System", 
                "description": "Endpoints for saving and loading game progress.",
            },
            {
                "name": "Character Development",
                "description": "Endpoints for managing character memories and personality traits.",
            },
            {
                "name": "Game State",
                "description": "Endpoints for retrieving current game information.",
            },
        ]
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    @app.get(
        "/",
        summary="Welcome",
        description="Welcome endpoint with API information and links to documentation.",
        tags=["Info"]
    )
    async def root():
        return {
            "message": "Welcome to BeTheMC - AI Pokémon Adventure",
            "version": "2.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "status": "running",
            "quick_start": {
                "start_game": "POST /api/v1/game/start?player_name=YourName",
                "make_choice": "POST /api/v1/game/choice with player_id and choice_id",
                "get_state": "GET /api/v1/game/state/{player_id}"
            }
        }
    
    @app.get(
        "/health",
        summary="Health Check",
        description="Simple health check endpoint to verify the API is running.",
        tags=["Info"]
    )
    async def health_check():
        return {
            "status": "healthy",
            "service": "BeTheMC API",
            "version": "2.0.0"
        }
    
    return app

# Create the app instance
app = create_app()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run the FastAPI server."""
    logger.info(f"Starting BeTheMC API server on {host}:{port}")
    uvicorn.run(
        "bethemc.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_server() 