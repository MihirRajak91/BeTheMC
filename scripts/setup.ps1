# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
New-Item -ItemType Directory -Force -Path data\processed
New-Item -ItemType Directory -Force -Path logs

# Copy environment file if it doesn't exist
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from .env.example"
    Write-Host "Please edit .env with your configuration"
}

# Start Qdrant
docker-compose up -d

# Load Kanto data
python -m src.scripts.load_data

Write-Host "Setup completed successfully!"
Write-Host "To start the game, run: python -m src.bethemc.core.game" 