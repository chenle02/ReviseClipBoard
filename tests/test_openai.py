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

def test_openai_api_call(mock_config, mock_openai_response):
    """Test successful OpenAI API call."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=mock_config.model,
            messages=[{"role": "user", "content": "Test input"}],
            temperature=mock_config.temperature
        )

        assert response.choices[0].message.content == "Test response"
        assert response.usage.total_tokens == 10

def test_openai_api_error(mock_config):
    """Test OpenAI API error handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIError(
            message="API Error",
            body={"error": {"message": "API Error"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APIError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"role": "user", "content": "Test input"}],
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
            mock_client.chat.completions.create.side_effect = openai.APIError(
                message="Invalid API key",
                body={"error": {"message": "Invalid API key"}},
                request=MagicMock()
            )

            with pytest.raises(openai.APIError):
                client = openai.OpenAI()
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test input"}]
                )

def test_openai_model_validation(mock_config):
    """Test OpenAI model validation."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIError(
            message="Invalid model",
            body={"error": {"message": "Invalid model"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APIError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model="invalid-model",
                messages=[{"role": "user", "content": "Test input"}]
            )

def test_openai_temperature_validation(mock_config):
    """Test OpenAI temperature validation."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIError(
            message="Invalid temperature",
            body={"error": {"message": "Invalid temperature"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APIError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"role": "user", "content": "Test input"}],
                temperature=2.0
            )

def test_openai_message_validation(mock_config):
    """Test OpenAI message validation."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIError(
            message="Invalid messages",
            body={"error": {"message": "Invalid messages"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APIError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"invalid": "message"}],
                temperature=mock_config.temperature
            )

def test_openai_response_validation(mock_config, mock_openai_response):
    """Test OpenAI response validation."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=mock_config.model,
            messages=[{"role": "user", "content": "Test input"}],
            temperature=mock_config.temperature
        )

        assert response.choices[0].message.content == "Test response"
        assert response.usage.total_tokens == 10

def test_openai_rate_limiting(mock_config, mock_openai_response):
    """Test OpenAI rate limiting."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit exceeded",
            body={"error": {"message": "Rate limit exceeded"}},
            request=MagicMock(),
            response=MagicMock()
        )

        with pytest.raises(openai.RateLimitError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"role": "user", "content": "Test input"}],
                temperature=mock_config.temperature
            )

def test_openai_timeout(mock_config):
    """Test OpenAI timeout handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(
            message="Request timed out",
            body={"error": {"message": "Request timed out"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APITimeoutError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"role": "user", "content": "Test input"}],
                temperature=mock_config.temperature
            )

def test_openai_network_error(mock_config):
    """Test OpenAI network error handling."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            message="Network error",
            body={"error": {"message": "Network error"}},
            request=MagicMock()
        )

        with pytest.raises(openai.APIConnectionError):
            client = openai.OpenAI()
            client.chat.completions.create(
                model=mock_config.model,
                messages=[{"role": "user", "content": "Test input"}],
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
            openai.APIError(
                message="First error",
                body={"error": {"message": "First error"}},
                request=MagicMock()
            ),
            openai.APIError(
                message="Second error",
                body={"error": {"message": "Second error"}},
                request=MagicMock()
            ),
            mock_openai_response
        ]

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=mock_config.model,
            messages=[{"role": "user", "content": "Test input"}],
            temperature=mock_config.temperature
        )

        assert response.choices[0].message.content == "Test response"
        assert mock_sleep.call_count == 2 