# gpt-clip

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) [![PyPI version](https://img.shields.io/pypi/v/gpt-clip.svg)](https://pypi.org/project/gpt-clip)

`gpt-clip` is a lightweight command-line tool that sends clipboard content to the OpenAI Chat API and copies the response back to the clipboard.

## Features

- Single-command chat via clipboard content
- Flexible configuration system with multiple sources:
  - Command line arguments (highest priority)
  - Environment variables
  - Configuration file
  - Default values (lowest priority)
- Configurable parameters:
  - System prompt
  - Model selection
  - Temperature control
  - Logging options
- Clipboard-agnostic: uses `pyperclip` (supports xclip, pbcopy, etc.)
- Supports Python 3.7 and above
- Logs each session to a daily Markdown file (`gpt-clip.md`) in your config directory with configurable retention period
- Type-safe configuration with validation

## Prerequisites

- Python 3.7 or higher
- pip
- wheel (`pip install wheel`)
- Python OpenAI client library version >=0.27.7 (`pip install 'openai>=0.27.7'`)
- Linux with `xclip` installed: `sudo apt-get install xclip`
- OpenAI API key

## Installation

### From PyPI

Install the latest release directly from PyPI:

```bash
pip install --upgrade gpt-clip
```

### From source

Clone the repository and install locally:

```bash
git clone https://github.com/chenle02/ReviseClipBoard.git
cd ReviseClipBoard
pip install .
```

For development mode (editable install):
```bash
pip install -e .
```

### Installing via pipx

If you'd like to install `gpt-clip` in an isolated environment using pipx, note that the CLI has been tested with OpenAI client `openai==0.27.7`. To pin the compatible OpenAI version and ensure all dependencies (including `pyperclip`) are installed, follow these steps:

1. (Optional) Uninstall any existing `gpt-clip` installation:
   ```bash
   pipx uninstall gpt-clip || true
   ```
2. Install from your local path, forcing a fresh install and pinning the OpenAI client:
   ```bash
   pipx install --force \
     --spec . \
     --pip-args "openai==0.27.7" \
     gpt-clip
   ```
3. (Optional) To install in editable mode (so local changes take effect immediately):
   ```bash
   pipx install --force \
     --spec . \
     --editable \
     --pip-args "openai==0.27.7" \
     gpt-clip
   ```
4. If you see a warning about missing `pyperclip`, inject it manually:
   ```bash
   pipx inject gpt-clip pyperclip
   ```

This setup creates an isolated virtual environment for `gpt-clip`, installs its dependencies, and pins the OpenAI client to a tested version.

## Configuration

Configuration can be set through multiple sources, with the following priority order:

1. Command line arguments
2. Environment variables
3. Configuration file
4. Default values

### Configuration File

1. Copy the example configuration to your config directory:
   ```bash
   mkdir -p ~/.config/gpt-clip
   cp config.json.example ~/.config/gpt-clip/config.json
   ```
2. Edit `~/.config/gpt-clip/config.json` to set your preferences:
   ```json
   {
     "system_prompt": "You are a helpful and professional assistant. Your task is to revise the user's email, improving clarity, tone, and grammar. The email may include a reply history; please take that into account to ensure the response is appropriate in tone, content, and context.",
     "model": "gpt-4",
     "temperature": 0.7,
     "log_enabled": true,
     "log_retention_days": 30,
     "log_format": "markdown"
   }
   ```

### Environment Variables

You can also configure `gpt-clip` using environment variables. Create a `.env` file in your project directory or set them in your shell:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional configuration
GPTCLIP_SYSTEM_PROMPT="You are a helpful assistant."
GPTCLIP_MODEL=gpt-3.5-turbo
GPTCLIP_TEMPERATURE=0.7  # Lower values (0.7) for more focused outputs, higher values (1.0) for more creative responses
GPTCLIP_LOG_ENABLED=true
GPTCLIP_LOG_RETENTION_DAYS=30
GPTCLIP_LOG_FORMAT=markdown
```

## Usage

Ensure your OpenAI API key is set:
```bash
export OPENAI_API_KEY="<your_api_key>"
```

Copy text to the clipboard and run:
```bash
gpt-clip [options]
```

Options:
```bash
  -c, --config PATH       Path to config JSON file (default: ~/.config/gpt-clip/config.json)
      --model MODEL       Override the model specified in the config file
      --prompt PROMPT     Override the system prompt specified in the config file
      --temperature TEMP  Override the temperature (0.0-2.0)
      --no-log           Disable logging for this run
  -v, --version          Show program version and exit
  -h, --help             Show this help message and exit
```

The response from ChatGPT will be copied back to the clipboard.

## Logging

gpt-clip automatically maintains a log file at `$XDG_CONFIG_HOME/gpt-clip/gpt-clip.md` (default `~/.config/gpt-clip/gpt-clip.md`). Each entry includes:
- **Timestamp**
- **System Prompt**
- **User Input**
- **Reply**
- **Model Name**
- **Temperature**
- **Token Usage** (prompt_tokens, completion_tokens, total_tokens)
- **Response ID**

The log rotates daily and retains entries for the configured number of days (default: 30).

## Integrations

### Awesome WM Keybinding

If you use Awesome Window Manager, you can bind a key to run `gpt-clip` and show the response via a desktop notification. Add the following to your `~/.config/awesome/rc.lua`, adjusting `modkey` and the key binding as desired:

```lua
local gears = require("gears")
local awful = require("awful")

-- Add this inside your globalkeys declaration:
awful.key({ modkey }, "g",
    function()
        awful.spawn.with_shell(
            "gpt-clip && notify-send 'GPT' \"$(xclip -o -selection clipboard)\""
        )
    end,
    {description = "Chat via clipboard and notify result", group = "launcher"}
)

-- After defining your key, ensure you set the new keys table:
root.keys(gears.table.join(globalkeys, /* include the key above */))
```

This setup will:
- Send the current clipboard content to `gpt-clip`.
- Copy the AI response back to the clipboard.
- Display the response in a notification via `notify-send`.

If you're on Wayland with `wl-clipboard`, replace `xclip -o -selection clipboard` with `wl-paste`.

## Troubleshooting

### Configuration Issues

If you encounter configuration-related issues:

1. Check if your configuration file is valid JSON
2. Verify environment variables are set correctly
3. Try running with `--no-log` to disable logging
4. Check the error messages for specific validation errors

### Compatibility with older OpenAI clients

`gpt-clip` auto-detects your OpenAI SDK version:
- If you have `openai>=0.27.0`, it uses the new `OpenAI()` client class.
- Otherwise it falls back to the legacy top-level API (`openai.ChatCompletion.create`).

If you encounter unexpected API errors or want to force the new client, upgrade:

```bash
pip install --upgrade 'openai>=0.27.7'
```

Then, if installed via pipx, reinstall to pick up the updated SDK:

```bash
pipx uninstall gpt-clip || true
pipx install --force \
  --spec . \
  --pip-args "openai==0.27.7" \
  gpt-clip
```

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## Author

Le Chen

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
