#!/usr/bin/env python3
"""
cli.py: Send clipboard content to OpenAI Chat API and copy response back to clipboard.
"""
import os
import sys
import json

try:
    import pyperclip
except ImportError:
    print("Missing dependency: pyperclip. Install with 'pip install pyperclip'", file=sys.stderr)
    sys.exit(1)

try:
    import openai
except ImportError:
    print("Missing dependency: openai. Install with 'pip install openai'", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config(path=CONFIG_PATH):
    if not os.path.isfile(path):
        print(f"Configuration file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    # Load config
    config = load_config()

    # Set API key and create client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    client = openai.OpenAI(api_key=api_key)

    # Read from clipboard
    clipboard_text = pyperclip.paste()
    if not clipboard_text.strip():
        print("Clipboard is empty or whitespace.", file=sys.stderr)
        sys.exit(1)

    # Prepare messages
    system_prompt = config.get('system_prompt', '')
    model = config.get('model', 'gpt-3.5-turbo')
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': clipboard_text})

    # Call OpenAI API (v1)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
    except Exception as e:
        print(f"OpenAI API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract and copy response
    try:
        reply = response.choices[0].message.content
    except (AttributeError, IndexError) as e:
        print(f"Unexpected API response format: {e}", file=sys.stderr)
        sys.exit(1)

    pyperclip.copy(reply)
    print("Response copied to clipboard.")

if __name__ == '__main__':
    main()