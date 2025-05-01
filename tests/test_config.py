"""
Tests for configuration management.
"""
import os
import json
import pytest
from pathlib import Path
from config import GPTClipConfig
from unittest.mock import patch

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
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
    assert config.system_prompt == "You are a helpful assistant that improves text. Fix any spelling, grammar, or punctuation errors. Make the text more concise and clear while preserving its meaning."
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
    assert "Input should be greater than or equal to 1" in str(exc_info.value)

def test_load_config_from_file(temp_config_dir):
    """Test loading configuration from file."""
    config_file = temp_config_dir / "config.json"
    config_data = {
        "system_prompt": "Custom prompt",
        "model": "gpt-4",
        "temperature": 0.5,
        "log_enabled": False,
        "log_retention_days": 15,
        "log_format": "json"
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    config = GPTClipConfig.load_config(config_file)
    assert config.system_prompt == "Custom prompt"
    assert config.model == "gpt-4"
    assert config.temperature == 0.5
    assert config.log_enabled is False
    assert config.log_retention_days == 15
    assert config.log_format == "json"

def test_load_config_from_env():
    """Test loading configuration from environment variables."""
    with patch.dict(os.environ, {
        "GPTCLIP_SYSTEM_PROMPT": "Env prompt",
        "GPTCLIP_MODEL": "gpt-4",
        "GPTCLIP_TEMPERATURE": "0.5",
        "GPTCLIP_LOG_ENABLED": "false",
        "GPTCLIP_LOG_RETENTION_DAYS": "15",
        "GPTCLIP_LOG_FORMAT": "json"
    }):
        config = GPTClipConfig()
        assert config.system_prompt == "Env prompt"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.log_enabled is False
        assert config.log_retention_days == 15
        assert config.log_format == "json"

def test_save_config(temp_config_dir):
    """Test saving configuration to file."""
    config_file = temp_config_dir / "config.json"
    config = GPTClipConfig(
        system_prompt="Test prompt",
        model="gpt-4",
        temperature=0.5,
        log_enabled=False,
        log_retention_days=15,
        log_format="json"
    )
    config.save_config(config_file)

    assert config_file.exists()
    with open(config_file) as f:
        saved_data = json.load(f)
    assert saved_data["system_prompt"] == "Test prompt"
    assert saved_data["model"] == "gpt-4"
    assert saved_data["temperature"] == 0.5
    assert saved_data["log_enabled"] is False
    assert saved_data["log_retention_days"] == 15
    assert saved_data["log_format"] == "json"

def test_create_default_config(temp_config_dir):
    """Test creating default configuration file."""
    config_file = temp_config_dir / "default.json"
    GPTClipConfig.create_default_config(config_file)

    # Verify file exists and content is correct
    assert config_file.exists()
    with open(config_file) as f:
        saved_data = json.load(f)
    assert saved_data["system_prompt"] == "You are a helpful assistant that improves text. Fix any spelling, grammar, or punctuation errors. Make the text more concise and clear while preserving its meaning."
    assert saved_data["model"] == "gpt-3.5-turbo"
    assert saved_data["temperature"] == 0.7
    assert saved_data["log_enabled"] is True
    assert saved_data["log_retention_days"] == 30
    assert saved_data["log_format"] == "markdown"

def test_config_file_not_found(temp_config_dir):
    """Test handling of missing configuration file."""
    config_file = temp_config_dir / "nonexistent.json"
    config = GPTClipConfig.load_config(config_file)
    assert config.system_prompt == "You are a helpful assistant that improves text. Fix any spelling, grammar, or punctuation errors. Make the text more concise and clear while preserving its meaning."
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7
    assert config.log_enabled is True
    assert config.log_retention_days == 30
    assert config.log_format == "markdown"

def test_config_file_permission_error(temp_config_dir):
    """Test handling of permission error when reading configuration file."""
    config_file = temp_config_dir / "config.json"
    with open(config_file, "w") as f:
        f.write('{"test": "data"}')
    os.chmod(config_file, 0o444)

    with pytest.raises(PermissionError):
        GPTClipConfig.load_config(config_file)

def test_config_file_corrupted(temp_config_dir):
    """Test handling of corrupted configuration file."""
    config_file = temp_config_dir / "corrupted.json"
    with open(config_file, "w") as f:
        f.write('{"invalid": "data"}')

    config = GPTClipConfig.load_config(config_file)
    assert config.system_prompt == "You are a helpful assistant that improves text. Fix any spelling, grammar, or punctuation errors. Make the text more concise and clear while preserving its meaning."
    assert config.model == "gpt-3.5-turbo"
    assert config.temperature == 0.7
    assert config.log_enabled is True
    assert config.log_retention_days == 30
    assert config.log_format == "markdown"

def test_config_file_backup(temp_config_dir):
    """Test configuration file backup."""
    config_file = temp_config_dir / "config.json"
    backup_file = temp_config_dir / "config.json.bak"
    config_data = {
        "system_prompt": "Test prompt",
        "model": "gpt-4",
        "temperature": 0.5,
        "log_enabled": False,
        "log_retention_days": 15,
        "log_format": "json"
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    # Create backup
    GPTClipConfig.create_backup(config_file)

    assert backup_file.exists()
    with open(backup_file) as f:
        backup_data = json.load(f)
    assert backup_data == config_data

def test_config_file_encryption(temp_config_dir):
    """Test configuration file encryption."""
    config_file = temp_config_dir / "config.json"
    config_data = {
        "system_prompt": "Test prompt",
        "model": "gpt-4",
        "temperature": 0.5,
        "log_enabled": False,
        "log_retention_days": 15,
        "log_format": "json"
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    # Encrypt file
    GPTClipConfig.encrypt_config(config_file)

    # Verify file is encrypted
    with open(config_file, "rb") as f:
        content = f.read()
    assert content != json.dumps(config_data).encode()

    # Decrypt file
    GPTClipConfig.decrypt_config(config_file)

    # Verify file is decrypted
    with open(config_file) as f:
        decrypted_data = json.load(f)
    assert decrypted_data == config_data 