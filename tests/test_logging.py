"""
Tests for logging functionality.
"""
import os
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from config import GPTClipConfig
from unittest.mock import patch, MagicMock

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary log directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return GPTClipConfig(
        system_prompt="test prompt",
        model="gpt-3.5-turbo",
        temperature=0.7,
        log_enabled=True,
        log_retention_days=30,
        log_format="markdown"
    )

def test_log_creation(temp_log_dir, mock_config):
    """Test log file creation."""
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }

    # Write log entry
    with open(log_file, "w") as f:
        json.dump(log_data, f)

    # Verify log file exists
    assert log_file.exists()

def test_log_rotation(temp_log_dir, mock_config):
    """Test log rotation."""
    # Create old log file
    old_log = temp_log_dir / "old.log"
    old_data = {
        "timestamp": (datetime.now() - timedelta(days=31)).isoformat(),
        "input": "Old input",
        "output": "Old output"
    }
    with open(old_log, "w") as f:
        json.dump(old_data, f)

    # Create new log file
    new_log = temp_log_dir / "new.log"
    new_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "New input",
        "output": "New output"
    }
    with open(new_log, "w") as f:
        json.dump(new_data, f)

    # Run cleanup
    mock_config.cleanup_old_logs(temp_log_dir)

    # Verify old log was deleted
    assert not old_log.exists()
    # Verify new log still exists
    assert new_log.exists()

def test_log_retention(temp_log_dir, mock_config):
    """Test log retention."""
    # Create old log file
    old_log = temp_log_dir / "old.log"
    old_data = {
        "timestamp": (datetime.now() - timedelta(days=31)).isoformat(),
        "input": "Old input",
        "output": "Old output"
    }
    with open(old_log, "w") as f:
        json.dump(old_data, f)

    # Create new log file
    new_log = temp_log_dir / "new.log"
    new_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "New input",
        "output": "New output"
    }
    with open(new_log, "w") as f:
        json.dump(new_data, f)

    # Run cleanup
    mock_config.cleanup_old_logs(temp_log_dir)

    # Verify old log was deleted
    assert not old_log.exists()
    # Verify new log still exists
    assert new_log.exists()

def test_log_format(temp_log_dir, mock_config):
    """Test log format."""
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }

    # Write log entry
    with open(log_file, "w") as f:
        json.dump(log_data, f)

    # Verify log file exists and has correct format
    assert log_file.exists()
    with open(log_file, "r") as f:
        saved_data = json.load(f)
        assert saved_data == log_data

def test_log_disabled(temp_log_dir, mock_config):
    """Test logging when disabled."""
    mock_config.log_enabled = False

    # Create log entry
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }

    # Write log entry
    with open(log_file, "w") as f:
        json.dump(log_data, f)

    # Run cleanup
    mock_config.cleanup_old_logs(temp_log_dir)

    # Verify log file still exists (cleanup should not run when logging is disabled)
    assert log_file.exists()

def test_log_error_handling(temp_log_dir, mock_config):
    """Test log error handling."""
    # Create read-only directory
    os.chmod(temp_log_dir, 0o444)

    # Try to create log file
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }

    # Write log entry should fail
    with pytest.raises(PermissionError):
        with open(log_file, "w") as f:
            json.dump(log_data, f)

    # Verify log file was not created
    assert not log_file.exists()

def test_log_concurrent_access(temp_log_dir, mock_config):
    """Test concurrent access to log files."""
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }

    # Write log entry
    with open(log_file, "w") as f:
        json.dump(log_data, f)

    # Try to write to the same file concurrently
    with pytest.raises(OSError):
        with open(log_file, "w") as f:
            json.dump(log_data, f)

def test_log_cleanup(temp_log_dir, mock_config):
    """Test log cleanup."""
    # Create old log files
    for i in range(5):
        log_file = temp_log_dir / f"old_{i}.log"
        log_data = {
            "timestamp": (datetime.now() - timedelta(days=31)).isoformat(),
            "input": f"Old input {i}",
            "output": f"Old output {i}"
        }
        with open(log_file, "w") as f:
            json.dump(log_data, f)

    # Create new log files
    for i in range(3):
        log_file = temp_log_dir / f"new_{i}.log"
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "input": f"New input {i}",
            "output": f"New output {i}"
        }
        with open(log_file, "w") as f:
            json.dump(log_data, f)

    # Run cleanup
    mock_config.cleanup_old_logs(temp_log_dir)

    # Verify old logs were deleted
    for i in range(5):
        assert not (temp_log_dir / f"old_{i}.log").exists()
    # Verify new logs still exist
    for i in range(3):
        assert (temp_log_dir / f"new_{i}.log").exists() 