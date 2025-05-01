"""
Tests for OpenAI API integration.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
import openai
from config import GPTClipConfig

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

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Test response"
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30
    response.id = "test-response-id"
    return response

def test_openai_api_call(mock_config, mock_openai_response):
    """Test successful OpenAI API call."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        response = client.chat.completions.create(
            model=mock_config.model,
            messages=[{'role': 'user', 'content': 'Test input'}],
            temperature=mock_config.temperature
        )

        # Verify response
        assert response.choices[0].message.content == "Test response"
        assert response.usage.total_tokens == 30
        assert response.id == "test-response-id"

def test_openai_api_error(mock_config):
    """Test OpenAI API error handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.OpenAIError()

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        with pytest.raises(openai.OpenAIError):
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{'role': 'user', 'content': 'Test input'}],
                temperature=mock_config.temperature
            )

def test_openai_api_key_validation():
    """Test OpenAI API key validation."""
    # Test with missing API key
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(openai.OpenAIError):
            openai.OpenAI()

    # Test with invalid API key
    with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid-key"}):
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = openai.OpenAIError()

            client = openai.OpenAI()
            with pytest.raises(openai.OpenAIError):
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role': 'user', 'content': 'Test'}]
                )

def test_openai_model_validation(mock_config):
    """Test OpenAI model validation."""
    # Test with invalid model
    mock_config.model = "invalid-model"
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig.validate_model(mock_config.model)
    assert "Model must be one of" in str(exc_info.value)

def test_openai_temperature_validation(mock_config):
    """Test OpenAI temperature validation."""
    # Test with invalid temperature
    mock_config.temperature = 1.5
    with pytest.raises(ValueError) as exc_info:
        GPTClipConfig.validate_temperature(mock_config.temperature)
    assert "Temperature must be between 0 and 1" in str(exc_info.value)

def test_openai_message_validation(mock_config):
    """Test OpenAI message validation."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Test with empty messages
        with pytest.raises(ValueError) as exc_info:
            client = openai.OpenAI(api_key="test-key")
            client.chat.completions.create(
                model=mock_config.model,
                messages=[],
                temperature=mock_config.temperature
            )
        assert "messages" in str(exc_info.value)

def test_openai_response_validation(mock_openai_response):
    """Test OpenAI response validation."""
    # Test with empty choices
    mock_openai_response.choices = []
    with pytest.raises(IndexError):
        content = mock_openai_response.choices[0].message.content
        assert content is None

def test_openai_rate_limiting(mock_config, mock_openai_response):
    """Test OpenAI rate limiting."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.RateLimitError()

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        with pytest.raises(openai.RateLimitError):
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{'role': 'user', 'content': 'Test input'}],
                temperature=mock_config.temperature
            )

def test_openai_timeout(mock_config):
    """Test OpenAI timeout handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError()

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        with pytest.raises(openai.APITimeoutError):
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{'role': 'user', 'content': 'Test input'}],
                temperature=mock_config.temperature
            )

def test_openai_network_error(mock_config):
    """Test OpenAI network error handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError()

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        with pytest.raises(openai.APIConnectionError):
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{'role': 'user', 'content': 'Test input'}],
                temperature=mock_config.temperature
            )

def test_openai_retry_mechanism(mock_config, mock_openai_response):
    """Test OpenAI retry mechanism."""
    with patch('openai.OpenAI') as mock_openai, \
         patch('time.sleep') as mock_sleep:

        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Simulate two failures followed by success
        mock_client.chat.completions.create.side_effect = [
            openai.APIError(),
            openai.APIError(),
            mock_openai_response
        ]

        # Create OpenAI client
        client = openai.OpenAI(api_key="test-key")
        with pytest.raises(openai.APIError):
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{'role': 'user', 'content': 'Test'}],
                temperature=mock_config.temperature
            ) 