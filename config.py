"""
Configuration management module for GPT-Clip.
"""
import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Default configuration path
CONFIG_PATH = os.path.expanduser("~/.config/gpt-clip/config.json")

class GPTClipConfig(BaseModel):
    """Configuration model for GPT-Clip."""
    system_prompt: str = Field(default="You are a helpful assistant.")
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)
    log_enabled: bool = Field(default=True)
    log_retention_days: int = Field(default=30)
    log_format: str = Field(default="markdown")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        """Validate model name."""
        valid_models = ["gpt-3.5-turbo", "gpt-4"]
        if v not in valid_models:
            raise ValueError(f"Model must be one of: {', '.join(valid_models)}")
        return v

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ["markdown", "json"]
        if v not in valid_formats:
            raise ValueError(f"Log format must be one of: {', '.join(valid_formats)}")
        return v

    @field_validator("log_retention_days")
    @classmethod
    def validate_log_retention_days(cls, v):
        """Validate log retention days."""
        if v < 1:
            raise ValueError("Log retention days must be at least 1")
        return v

    @classmethod
    def load_config(cls, config_path: Optional[str | Path] = None) -> "GPTClipConfig":
        """Load configuration from file and environment variables."""
        config_path = Path(config_path or CONFIG_PATH)
        config_data = {}

        # Load from file if exists
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)

        # Override with environment variables if set
        env_mapping = {
            "GPT_CLIP_SYSTEM_PROMPT": "system_prompt",
            "GPT_CLIP_MODEL": "model",
            "GPT_CLIP_TEMPERATURE": "temperature",
            "GPT_CLIP_LOG_ENABLED": "log_enabled",
            "GPT_CLIP_LOG_RETENTION_DAYS": "log_retention_days",
            "GPT_CLIP_LOG_FORMAT": "log_format"
        }

        for env_var, config_key in env_mapping.items():
            if env_value := os.getenv(env_var):
                if config_key in ["temperature", "log_retention_days"]:
                    config_data[config_key] = float(env_value)
                elif config_key == "log_enabled":
                    config_data[config_key] = env_value.lower() == "true"
                else:
                    config_data[config_key] = env_value

        return cls(**config_data)

    def save_config(self, config_path: Optional[str | Path] = None, encrypt: bool = False):
        """Save configuration to file."""
        config_path = Path(config_path or CONFIG_PATH)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if file exists
        if config_path.exists():
            backup_path = config_path.with_suffix(".json.bak")
            config_path.rename(backup_path)

        # Save configuration
        config_data = self.model_dump()
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)

    @classmethod
    def create_default_config(cls, config_path: Optional[str | Path] = None):
        """Create default configuration file."""
        config = cls()
        config.save_config(config_path) 