"""
Configuration management for gpt-clip.

This module handles loading and validation of configuration from both
environment variables and config files.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# XDG Base Directory for configuration
CONFIG_DIR = os.environ.get(
    'XDG_CONFIG_HOME',
    os.path.expanduser('~/.config')
)
CONFIG_PATH = os.path.join(CONFIG_DIR, 'gpt-clip', 'config.json')

class GPTClipConfig(BaseModel):
    """Configuration model for gpt-clip."""
    system_prompt: str = Field(
        default="",
        description="System prompt to be used for all conversations"
    )
    model: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model to use"
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature (0.0-2.0). Lower values (e.g., 0.7) produce more focused and consistent outputs, while higher values (e.g., 1.0) increase creativity and randomness.",
        ge=0.0,
        le=2.0
    )
    log_enabled: bool = Field(
        default=True,
        description="Whether to enable logging"
    )
    log_retention_days: int = Field(
        default=30,
        description="Number of days to retain logs",
        ge=1
    )
    log_format: str = Field(
        default="markdown",
        description="Log format (markdown or plain)",
        pattern="^(markdown|plain)$"
    )

    @classmethod
    def load_config(cls, config_path: str = CONFIG_PATH) -> 'GPTClipConfig':
        """
        Load configuration from file and environment variables.
        Environment variables take precedence over config file.

        Args:
            config_path: Path to the configuration file

        Returns:
            GPTClipConfig: Configuration object

        Raises:
            ValidationError: If config values are invalid
        """
        # Start with empty config
        config_dict: Dict[str, Any] = {}

        # Load from file if it exists
        if os.path.isfile(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    if isinstance(file_config, dict):
                        config_dict.update(file_config)
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing config file: {e}", file=sys.stderr)
                print("Using default configuration", file=sys.stderr)

        # Override with environment variables if they exist
        env_mapping = {
            'GPTCLIP_SYSTEM_PROMPT': 'system_prompt',
            'GPTCLIP_MODEL': 'model',
            'GPTCLIP_TEMPERATURE': 'temperature',
            'GPTCLIP_LOG_ENABLED': 'log_enabled',
            'GPTCLIP_LOG_RETENTION_DAYS': 'log_retention_days',
            'GPTCLIP_LOG_FORMAT': 'log_format'
        }

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                # Convert string to appropriate type
                if config_key in ['log_retention_days']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif config_key == 'temperature':
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                elif config_key == 'log_enabled':
                    value = value.lower() in ('true', '1', 'yes')
                config_dict[config_key] = value

        try:
            return cls(**config_dict)
        except ValidationError as e:
            print(f"Configuration validation error: {e}", file=sys.stderr)
            print("Using default configuration", file=sys.stderr)
            return cls()

    def save_config(self, config_path: str = CONFIG_PATH) -> None:
        """
        Save configuration to file.

        Args:
            config_path: Path to save the configuration file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Save config
        with open(config_path, 'w') as f:
            json.dump(self.model_dump(), f, indent=4)

    @staticmethod
    def create_default_config(config_path: str = CONFIG_PATH) -> None:
        """
        Create a default configuration file if it doesn't exist.

        Args:
            config_path: Path to create the configuration file
        """
        if not os.path.exists(config_path):
            config = GPTClipConfig()
            config.save_config(config_path) 