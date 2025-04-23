Purpose:

Use OpenAI API to send the clipboard content to ChatGPT and get a response. The response is then copied to the clipboard.

Setup the configuration in a json file, specifying the system prompt and model.

Prerequisites:
- Python 3.7+
- pip
- Linux with xclip installed (`sudo apt-get install xclip`)

Installation:
```bash
pip install -r requirements.txt
```

Configuration:
1. Copy `config.json.example` to `config.json`.
2. Edit `config.json` to set your desired `system_prompt` and `model`.

Usage:
```bash
# Ensure your OpenAI API key is set:
export OPENAI_API_KEY="your_api_key_here"

# Copy text to clipboard, then run:
python cli.py

# The response from ChatGPT will be copied back to your clipboard.
```

