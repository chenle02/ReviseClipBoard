# gpt-clip

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

`gpt-clip` is a lightweight command-line tool that sends your clipboard contents to the OpenAI Chat API and copies the response back to the clipboard.

## Features

- Single-command chat via clipboard
- Configurable system prompt & model via JSON
- Clipboard-agnostic: uses `pyperclip` (supports xclip, pbcopy, etc.)
- Supports Python 3.7 and above

## Prerequisites

- Python 3.7 or higher
- pip
- wheel (`pip install wheel`)
- Linux with `xclip` installed: `sudo apt-get install xclip`
- OpenAI API key

## Installation

Clone the repository and install locally:
```bash
git clone https://github.com/<username>/ReviseClipBoard.git
cd ReviseClipBoard
pip install .
```

For development mode (editable install):
```bash
pip install -e .
```

## Configuration

1. Copy the example configuration to your config directory:
   ```bash
   mkdir -p ~/.config/gpt-clip
   cp config.json.example ~/.config/gpt-clip/config.json
   ```
2. Edit `~/.config/gpt-clip/config.json` to set your system prompt and model:
   ```json
   {
     "system_prompt": "You are a helpful assistant.",
     "model": "gpt-3.5-turbo"
   }
   ```

## Usage

Ensure your OpenAI API key is set:
```bash
export OPENAI_API_KEY="<your_api_key>"
```

Copy text to your clipboard and run:
```bash
gpt-clip
```

The response from ChatGPT will be copied back to your clipboard.

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## Author

Le Chen

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

