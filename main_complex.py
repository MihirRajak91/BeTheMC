#!/usr/bin/env python3
"""
Run the BeTheMC API server - COMPLEX ARCHITECTURE VERSION.

This runs the complex, enterprise-style version of the API
for studying advanced architectural patterns.
"""
import uvicorn
from src.bethemc_complex.api.app import create_app
from src.bethemc_complex.utils.logger import get_logger

logger = get_logger(__name__)

# Create the app using the complex architecture
app = create_app()

print("🏗️ COMPLEX ARCHITECTURE SERVER STARTED")
print("📚 This version demonstrates enterprise patterns:")
print("   - Multi-layer service architecture")
print("   - Complex dependency injection")
print("   - Adapter and interface patterns")
print("   - Separated concerns and responsibilities")
print("")
print("🔍 Compare with simplified version by running: python main.py")

if __name__ == "__main__":
    logger.info("Starting BeTheMC Complex Architecture API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,  # Different port from simple version
        reload=False,
        log_level="info"
    ) 