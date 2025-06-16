#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/processed
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env with your configuration"
fi

# Start Qdrant
docker-compose up -d

# Load Kanto data
python -m src.scripts.load_data

echo "Setup completed successfully!"
echo "To start the game, run: python -m src.bethemc.core.game" 