#!/usr/bin/env python3
"""
Run the BeTheMC API server.
"""
import uvicorn
from src.bethemc.api.app import app
from src.bethemc.utils.logger import get_logger

logger = get_logger(__name__)

print("SERVER STARTED")

if __name__ == "__main__":
    logger.info("Starting BeTheMC API server...")
    uvicorn.run(
        "src.bethemc.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 