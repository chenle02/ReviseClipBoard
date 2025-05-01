"""
Tests for the clipboard functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
import pyperclip

@pytest.fixture
def mock_clipboard():
    """Mock clipboard operations."""
    with patch('pyperclip.copy') as mock_copy, \
         patch('pyperclip.paste') as mock_paste:
        mock_paste.return_value = ""
        yield {
            'copy': mock_copy,
            'paste': mock_paste
        }

def test_clipboard_operations(mock_clipboard):
    """Test clipboard operations."""
    # Test setting clipboard content
    test_content = "Test clipboard content"
    pyperclip.copy(test_content)
    mock_clipboard['copy'].assert_called_once_with(test_content)
    
    # Test clearing clipboard
    pyperclip.copy("")
    mock_clipboard['copy'].assert_called_with("")

def test_clipboard_error_handling(mock_clipboard):
    """Test clipboard error handling."""
    mock_clipboard['paste'].side_effect = Exception("Clipboard error")
    with pytest.raises(Exception) as exc_info:
        pyperclip.paste()
    assert str(exc_info.value) == "Clipboard error"

def test_clipboard_unicode(mock_clipboard):
    """Test clipboard with Unicode content."""
    # Test with Unicode characters
    unicode_content = "Hello, 世界! 🌍"
    pyperclip.copy(unicode_content)
    mock_clipboard['copy'].assert_called_once_with(unicode_content)
    
    # Test with emoji
    emoji_content = "Testing emoji: 😊 🎉 🚀"
    pyperclip.copy(emoji_content)
    mock_clipboard['copy'].assert_called_with(emoji_content)

def test_clipboard_large_content(mock_clipboard):
    """Test clipboard with large content."""
    # Create a large string
    large_content = "x" * 1000000  # 1 million characters
    
    # Test copying large content
    pyperclip.copy(large_content)
    mock_clipboard['copy'].assert_called_once_with(large_content)
    
    # Test with multiple lines
    multiline_content = "\n".join(["Line " + str(i) for i in range(1000)])
    pyperclip.copy(multiline_content)
    mock_clipboard['copy'].assert_called_with(multiline_content)

def test_clipboard_special_characters(mock_clipboard):
    """Test clipboard with special characters."""
    # Test with various special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    pyperclip.copy(special_chars)
    mock_clipboard['copy'].assert_called_once_with(special_chars)
    
    # Test with escape sequences
    escape_chars = "\\n\\t\\r\\f\\v"
    pyperclip.copy(escape_chars)
    mock_clipboard['copy'].assert_called_with(escape_chars)

def test_clipboard_multiple_operations(mock_clipboard):
    """Test multiple clipboard operations."""
    # Test multiple copy-paste operations
    contents = [
        "First content",
        "Second content",
        "Third content"
    ]
    
    for content in contents:
        pyperclip.copy(content)
        mock_clipboard['copy'].assert_called_with(content)
    
    # Test overwriting content
    pyperclip.copy("Original content")
    mock_clipboard['copy'].assert_called_with("Original content")
    
    pyperclip.copy("Overwritten content")
    mock_clipboard['copy'].assert_called_with("Overwritten content")
    
    # Test clearing and setting new content
    pyperclip.copy("")
    mock_clipboard['copy'].assert_called_with("")
    
    pyperclip.copy("New content")
    mock_clipboard['copy'].assert_called_with("New content")

def test_clipboard_empty_content(mock_clipboard):
    """Test clipboard with empty content."""
    # Test with empty string
    pyperclip.copy("")
    mock_clipboard['copy'].assert_called_once_with("")
    
    # Test with whitespace
    pyperclip.copy("   ")
    mock_clipboard['copy'].assert_called_with("   ")
    
    # Test with newlines
    pyperclip.copy("\n\n\n")
    mock_clipboard['copy'].assert_called_with("\n\n\n")

def test_clipboard_concurrent_access(mock_clipboard):
    """Test concurrent clipboard access."""
    import threading
    
    def copy_content(content):
        pyperclip.copy(content)
        mock_clipboard['paste'].return_value = content
        assert pyperclip.paste() == content
    
    # Create multiple threads
    threads = []
    contents = [f"Content {i}" for i in range(10)]
    
    for content in contents:
        thread = threading.Thread(target=copy_content, args=(content,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify final clipboard content
    mock_clipboard['paste'].return_value = contents[-1]
    assert pyperclip.paste() in contents

def test_clipboard_platform_specific(mock_clipboard):
    """Test platform-specific clipboard behavior."""
    # Test on Linux
    with patch('platform.system', return_value='Linux'):
        pyperclip.copy("Linux content")
        mock_clipboard['copy'].assert_called_with("Linux content")
    
    # Test on Windows
    with patch('platform.system', return_value='Windows'):
        pyperclip.copy("Windows content")
        mock_clipboard['copy'].assert_called_with("Windows content")
    
    # Test on macOS
    with patch('platform.system', return_value='Darwin'):
        pyperclip.copy("macOS content")
        mock_clipboard['copy'].assert_called_with("macOS content")

def test_clipboard_unsupported_platform(mock_clipboard):
    """Test clipboard on unsupported platform."""
    with patch('platform.system', return_value='Unsupported'):
        mock_clipboard['copy'].side_effect = Exception("Unsupported platform")
        with pytest.raises(Exception) as exc_info:
            pyperclip.copy("Test content")
        assert "Unsupported platform" in str(exc_info.value) 