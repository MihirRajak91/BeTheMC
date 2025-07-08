"""
Configuration management for the game.
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    def __init__(self):
        """Initialize configuration from default.yaml."""
        self.config_path = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value

    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self.config_data

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save(self) -> None:
        """Save the current configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False) 