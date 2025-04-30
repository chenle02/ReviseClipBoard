#!/usr/bin/env python3
"""
cli.py: Send clipboard content to OpenAI Chat API and copy response back to clipboard.

Copyright (c) 2024 Le Chen (chenle02@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author: Le Chen (chenle02@gmail.com)

This script provides a command-line interface to interact with OpenAI's Chat API using
clipboard content. It reads text from the clipboard, sends it to OpenAI's API, and
copies the response back to the clipboard.

Requirements:
    - pyperclip: For clipboard operations
    - openai: For interacting with OpenAI's API
    - python-dotenv: For environment variable management
    - pydantic: For configuration validation
    - Valid OpenAI API key set in OPENAI_API_KEY environment variable
    - Configuration file in ~/.config/gpt-clip/config.json

Configuration can be set via:
    1. Command line arguments (highest priority)
    2. Environment variables
    3. Configuration file
    4. Default values (lowest priority)
"""
import os
import sys
import json
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
from config import GPTClipConfig, CONFIG_PATH

VERSION = '0.2.3'

def parse_args():
    parser = argparse.ArgumentParser(
        description='Send clipboard content to OpenAI Chat API and copy response back to clipboard.'
    )
    parser.add_argument(
        '-c', '--config',
        default=CONFIG_PATH,
        help=f'Path to config JSON file (default: {CONFIG_PATH})'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {VERSION}'
    )
    parser.add_argument(
        '--model',
        help='Override the model specified in the config file'
    )
    parser.add_argument(
        '--prompt',
        help='Override the system prompt specified in the config file'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        help='Override the temperature (0.0-2.0)'
    )
    parser.add_argument(
        '--no-log',
        action='store_true',
        help='Disable logging for this run'
    )
    return parser.parse_args()

def main():
    """
    Main function that orchestrates the clipboard-to-ChatGPT workflow.

    The function performs the following steps:
    1. Loads configuration from the config file
    2. Initializes OpenAI client (supports both new and legacy API)
    3. Reads text from clipboard
    4. Sends the text to OpenAI's Chat API
    5. Copies the response back to clipboard

    Raises:
        SystemExit: On various error conditions (empty clipboard, API errors, etc.)
    """
    # Parse arguments
    args = parse_args()

    # Import optional dependencies after parsing to allow --help/--version without errors
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

    # Load config
    try:
        config = GPTClipConfig.load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Override config values if provided in command line
    if args.model:
        config.model = args.model
    if args.prompt:
        config.system_prompt = args.prompt
    if args.temperature is not None:
        config.temperature = args.temperature
    if args.no_log:
        config.log_enabled = False

    # Setup logging only if enabled
    if config.log_enabled:
        config_path = os.path.abspath(args.config)
        log_dir = os.path.dirname(config_path)
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'gpt-clip.md')
        logger = logging.getLogger('gpt_clip')
        logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(
            log_path,
            when='D',
            interval=1,
            backupCount=config.log_retention_days
        )
        md_format = (
            "## %(asctime)s\n\n"
            "**System Prompt:**\n%(system_prompt)s\n\n"
            "**User Input:**\n```\n%(user_input)s\n```\n\n"
            "**Reply:**\n```\n%(reply)s\n```\n\n"
            "- **Model:** %(model)s\n"
            "- **Temperature:** %(temperature)s\n"
            "- **Usage:** prompt_tokens: %(usage_prompt_tokens)s, completion_tokens: %(usage_completion_tokens)s, total_tokens: %(usage_total_tokens)s\n"
            "- **Response ID:** %(response_id)s\n"
            "\n---\n"
        )
        formatter = logging.Formatter(md_format, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set API key and initialize OpenAI client (new or legacy)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    # New OpenAI client (v0.27+) uses OpenAI() class
    # Fallback to legacy top-level API if unavailable
    if hasattr(openai, 'OpenAI'):
        client = openai.OpenAI(api_key=api_key)
        use_legacy = False
    else:
        openai.api_key = api_key
        client = openai
        use_legacy = True

    # Read from clipboard
    clipboard_text = pyperclip.paste()
    if not clipboard_text.strip():
        print("Clipboard is empty or whitespace.", file=sys.stderr)
        sys.exit(1)

    # Prepare messages
    messages = []
    if config.system_prompt:
        messages.append({'role': 'system', 'content': config.system_prompt})
    messages.append({'role': 'user', 'content': clipboard_text})

    # Call OpenAI API
    try:
        if use_legacy:
            # Legacy ChatCompletion API
            response = client.ChatCompletion.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature
            )
        else:
            # New client interface
            response = client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature
            )
    except Exception as e:
        print(f"OpenAI API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract and copy response
    try:
        # Both legacy and new client use same response structure
        reply = response.choices[0].message.content
    except (AttributeError, IndexError) as e:
        print(f"Unexpected API response format: {e}", file=sys.stderr)
        sys.exit(1)

    pyperclip.copy(reply)
    print(reply)
    print("Response copied to clipboard.")

    # Log the interaction in markdown
    if config.log_enabled:
        try:
            usage_raw = getattr(response, 'usage', None)
            if usage_raw is None and isinstance(response, dict):
                usage_raw = response.get('usage')
            usage = dict(usage_raw) if usage_raw else {}
        except Exception:
            usage = {}
        try:
            response_id = getattr(response, 'id', None)
            if response_id is None and isinstance(response, dict):
                response_id = response.get('id')
        except Exception:
            response_id = ''
        prompt_tokens = usage.get('prompt_tokens', '')
        completion_tokens = usage.get('completion_tokens', '')
        total_tokens = usage.get('total_tokens', '')
        log_extra = {
            'system_prompt': config.system_prompt,
            'user_input': clipboard_text,
            'reply': reply,
            'model': config.model,
            'temperature': config.temperature,
            'usage_prompt_tokens': prompt_tokens,
            'usage_completion_tokens': completion_tokens,
            'usage_total_tokens': total_tokens,
            'response_id': response_id or '',
        }
        logger.info('', extra=log_extra)


if __name__ == '__main__':
    main()
