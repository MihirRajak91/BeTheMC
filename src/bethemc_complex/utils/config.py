"""
⚙️ Configuration Management - BeTheMC Complex Architecture

This module provides centralized configuration management for the complex
architecture. It handles loading, accessing, and modifying configuration
settings from YAML files with support for nested key access using dot notation.
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    """
    ⚙️ Configuration Manager - YAML-Based Settings Management
    
    This class provides a centralized interface for managing application
    configuration settings. It loads configuration from YAML files and
    provides methods for accessing and modifying settings using dot notation.
    
    Key Features:
    • YAML Configuration: Loads settings from config/default.yaml
    • Dot Notation Access: Use "ai.llm.provider" to access nested settings
    • Type Safety: Maintains original data types from YAML
    • Lazy Loading: Configuration is loaded only when needed
    • Persistence: Changes can be saved back to the configuration file
    
    Usage:
        config = Config()
        llm_provider = config.get("ai.llm.provider", "openai")
        database_url = config.get("database.mongodb.url")
        all_settings = config.get_all()
    """
    
    def __init__(self):
        """
        Initialize the Configuration Manager.
        
        Loads configuration from the default.yaml file located in the
        config directory. The configuration is loaded immediately upon
        initialization to ensure settings are available.
        """
        self.config_path = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        🔍 Get a configuration value using dot notation.
        
        Retrieves a configuration value by traversing nested dictionaries
        using dot-separated keys. Returns the default value if the key
        path doesn't exist.
        
        Args:
            key (str): Dot-separated key path (e.g., "ai.llm.provider")
            default (Any): Default value to return if key not found
        
        Returns:
            Any: Configuration value or default if not found
        
        Examples:
            config.get("ai.llm.provider", "openai")
            config.get("database.mongodb.url")
            config.get("game.default_location", "Pallet Town")
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value

    def get_all(self) -> Dict[str, Any]:
        """
        📋 Get the entire configuration dictionary.
        
        Returns the complete configuration data structure as loaded
        from the YAML file. Useful for debugging or when you need
        access to all configuration settings at once.
        
        Returns:
            Dict[str, Any]: Complete configuration dictionary
        
        Example:
            all_config = config.get_all()
            print(f"Available settings: {list(all_config.keys())}")
        """
        return self.config_data

    def set(self, key: str, value: Any) -> None:
        """
        ✏️ Set a configuration value using dot notation.
        
        Sets a configuration value by traversing nested dictionaries
        using dot-separated keys. Creates intermediate dictionaries
        if they don't exist.
        
        Args:
            key (str): Dot-separated key path (e.g., "ai.llm.provider")
            value (Any): Value to set for the specified key
        
        Example:
            config.set("ai.llm.provider", "anthropic")
            config.set("game.default_location", "Viridian City")
        """
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save(self) -> None:
        """
        💾 Save the current configuration to file.
        
        Writes the current configuration data back to the YAML file.
        This persists any changes made using the set() method.
        
        Raises:
            IOError: If the file cannot be written
        
        Example:
            config.set("ai.llm.provider", "anthropic")
            config.save()  # Persists the change to file
        """
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False) 