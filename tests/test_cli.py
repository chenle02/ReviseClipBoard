"""
Tests for the CLI functionality.
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from cli import main, parse_args
from config import GPTClipConfig

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Test response"
    response.usage = {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
    response.id = "test-response-id"
    return response

@pytest.fixture
def mock_config():
    """Mock configuration."""
    return GPTClipConfig(
        system_prompt="test prompt",
        model="gpt-3.5-turbo",
        temperature=0.7,
        log_enabled=True,
        log_retention_days=30,
        log_format="markdown"
    )

def test_parse_args():
    """Test command line argument parsing."""
    with patch('sys.argv', ['gpt-clip', '--model', 'gpt-4', '--prompt', 'test', '--temperature', '0.5', '--no-log']):
        args = parse_args()
        assert args.model == 'gpt-4'
        assert args.prompt == 'test'
        assert args.temperature == 0.5
        assert args.no_log is True

def test_main_success(mock_openai_response, mock_config, tmp_path):
    """Test successful execution of main function."""
    # Mock dependencies
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('pyperclip.copy') as mock_copy, \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('logging.getLogger') as mock_logger:
        
        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Setup logger mock
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        # Run main function
        main()
        
        # Verify OpenAI API call
        mock_client.chat.completions.create.assert_called_once_with(
            model=mock_config.model,
            messages=[
                {'role': 'system', 'content': mock_config.system_prompt},
                {'role': 'user', 'content': 'Test input'}
            ],
            temperature=mock_config.temperature
        )
        
        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")
        
        # Verify logging
        mock_log.info.assert_called_once()

def test_main_empty_clipboard(mock_config):
    """Test handling of empty clipboard."""
    with patch('pyperclip.paste', return_value=""), \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:
        
        main()
        mock_exit.assert_called_once_with(1)

def test_main_api_error(mock_config):
    """Test handling of API errors."""
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:
        
        # Setup OpenAI mock to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        main()
        mock_exit.assert_called_once_with(1)

def test_main_missing_api_key(mock_config):
    """Test handling of missing API key."""
    with patch('os.getenv', return_value=None), \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:
        
        main()
        mock_exit.assert_called_once_with(1)

def test_main_legacy_api(mock_openai_response, mock_config):
    """Test using legacy OpenAI API."""
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('pyperclip.copy') as mock_copy, \
         patch('openai.OpenAI', side_effect=AttributeError), \
         patch('openai.ChatCompletion.create', return_value=mock_openai_response), \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('logging.getLogger') as mock_logger:
        
        # Setup logger mock
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        # Run main function
        main()
        
        # Verify legacy API call
        openai.ChatCompletion.create.assert_called_once_with(
            model=mock_config.model,
            messages=[
                {'role': 'system', 'content': mock_config.system_prompt},
                {'role': 'user', 'content': 'Test input'}
            ],
            temperature=mock_config.temperature
        )
        
        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")
        
        # Verify logging
        mock_log.info.assert_called_once() 