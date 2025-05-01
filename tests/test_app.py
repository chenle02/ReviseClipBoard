"""
Tests for the main application functionality.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pyperclip
import openai
import cli
from config import GPTClipConfig

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

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message = MagicMock()
    response.choices[0].message.content = "Test response"
    response.usage = MagicMock()
    response.usage.total_tokens = 10
    return response

def test_main_success(mock_config, mock_openai_response):
    """Test successful execution of main function."""
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('pyperclip.copy') as mock_copy, \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config):

        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        # Run main function
        from cli import main
        main()

        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")

def test_main_empty_clipboard(mock_config):
    """Test handling of empty clipboard."""
    with patch('pyperclip.paste', return_value=""), \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:

        # Run main function
        from cli import main
        main()

        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_api_error(mock_config):
    """Test main function with API error."""
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:

        # Setup mock OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIError(
            message="API Error",
            body={"error": {"message": "API Error"}},
            request=MagicMock()
        )

        # Run main function
        from cli import main
        main()

        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_missing_api_key(mock_config):
    """Test main function with missing API key."""
    with patch('os.getenv', return_value=None), \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('sys.exit') as mock_exit:

        # Run main function
        from cli import main
        main()

        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_legacy_api(mock_config, mock_openai_response):
    """Test main function with legacy OpenAI API."""
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
        from cli import main
        main()

        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")

def test_parse_args():
    """Test command line argument parsing."""
    with patch('sys.argv', ['cli.py', '--temperature', '0.5']):
        from cli import parse_args
        args = parse_args()
        assert args.temperature == 0.5

def test_main_with_custom_prompt(mock_config, mock_openai_response):
    """Test main function with custom system prompt."""
    mock_config.system_prompt = "Custom prompt"
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('pyperclip.copy') as mock_copy, \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config):

        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        # Run main function
        from cli import main
        main()

        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args["messages"][0]["content"] == "Custom prompt"

def test_main_with_logging_disabled(mock_config, mock_openai_response):
    """Test main function with logging disabled."""
    mock_config.log_enabled = False
    with patch('pyperclip.paste', return_value="Test input"), \
         patch('pyperclip.copy') as mock_copy, \
         patch('openai.OpenAI') as mock_openai, \
         patch('config.GPTClipConfig.load_config', return_value=mock_config), \
         patch('logging.getLogger') as mock_logger:

        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        # Run main function
        from cli import main
        main()

        # Verify logging was not called
        mock_logger.assert_not_called() 