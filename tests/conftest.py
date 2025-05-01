"""
Shared test fixtures.
"""
import os
import pytest
from pathlib import Path
from config import GPTClipConfig
import json
from unittest.mock import patch

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary configuration directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create a temporary configuration file."""
    config_file = temp_config_dir / "config.json"
    config = {
        "system_prompt": "test prompt",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "log_enabled": True,
        "log_retention_days": 30,
        "log_format": "markdown"
    }
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables."""
    env_vars = {
        "OPENAI_API_KEY": "test-api-key",
        "GPT_CLIP_SYSTEM_PROMPT": "test env prompt",
        "GPT_CLIP_MODEL": "gpt-4",
        "GPT_CLIP_TEMPERATURE": "0.8"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars 