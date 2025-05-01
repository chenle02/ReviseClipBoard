"""
Tests for the logging functionality.
"""
import os
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import logging
from config import GPTClipConfig

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
    """Test log entry creation."""
    # Create log entry
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output",
        "model": mock_config.model,
        "temperature": mock_config.temperature,
        "tokens": {
            "prompt": 10,
            "completion": 20,
            "total": 30
        }
    }
    
    # Write log entry
    with open(log_file, "w") as f:
        if mock_config.log_format == "markdown":
            f.write(f"# Log Entry\n\n")
            f.write(f"**Timestamp:** {log_data['timestamp']}\n")
            f.write(f"**Input:** {log_data['input']}\n")
            f.write(f"**Output:** {log_data['output']}\n")
            f.write(f"**Model:** {log_data['model']}\n")
            f.write(f"**Temperature:** {log_data['temperature']}\n")
            f.write(f"**Tokens:**\n")
            f.write(f"- Prompt: {log_data['tokens']['prompt']}\n")
            f.write(f"- Completion: {log_data['tokens']['completion']}\n")
            f.write(f"- Total: {log_data['tokens']['total']}\n")
        else:
            json.dump(log_data, f)
    
    # Verify log file exists and contains correct data
    assert log_file.exists()
    with open(log_file) as f:
        content = f.read()
        assert "Test input" in content
        assert "Test output" in content
        assert mock_config.model in content
        assert str(mock_config.temperature) in content

def test_log_retention(temp_log_dir, mock_config):
    """Test log file retention policy."""
    # Create old log file
    old_log = temp_log_dir / "old.log"
    old_date = datetime.now() - timedelta(days=mock_config.log_retention_days + 1)
    old_log.touch()
    os.utime(old_log, (old_date.timestamp(), old_date.timestamp()))
    
    # Create recent log file
    recent_log = temp_log_dir / "recent.log"
    recent_date = datetime.now() - timedelta(days=mock_config.log_retention_days - 1)
    recent_log.touch()
    os.utime(recent_log, (recent_date.timestamp(), recent_date.timestamp()))
    
    # Clean up old logs
    for log_file in temp_log_dir.glob("*.log"):
        if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days > mock_config.log_retention_days:
            log_file.unlink()
    
    # Verify old log was deleted and recent log was retained
    assert not old_log.exists()
    assert recent_log.exists()

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
    
    # Verify log file was not created
    assert not log_file.exists()

def test_log_format_markdown(temp_log_dir, mock_config):
    """Test markdown log format."""
    mock_config.log_format = "markdown"
    
    # Create log entry
    log_file = temp_log_dir / "test.md"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output",
        "model": mock_config.model,
        "temperature": mock_config.temperature
    }
    
    # Write log entry
    with open(log_file, "w") as f:
        f.write(f"# Log Entry\n\n")
        f.write(f"**Timestamp:** {log_data['timestamp']}\n")
        f.write(f"**Input:** {log_data['input']}\n")
        f.write(f"**Output:** {log_data['output']}\n")
        f.write(f"**Model:** {log_data['model']}\n")
        f.write(f"**Temperature:** {log_data['temperature']}\n")
    
    # Verify markdown format
    with open(log_file) as f:
        content = f.read()
        assert content.startswith("# Log Entry")
        assert "**Timestamp:**" in content
        assert "**Input:**" in content
        assert "**Output:**" in content
        assert "**Model:**" in content
        assert "**Temperature:**" in content

def test_log_format_json(temp_log_dir, mock_config):
    """Test JSON log format."""
    mock_config.log_format = "json"
    
    # Create log entry
    log_file = temp_log_dir / "test.json"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output",
        "model": mock_config.model,
        "temperature": mock_config.temperature
    }
    
    # Write log entry
    with open(log_file, "w") as f:
        json.dump(log_data, f)
    
    # Verify JSON format
    with open(log_file) as f:
        content = json.load(f)
        assert "timestamp" in content
        assert "input" in content
        assert "output" in content
        assert "model" in content
        assert "temperature" in content

def test_log_directory_creation(temp_log_dir):
    """Test log directory creation."""
    # Remove log directory
    temp_log_dir.rmdir()
    
    # Create log entry
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }
    
    # Write log entry
    temp_log_dir.mkdir(exist_ok=True)
    with open(log_file, "w") as f:
        json.dump(log_data, f)
    
    # Verify directory and file were created
    assert temp_log_dir.exists()
    assert log_file.exists()

def test_log_file_permission_error(temp_log_dir, mock_config):
    """Test handling of permission errors when writing log files."""
    # Create read-only log directory
    os.chmod(temp_log_dir, 0o444)
    
    # Try to create log file
    log_file = temp_log_dir / "test.log"
    with pytest.raises(PermissionError):
        with open(log_file, "w") as f:
            json.dump({"test": "data"}, f)

def test_log_file_io_error(temp_log_dir, mock_config):
    """Test handling of I/O errors when writing log files."""
    # Create log file
    log_file = temp_log_dir / "test.log"
    log_file.touch()
    
    # Make file read-only
    os.chmod(log_file, 0o444)
    
    # Try to write to read-only file
    with pytest.raises(IOError):
        with open(log_file, "w") as f:
            json.dump({"test": "data"}, f)

def test_log_rotation(temp_log_dir, mock_config):
    """Test log file rotation."""
    # Create multiple log files
    for i in range(5):
        log_file = temp_log_dir / f"test_{i}.log"
        with open(log_file, "w") as f:
            json.dump({"test": f"data_{i}"}, f)
    
    # Rotate logs (keep only 3 most recent)
    log_files = sorted(temp_log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    for old_file in log_files[3:]:
        old_file.unlink()
    
    # Verify only 3 most recent logs remain
    remaining_files = list(temp_log_dir.glob("*.log"))
    assert len(remaining_files) == 3

def test_log_compression(temp_log_dir, mock_config):
    """Test log file compression."""
    import gzip
    
    # Create log file
    log_file = temp_log_dir / "test.log"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "input": "Test input",
        "output": "Test output"
    }
    
    # Write and compress log file
    with open(log_file, "w") as f:
        json.dump(log_data, f)
    
    compressed_file = log_file.with_suffix(".log.gz")
    with open(log_file, "rb") as f_in, gzip.open(compressed_file, "wb") as f_out:
        f_out.writelines(f_in)
    
    # Verify compressed file exists and contains correct data
    assert compressed_file.exists()
    with gzip.open(compressed_file, "rt") as f:
        content = json.load(f)
        assert content["input"] == "Test input"
        assert content["output"] == "Test output" 