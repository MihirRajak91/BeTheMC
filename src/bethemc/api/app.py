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
        description="An AI-powered Pokémon adventure game with anime-style storytelling",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
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
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to BeTheMC - AI Pokémon Adventure",
            "version": "2.0.0",
            "docs": "/docs",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
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