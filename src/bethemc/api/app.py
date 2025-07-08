"""
Simple FastAPI Application for BeTheMC

This is the main application file - simplified and easy to understand!
All the complex stuff has been removed to make it crystal clear.
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import our SIMPLE routes instead of complex ones
from .routes import router
from ..database.connection import connect_to_database, disconnect_from_database, database_health_check
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create the FastAPI application.
    
    This is MUCH simpler than before - just the essentials!
    """
    # Create the app with simple, clear information
    app = FastAPI(
        title="🎮 BeTheMC - Simple Pokémon Adventure API",
        version="2.0.0-SIMPLE",
        description="""
        ## 🎯 Simple Pokémon Adventure Game API
        
        **What this API does:**
        - Start new Pokémon adventures
        - Make choices to advance your story
        - Save and load your progress
        - Track your personality and relationships
        
        **How to use:**
        1. POST /api/v1/game/start - Start playing!
        2. POST /api/v1/game/choice - Make choices
        3. GET /api/v1/game/state/{player_id} - Check your progress
        4. POST /api/v1/game/save - Save your game
        5. POST /api/v1/game/load - Load a saved game
        
        **That's it!** Simple and straightforward.
        """,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS so browsers can access the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for simplicity
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include our SIMPLE router
    app.include_router(
        router,  # Use simple router instead of complex router
        prefix="/api/v1",
        tags=["Game API"]
    )
    
    # Database connection events (simplified)
    @app.on_event("startup")
    async def startup_event():
        """Connect to database when app starts."""
        try:
            await connect_to_database()
            logger.info("✅ Database connected successfully!")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Disconnect from database when app shuts down."""
        try:
            await disconnect_from_database()
            logger.info("👋 Database disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from database: {e}")
    
    # Simple health check
    @app.get("/health")
    async def health_check():
        """Check if the API and database are working."""
        try:
            db_healthy = await database_health_check()
            return {
                "status": "✅ Healthy" if db_healthy else "⚠️ Database issues",
                "database": "Connected" if db_healthy else "Disconnected",
                "api": "Working"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "❌ Error",
                "database": "Error",
                "api": "Error",
                "error": str(e)
            }
    
    # Simple welcome message
    @app.get("/")
    async def welcome():
        """Welcome message with all the important links."""
        return {
            "message": "🎮 Welcome to BeTheMC - Simple Pokémon Adventure API!",
            "version": "2.0.0-SIMPLE",
            "description": "A simplified, easy-to-understand Pokémon adventure game API",
            
            "🔗 Important Links": {
                "📖 API Documentation": "/docs",
                "📋 Alternative Docs": "/redoc", 
                "❤️ Health Check": "/health"
            },
            
            "🎯 How to Play": {
                "1️⃣ Start Game": "POST /api/v1/game/start",
                "2️⃣ Make Choices": "POST /api/v1/game/choice",
                "3️⃣ Check Progress": "GET /api/v1/game/state/{player_id}",
                "4️⃣ Save Game": "POST /api/v1/game/save",
                "5️⃣ Load Game": "POST /api/v1/game/load"
            },
            
            "💡 Tip": "Visit /docs to try the API interactively!"
        }
    
    return app


# 🚀 SIMPLE EXPLANATION:
#
# This app does 4 things:
# 1. Creates a FastAPI app with simple, clear documentation
# 2. Adds CORS so browsers can use it
# 3. Connects our simple game routes
# 4. Handles database connections
#
# That's it! Much simpler than the old version. 