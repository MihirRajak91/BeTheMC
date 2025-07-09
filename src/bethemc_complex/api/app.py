"""
🎮 FastAPI Application - BeTheMC Complex Architecture

This module creates and configures the main FastAPI application for the
complex architecture version of BeTheMC. It demonstrates enterprise-level
patterns including dependency injection, service layers, and adapter patterns.

🏗️ Architecture Overview:
    ┌─────────────────────────────────────────────────────────────┐
    │                    FastAPI Application                     │
    │  (This Module - Entry Point & Configuration)              │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                    API Routes Layer                         │
    │  • /api/v1/game/start - Initialize new games              │
    │  • /api/v1/game/choice - Process player decisions         │
    │  • /api/v1/game/state/{id} - Retrieve game state          │
    │  • /api/v1/game/save/load - Persistence operations        │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                  Game Manager Layer                         │
    │  • Orchestrates business logic                             │
    │  • Handles dependency injection                            │
    │  • Manages service coordination                            │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                  Service Layer                             │
    │  • GameService - Core game logic                           │
    │  • SaveService - Persistence operations                    │
    │  • DatabaseService - Data access layer                     │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │                  Database Layer                            │
    │  • MongoDB connection management                           │
    │  • Data persistence and retrieval                          │
    │  • Health monitoring and error handling                    │
    └─────────────────────────────────────────────────────────────┘

🎯 Key Features:
    • Enterprise-grade dependency injection
    • Multi-layer service architecture
    • Comprehensive error handling and logging
    • CORS middleware for frontend integration
    • Health checks and monitoring endpoints
    • Automatic API documentation (Swagger/ReDoc)

🔧 Configuration:
    • Database connection lifecycle management
    • CORS middleware for cross-origin requests
    • Request/response middleware for logging
    • Error handling middleware for consistent responses
    • Health check endpoints for monitoring

📋 API Endpoints:
    • GET / - Welcome and architecture information
    • GET /health - System health and database status
    • GET /docs - Interactive API documentation (Swagger)
    • GET /redoc - Alternative API documentation
    • POST /api/v1/game/* - Game management endpoints

🚀 Usage:
    from bethemc_complex.api.app import create_app
    
    # Create the application
    app = create_app()
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

⚠️ Important Notes:
    • This is the complex architecture version - compare with src/bethemc/
    • All database operations are async
    • Comprehensive error handling and logging
    • Designed for enterprise-scale applications
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import the COMPLEX routes with full architecture
from .routes import router as complex_router
from ..database.connection import connect_to_database, disconnect_from_database, database_health_check
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create the FastAPI application with complex architecture.
    
    This version demonstrates:
    - Multiple service layers
    - Complex dependency injection
    - Adapter and interface patterns
    - Separation of concerns
    """
    # Create the app with complex architecture information
    app = FastAPI(
        title="🎮 BeTheMC - Complex Pokémon Adventure API",
        version="1.0.0-COMPLEX",
        description="""
        ## 🏗️ Complex Multi-Layer Pokémon Adventure Game API
        
        **Architecture Features:**
        - Multi-layer service architecture
        - Complex dependency injection patterns
        - Adapter and interface patterns
        - Separated concerns and responsibilities
        
        **API Endpoints:**
        1. POST /api/v1/game/start - Start playing!
        2. POST /api/v1/game/choice - Make choices
        3. GET /api/v1/game/state/{player_id} - Check your progress
        4. POST /api/v1/game/save - Save your game
        5. POST /api/v1/game/load - Load a saved game
        
        **Study this to understand:**
        - How complex enterprise architectures work
        - Dependency injection patterns
        - Service layer separation
        - Adapter and interface patterns
        """,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include the COMPLEX router with full dependency injection
    app.include_router(
        complex_router,
        prefix="/api/v1",
        tags=["Complex Game API"]
    )
    
    # Database connection events
    @app.on_event("startup")
    async def startup_event():
        """Connect to database when app starts."""
        try:
            await connect_to_database()
            logger.info("✅ Complex architecture database connected!")
        except Exception as e:
            logger.error(f"❌ Complex architecture database connection failed: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Disconnect from database when app shuts down."""
        try:
            await disconnect_from_database()
            logger.info("👋 Complex architecture database disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from complex database: {e}")
    
    # Health check with complex architecture details
    @app.get("/health")
    async def health_check():
        """Check if the complex API and database are working."""
        try:
            db_healthy = await database_health_check()
            return {
                "status": "✅ Complex Architecture Healthy" if db_healthy else "⚠️ Database issues",
                "database": "Connected" if db_healthy else "Disconnected",
                "api": "Complex Architecture Running",
                "architecture": "Multi-layer with dependency injection"
            }
        except Exception as e:
            logger.error(f"Complex health check failed: {e}")
            return {
                "status": "❌ Complex Architecture Error",
                "database": "Error",
                "api": "Error",
                "error": str(e)
            }
    
    # Welcome message explaining the complex architecture
    @app.get("/")
    async def welcome():
        """Welcome message explaining the complex architecture."""
        return {
            "message": "🎮 Welcome to BeTheMC - Complex Architecture Version!",
            "version": "1.0.0-COMPLEX",
            "description": "A complex, enterprise-style Pokémon adventure game API",
            
            "🏗️ Architecture Features": {
                "🔧 Dependency Injection": "Full FastAPI dependency system",
                "🏢 Service Layers": "GameManager → GameService → DatabaseService",
                "🔌 Adapters": "Database adapters and interfaces",
                "📦 Separation": "Models split across multiple files",
                "🎯 Enterprise": "Patterns suitable for large teams"
            },
            
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
            
            "📚 Study Guide": {
                "🎯 Purpose": "Compare this complex version with the simplified version",
                "📁 Location": "src/bethemc_complex/ (this version)",
                "🔍 Compare": "src/bethemc/ (simplified version)",
                "💡 Tip": "Study both to understand architectural tradeoffs"
            }
        }
    
    return app


# 🏗️ COMPLEX ARCHITECTURE EXPLANATION:
#
# This app demonstrates enterprise patterns:
# 1. Multiple service layers with clear separation
# 2. Complex dependency injection throughout the system
# 3. Adapter patterns for database operations
# 4. Interface definitions for loose coupling
# 5. Multiple model files for different concerns
#
# Compare this with src/bethemc/api/app.py to see the differences! 