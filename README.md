# gpt-clip

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) [![PyPI version](https://img.shields.io/pypi/v/gpt-clip.svg)](https://pypi.org/project/gpt-clip)

`gpt-clip` is a lightweight command-line tool that sends clipboard content to the OpenAI Chat API and copies the response back to the clipboard.

## Features

- Single-command chat via clipboard content
- Configurable system prompt & model via JSON
- Clipboard-agnostic: uses `pyperclip` (supports xclip, pbcopy, etc.)
- Supports Python 3.7 and above
  - Logs each session to a daily Markdown file (`gpt-clip.md`) in your config directory with 30-day rotation, capturing prompts, inputs, replies, model, and token usage.

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

1. Copy the example configuration to your config directory:
   ```bash
   mkdir -p ~/.config/gpt-clip
   cp config.json.example ~/.config/gpt-clip/config.json
   ```
2. Edit `~/.config/gpt-clip/config.json` to set your system prompt and model. For example, to revise emails professionally:
   ```json
   {
     "system_prompt": "You are a helpful and professional assistant. Your task is to revise the user's email, improving clarity, tone, and grammar. The email may include a reply history; please take that into account to ensure the response is appropriate in tone, content, and context.",
     "model": "gpt-4.1"
   }
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
      --model MODEL        Override the model specified in the config file
      --prompt PROMPT      Override the system prompt specified in the config file
  -v, --version            Show program version and exit
  -h, --help               Show this help message and exit
```

The response from ChatGPT will be copied back to the clipboard.

## Logging

gpt-clip automatically maintains a Markdown log file at `$XDG_CONFIG_HOME/gpt-clip/gpt-clip.md` (default `~/.config/gpt-clip/gpt-clip.md`). Each entry includes:
- **Timestamp**
- **System Prompt**
- **User Input**
- **Reply**
- **Model Name**
- **Token Usage** (prompt_tokens, completion_tokens, total_tokens)
- **Response ID**

The log rotates daily and retains the last 30 days of entries via timed rotation.

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
</augment_code_snippet>
