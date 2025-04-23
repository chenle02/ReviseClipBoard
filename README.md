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

## Tips & Integrations

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

