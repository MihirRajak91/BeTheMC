"""
Main FastAPI application for BeTheMC.
"""
from fastapi import (
    FastAPI, 
    Depends, 
    Request, 
    HTTPException, 
    status,
    Response,
    Security
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import (
    HTTPBearer, 
    HTTPAuthorizationCredentials
)
from fastapi.middleware import Middleware
from fastapi.routing import APIRoute
from typing import Callable, List, Optional, Set, Type, Dict, Any, Union
import uvicorn
import re

from .routes import router as api_router
from bethemc.utils.logger import setup_logger
from .game_manager import get_game_manager
from ..services.game_service import GameService
from ..services.save_service import SaveService
from ..utils.logger import get_logger
from ..auth.service import verify_token, ALGORITHM
from ..config import settings

# Security
security = HTTPBearer()

# Simple HTML response for Swagger UI redirect
def get_swagger_redirect_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI - Redirect</title>
    </head>
    <body>
        <p>Redirecting back to Swagger UI...</p>
        <script>
            if (window.opener) {
                window.close();
            }
        </script>
    </body>
    </html>
    """

# List of paths that don't require authentication
PUBLIC_PATHS = {
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/auth/token",
    "/auth/token/",
    "/auth/login",
    "/auth/login/",
    "/auth/register",
    "/auth/register/",
    "/auth/auth/register",  # For backward compatibility
    "/auth/auth/register/",  # For backward compatibility
    "/auth/users",
    "/auth/users/",
    "/auth/users/*"  # This will match any path that starts with /auth/users/
}

class AuthMiddleware:
    """Middleware to handle authentication for all endpoints."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        request = Request(scope, receive)
        
        # Skip authentication for public paths
        if request.url.path in PUBLIC_PATHS or any(
            request.url.path.startswith(public_path.rstrip('*')) 
            for public_path in PUBLIC_PATHS if public_path.endswith('*')
        ):
            return await self.app(scope, receive, send)
            
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
            
        # Verify the token
        try:
            token = auth_header.split(" ")[1]
            logger.info(f"Verifying token: {token[:10]}...")  # Log first 10 chars of token
            # Specify token_type="access" since this is for API access
            token_data = verify_token(token, token_type="access")
            logger.info(f"Token verified successfully for user: {token_data.username}")
            # Attach user info to request state
            request.state.user = token_data
        except HTTPException as e:
            logger.error(f"Token verification failed: {str(e)}")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e.detail)},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
            
        return await self.app(scope, receive, send)

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create the app with middleware
    app = FastAPI(
        title="BeTheMC - AI Pokémon Adventure",
        version="1.0.0",
        description="""BeTheMC API - AI-Powered Pokémon Adventure Game
        
        ## Authentication
        
        1. Use the `/auth/login` endpoint to get an access token
        2. Click the **Authorize** button (🔒) in the top right
        3. Enter: `Bearer your_access_token_here`
        
        All authenticated endpoints will automatically use this token.
        """,
        contact={
            "name": "BeTheMC Development Team",
            "email": "support@bethemc.com",
            "url": "https://github.com/your-repo/bethemc"
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        openapi_tags=[
            {
                "name": "auth",
                "description": "Authentication and user management"
            },
            {
                "name": "game",
                "description": "Game operations"
            },
            {
                "name": "items",
                "description": "Item management"
            }
        ],
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add route for Swagger UI redirect
    @app.get("/docs/redirect", include_in_schema=False)
    async def swagger_ui_redirect():
        return HTMLResponse(content=get_swagger_redirect_html())
        
    # Add security scheme to OpenAPI
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    
    # Add authentication middleware
    app.add_middleware(AuthMiddleware)
    
    from .routes import router as api_router
    from ..auth.routes import router as auth_router
    
    # Include the auth router
    app.include_router(auth_router)
    
    # Include the API router
    app.include_router(
        api_router,
        prefix="/api/v1",
        tags=["game"]
    )
    
    # Health check endpoint
    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "ok"}
        
    # Startup event to initialize database connection
    @app.on_event("startup")
    async def startup_db_client():
        from ..database import mongodb
        try:
            await mongodb.connect()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    # Shutdown event to close database connection
    @app.on_event("shutdown")
    async def shutdown_db_client():
        from ..database import mongodb
        await mongodb.close()
        logger.info("Closed MongoDB connection")
        
    @app.get("/",
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