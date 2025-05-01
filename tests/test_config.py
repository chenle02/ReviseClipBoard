"""
Tests for configuration management.
"""
import os
import json
import pytest
from pathlib import Path
from config import GPTClipConfig

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
    config_data = {
        "system_prompt": "test prompt",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "log_enabled": True,
        "log_retention_days": 30,
        "log_format": "markdown"
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    return config_file

def test_default_config():
    """Test default configuration values."""
    config = GPTClipConfig()
    assert config.system_prompt == "You are a helpful assistant."
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7
    assert config.log_enabled is True
    assert config.log_retention_days == 30
    assert config.log_format == "markdown"

def test_config_validation():
    """Test configuration validation."""
    # Test invalid temperature
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig(temperature=1.5)
    assert "Temperature must be between 0 and 1" in str(exc_info.value)

    # Test invalid model
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig(model="invalid-model")
    assert "Model must be one of" in str(exc_info.value)

    # Test invalid log format
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig(log_format="invalid-format")
    assert "Log format must be one of" in str(exc_info.value)

    # Test invalid log retention days
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig(log_retention_days=0)
    assert "Log retention days must be at least 1" in str(exc_info.value)

def test_load_config_from_file(temp_config_file):
    """Test loading configuration from file."""
    config = GPTClipConfig.load_config(temp_config_file)
    assert config.system_prompt == "test prompt"
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7
    assert config.log_enabled is True
    assert config.log_retention_days == 30
    assert config.log_format == "markdown"

def test_load_config_from_env():
    """Test loading configuration from environment variables."""
    env_vars = {
        "GPT_CLIP_SYSTEM_PROMPT": "env prompt",
        "GPT_CLIP_MODEL": "gpt-3.5-turbo",
        "GPT_CLIP_TEMPERATURE": "0.5",
        "GPT_CLIP_LOG_ENABLED": "false",
        "GPT_CLIP_LOG_RETENTION_DAYS": "7",
        "GPT_CLIP_LOG_FORMAT": "json"
    }
    with pytest.MonkeyPatch.context() as mp:
        for key, value in env_vars.items():
            mp.setenv(key, value)
        config = GPTClipConfig.load_config()
        assert config.system_prompt == "env prompt"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.log_enabled is False
        assert config.log_retention_days == 7
        assert config.log_format == "json"

def test_save_config(temp_config_dir):
    """Test saving configuration to file."""
    config_file = temp_config_dir / "test_save.json"
    config = GPTClipConfig(
        system_prompt="save test",
        model="gpt-3.5-turbo",
        temperature=0.5
    )
    config.save_config(config_file)

    # Verify file exists and content is correct
    assert config_file.exists()
    with open(config_file) as f:
        saved_data = json.load(f)
    assert saved_data["system_prompt"] == "save test"
    assert saved_data["model"] == "gpt-3.5-turbo"
    assert saved_data["temperature"] == 0.5

def test_create_default_config(temp_config_dir):
    """Test creating default configuration file."""
    config_file = temp_config_dir / "default.json"
    GPTClipConfig.create_default_config(config_file)

    # Verify file exists and content is correct
    assert config_file.exists()
    with open(config_file) as f:
        saved_data = json.load(f)
    assert saved_data["system_prompt"] == "You are a helpful assistant."
    assert saved_data["model"] == "gpt-3.5-turbo"
    assert saved_data["temperature"] == 0.7

def test_config_file_not_found(temp_config_dir):
    """Test handling of missing configuration file."""
    config_file = temp_config_dir / "nonexistent.json"
    config = GPTClipConfig.load_config(config_file)
    assert config.system_prompt == "You are a helpful assistant."
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7

def test_config_file_permission_error(temp_config_file):
    """Test handling of permission errors."""
    # Make file read-only
    os.chmod(temp_config_file, 0o444)

    # Try to save to read-only file
    config = GPTClipConfig()
    config.save_config(temp_config_file)
    assert temp_config_file.exists()

def test_config_file_corrupted(temp_config_dir):
    """Test handling of corrupted configuration file."""
    config_file = temp_config_dir / "corrupted.json"
    with open(config_file, "w") as f:
        f.write('{"invalid": "data"}')

    config = GPTClipConfig.load_config(config_file)
    assert config.system_prompt == "You are a helpful assistant."
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7

def test_config_file_backup(temp_config_dir):
    """Test configuration file backup."""
    config_file = temp_config_dir / "backup_test.json"
    
    # Create initial config
    config = GPTClipConfig(system_prompt="initial")
    config.save_config(config_file)
    
    # Update config
    config.system_prompt = "updated"
    config.save_config(config_file)
    
    # Verify backup exists
    backup_file = config_file.with_suffix(".json.bak")
    assert backup_file.exists()
    with open(backup_file) as f:
        backup_data = json.load(f)
    assert backup_data["system_prompt"] == "initial"

def test_config_file_encryption(temp_config_dir):
    """Test configuration file encryption."""
    config_file = temp_config_dir / "encrypted.json"
    config = GPTClipConfig(
        system_prompt="secret prompt",
        model="gpt-3.5-turbo",
        temperature=0.7
    )

    # Save config without encryption
    config.save_config(config_file, encrypt=False)

    # Verify file exists and is not encrypted
    assert config_file.exists()
    with open(config_file, "rb") as f:
        content = f.read()
    assert content.startswith(b"{")  # Plain JSON 