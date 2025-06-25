"""
Main FastAPI application for BeTheMC.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .routes import router
from bethemc.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BeTheMC API",
    description="AI-powered Pokémon adventure game API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to BeTheMC API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

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