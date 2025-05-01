"""
Tests for the main application functionality.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
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
    """Create a mock OpenAI API response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Test response"
    response.usage = {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
    return response

def test_main_success(mock_config, mock_openai_response):
    """Test successful execution of main function."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.pyperclip.copy') as mock_copy, \
         patch('cli.openai.OpenAI') as mock_openai:
        
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Run main function
        cli.main()
        
        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once_with(
            model=mock_config.model,
            messages=[
                {'role': 'system', 'content': mock_config.system_prompt},
                {'role': 'user', 'content': 'Test input'}
            ],
            temperature=mock_config.temperature
        )

def test_main_empty_clipboard(mock_config):
    """Test main function with empty clipboard."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value=""), \
         patch('cli.sys.exit') as mock_exit:
        
        # Run main function
        cli.main()
        
        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_api_error(mock_config):
    """Test main function with API error."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.openai.OpenAI') as mock_openai, \
         patch('cli.sys.exit') as mock_exit:
        
        # Setup mock OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Run main function
        cli.main()
        
        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_missing_api_key(mock_config):
    """Test main function with missing API key."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.openai.OpenAI', side_effect=ValueError("OPENAI_API_KEY")), \
         patch('cli.sys.exit') as mock_exit:
        
        # Run main function
        cli.main()
        
        # Verify exit was called
        mock_exit.assert_called_once_with(1)

def test_main_legacy_api(mock_config, mock_openai_response):
    """Test main function with legacy OpenAI API."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.pyperclip.copy') as mock_copy, \
         patch('cli.openai.OpenAI') as mock_openai:
        
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Run main function with legacy API
        mock_config.model = "gpt-3.5-turbo"
        cli.main()
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")

def test_parse_args():
    """Test command line argument parsing."""
    # Test default arguments
    with patch('sys.argv', ['cli.py']):
        args = cli.parse_args()
        assert args.temperature == 0.7
        assert args.model == "gpt-3.5-turbo"
        assert args.prompt is None
    
    # Test custom arguments
    with patch('sys.argv', ['cli.py', '--temperature', '0.5', '--model', 'gpt-4', '--prompt', 'Custom prompt']):
        args = cli.parse_args()
        assert args.temperature == 0.5
        assert args.model == "gpt-4"
        assert args.prompt == "Custom prompt"
    
    # Test invalid temperature
    with patch('sys.argv', ['cli.py', '--temperature', '2.0']), \
         patch('sys.exit') as mock_exit:
        cli.parse_args()
        mock_exit.assert_called_once_with(1)
    
    # Test invalid model
    with patch('sys.argv', ['cli.py', '--model', 'invalid-model']), \
         patch('sys.exit') as mock_exit:
        cli.parse_args()
        mock_exit.assert_called_once_with(1)

def test_main_with_custom_prompt(mock_config, mock_openai_response):
    """Test main function with custom prompt."""
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.pyperclip.copy') as mock_copy, \
         patch('cli.openai.OpenAI') as mock_openai, \
         patch('sys.argv', ['cli.py', '--prompt', 'Custom prompt']):
        
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Run main function
        cli.main()
        
        # Verify API call with custom prompt
        mock_client.chat.completions.create.assert_called_once_with(
            model=mock_config.model,
            messages=[
                {'role': 'system', 'content': 'Custom prompt'},
                {'role': 'user', 'content': 'Test input'}
            ],
            temperature=mock_config.temperature
        )
        
        # Verify clipboard operations
        mock_copy.assert_called_once_with("Test response")

def test_main_with_logging_disabled(mock_config, mock_openai_response):
    """Test main function with logging disabled."""
    mock_config.log_enabled = False
    
    with patch('cli.GPTClipConfig', return_value=mock_config), \
         patch('cli.pyperclip.paste', return_value="Test input"), \
         patch('cli.pyperclip.copy') as mock_copy, \
         patch('cli.openai.OpenAI') as mock_openai, \
         patch('cli.logging.info') as mock_logging:
        
        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Run main function
        cli.main()
        
        # Verify logging was not called
        mock_logging.assert_not_called()
        
        # Verify API call and clipboard operations
        mock_client.chat.completions.create.assert_called_once()
        mock_copy.assert_called_once_with("Test response") 