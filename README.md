# JARVIS

**A desktop AI assistant powered by KoboldCpp / OpenAI API.**

JARVIS is a beginner-friendly, modular AI assistant with dynamic tool plugins,
multi-step chaining, and desktop automation. It connects to any
OpenAI-compatible backend (KoboldCpp, vLLM, etc.) to serve
open-source language models.

---

## Features

### Core
- **OpenAI-compatible backend** — Connects to KoboldCpp, vLLM, or any OpenAI-compatible API.
- **Remote AI server** — Run the AI on a separate machine on your LAN.
- **Configurable models** — Switch models anytime via `.env` or `config.json`.
- **Gemma 4 12B support** — Defaults to `koboldcpp/gemma-4-12b-it-qat-q4_0`.
- **Streaming responses** — See tokens appear in real time.
- **Persistent memory** — Conversations, facts, and preferences saved to disk.
- **40+ tools** — Web, system, files, weather, desktop, productivity, and more.

### v1.4 — New
- **Dynamic plugin discovery** — Drop a Tool subclass into `jarvis/plugins/` and it loads automatically.
- **Multi-step tool chaining** — Bounded execution plans with intermediate results.
- **Permission system** — Risk levels (safe/write/sensitive/destructive) with user confirmation.
- **Calculator** — Safe arithmetic with percentages, powers, and square roots.
- **Unit conversion** — Length, weight, volume, temperature, speed, area.
- **Currency conversion** — Live exchange rates with caching.
- **News headlines** — By topic (general, tech, AI, sports).
- **Notes** — Create, list, read, update, delete, search.
- **Clipboard** — Read, copy, clear (X11/Wayland).
- **Screenshot** — Capture and save the screen.
- **Process manager** — List, search, terminate processes.
- **Desktop launcher** — Open approved apps, URLs, and folders.
- **Improved memory** — `/memory`, `/remember`, `/forget` commands.
- **61 automated tests** — Full unit test suite.

### v1.3 (kept)
- **Weather & Forecast** — Current conditions, 3-day forecast, sunrise/sunset.
- **Location & Time** — IP-based geolocation, timezone detection.
- **System Information** — CPU, RAM, disk, GPU, hostname, IP, uptime.
- **Network Status** — Internet, ping, DNS, gateway.
- **Battery Status** — Charge level, charging state, remaining time.
- **Speed Test** — Download/upload/ping (optional).
- **Web search & fetch** — DuckDuckGo search, URL content extraction.
- **File tools** — Read, write, list files.

---

## Requirements

- **Python** 3.10 or later
- An **OpenAI-compatible backend** — install KoboldCpp, vLLM, or any OpenAI-compatible API server
- A **model** served by your backend

### Setting up KoboldCpp (recommended)

1. Download the latest KoboldCpp from [the releases page](https://github.com/LostRuins/koboldcpp/releases).
2. Place your GGUF model file in the same directory.
3. Run:
   ```bash
   ./koboldcpp --model gemma-4-12b-it-qat-q4_0.gguf --port 5001
   ```
4. KoboldCpp exposes an OpenAI-compatible API at `http://localhost:5001/v1`.

---

## Installation

```bash
git clone https://github.com/USERNAME/jarvis-ai.git
cd jarvis-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cat > .env << 'EOF'
AI_BASE_URL=http://localhost:5001/v1
AI_API_KEY=local
AI_MODEL=koboldcpp/gemma-4-12b-it-qat-q4_0
EOF
```

---

## Usage

```bash
# Start JARVIS (from the repository root)
python -m jarvis.main
```

Type your messages at the `You:` prompt. Press `Ctrl+C` or type `exit` to quit.

### Slash Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/tools` | List tools by category with risk levels |
| `/tool <name> <json>` | Run a tool directly |
| `/clear` | Clear conversation history |
| `/status` | Show system information |
| `/set location <loc>` | Save your location for weather/time |
| `/memory` | List stored facts and preferences |
| `/remember <key> <value>` | Store a fact |
| `/forget <key>` | Remove a stored fact |
| `/notes` | List saved notes |

### Tools

| Category | Tools |
|---|---|
| **Web** | `web_search`, `web_fetch`, `news` |
| **Weather & Location** | `weather`, `forecast`, `sunrise_sunset`, `location`, `time` |
| **System** | `system_info`, `battery`, `list_processes`, `search_processes`, `terminate_process` |
| **Network** | `network_status`, `speed_test` |
| **Files** | `read_file`, `write_file`, `list_files`, `create_dir`, `copy_file`, `move_file`, `search_files`, `search_content`, `delete_file`, `open_file` |
| **Desktop** | `screenshot`, `clipboard_read`, `clipboard_copy`, `clipboard_clear`, `launch_app`, `open_url` |
| **Productivity** | `create_note`, `list_notes`, `read_note`, `update_note`, `delete_note`, `search_notes` |
| **Utilities** | `calculator`, `unit_convert`, `currency_convert` |

### Configuration Quick Reference

JARVIS reads settings from `.env` (project root) or environment variables.

| Variable | Default | Description |
|---|---|---|
| `AI_BASE_URL` | `http://192.168.1.194:5001/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | `local` | API key (set via env var for security) |
| `AI_MODEL` | `koboldcpp/gemma-4-12b-it-qat-q4_0` | Model name |
| `AI_TIMEOUT` | `120` | Request timeout in seconds |
| `MAX_TOOL_ROUNDS` | `5` | Max tool calls per interaction |
| `MAX_CHAIN_STEPS` | `5` | Max steps in a tool chain |
| `AUTO_CONFIRM_WRITE` | `true` | Auto-approve write-level tools |
| `DEFAULT_LOCATION` | `""` | Default location for weather |
| `MAX_CONTEXT_TURNS` | `10` | Conversation pairs sent to LLM |
| `ENABLE_STREAMING` | `true` | Token-by-token streaming |
| `ENABLE_COLORS` | `true` | Colored terminal output |
| `ENABLE_TOOLS` | `true` | Master tool toggle |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `CURRENCY_CACHE_TTL` | `300` | Seconds to cache exchange rates |
| `NOTES_DIR` | `jarvis/notes/` | Notes storage directory |

See `jarvis/config.example.json` for the full config reference.

---

## Creating a Plugin

1. Create a `.py` file in `jarvis/plugins/`.
2. Subclass `jarvis.tools.base.Tool` and implement `execute(**kwargs) -> dict`.
3. Set `self.name`, `self.description`, `self.category`, and `self.risk`.
4. Restart JARVIS — the plugin is discovered automatically.

Example (`jarvis/plugins/examples/hello_plugin.py`):

```python
from jarvis.tools.base import Tool

class HelloPlugin(Tool):
    def __init__(self):
        super().__init__(
            name="hello",
            description="A friendly greeting plugin.",
            category="Plugins",
            risk="safe",
        )

    def execute(self, name: str = "World") -> dict:
        return {"message": f"Hello, {name}!"}
```

---

## Permission System

| Level | Behavior | Examples |
|---|---|---|
| `safe` | Runs automatically | weather, time, calculator |
| `write` | Auto-confirms (configurable) | write_file, create_note |
| `sensitive` | Requires user confirmation | clipboard_read, screenshot |
| `destructive` | Requires user confirmation | delete_file, terminate_process |

---

## Testing

```bash
python -m pytest tests/ -v
```

Tests mock the file system where needed. No live internet required for the full suite.

---

## Project Structure

```
jarvis/
├── jarvis/
│   ├── brain/               # LLM interaction
│   │   ├── client.py
│   │   └── processor.py
│   ├── memory/              # Persistence
│   │   ├── conversations.py
│   │   ├── facts.py
│   │   └── preferences.py
│   ├── plugins/             # Auto-discovered plugins
│   │   └── examples/
│   ├── tools/               # Tool framework
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── discovery.py
│   │   ├── permissions.py
│   │   ├── chaining.py
│   │   ├── calculator_tool.py
│   │   ├── unit_conversion_tool.py
│   │   ├── currency_tool.py
│   │   ├── news_tool.py
│   │   ├── notes_tool.py
│   │   ├── clipboard_tool.py
│   │   ├── screenshot_tool.py
│   │   ├── enhanced_file_tools.py
│   │   ├── process_tool.py
│   │   ├── launcher_tool.py
│   │   ├── file_tools.py
│   │   ├── web_tools.py
│   │   ├── system_tools.py
│   │   ├── weather_tools.py
│   │   ├── location_tools.py
│   │   └── network_tools.py
│   └── voice/               # Future
├── tests/                   # Automated tests
├── .env                     # AI config (not committed)
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## Roadmap

- [x] v1.0 — Local AI assistant with memory and streaming
- [x] v1.1 — Tool framework, file ops, web search, system info
- [x] v1.2 — OpenAI-compatible backend, `.env` config
- [x] v1.3 — Weather, forecast, location, network, battery, speed test
- [x] v1.4 — Dynamic plugins, permission system, tool chaining, 26 new tools, tests
- [ ] Voice interaction
- [ ] Image generation
- [ ] Long-term memory / RAG
- [ ] GUI / web interface

---

## License

MIT License. See `LICENSE` for more information.
