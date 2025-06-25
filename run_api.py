#!/usr/bin/env python3
"""
Script to run the BeTheMC FastAPI server.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bethemc.api.app import run_server

if __name__ == "__main__":
    print("🚀 Starting BeTheMC API Server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/api/v1/health")
    print("=" * 50)
    
    try:
        run_server(host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1) 