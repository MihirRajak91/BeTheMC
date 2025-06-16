"""
Configuration management for the game.
"""
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration manager."""
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        
        # Load environment variables
        self._load_env()
        
        # Load YAML configuration
        self.load_config()

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Create default .env file if it doesn't exist
            self._create_default_env()

    def _create_default_env(self) -> None:
        """Create a default .env file with template values."""
        default_env = """# API Keys
OPENAI_API_KEY=your_key_here
QDRANT_API_KEY=your_key_here

# Database Connection
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Environment
ENV=development
DEBUG=true
"""
        with open('.env', 'w') as f:
            f.write(default_env)
        print("Created default .env file. Please update with your actual values.")

    def load_config(self, config_file: str = "default.yaml") -> None:
        """Load configuration from YAML file."""
        config_path = self.config_dir / config_file
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value, checking environment variables first."""
        # Check environment variable first
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # If not in environment, check config file
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any, persist: bool = False) -> None:
        """Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
            persist: If True, save to .env file
        """
        if persist:
            # Save to .env file
            env_key = key.upper().replace('.', '_')
            with open('.env', 'a') as f:
                f.write(f"\n{env_key}={value}")
            os.environ[env_key] = str(value)
        else:
            # Save to config dictionary
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value

    def save(self, config_file: str = "default.yaml") -> None:
        """Save configuration to YAML file."""
        config_path = self.config_dir / config_file
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values, including environment variables."""
        config = self.config.copy()
        
        # Add environment variables
        for key, value in os.environ.items():
            if key.startswith(('OPENAI_', 'QDRANT_', 'ENV_', 'DEBUG_')):
                config[key.lower()] = value
                
        return config

# Create a global configuration instance
config = ConfigManager() 