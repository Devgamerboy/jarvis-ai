# JARVIS

**A desktop AI assistant powered by KoboldCpp / OpenAI API.**

JARVIS is a beginner-friendly, modular AI assistant. It connects to any
OpenAI-compatible backend (KoboldCpp, vLLM, etc.) to serve
open-source language models.

---

## Features

- **OpenAI-compatible backend** — Connects to KoboldCpp, vLLM, or any OpenAI-compatible API.
- **Remote AI server** — Run the AI on a separate machine on your LAN (e.g., a desktop with a GPU).
- **Configurable models** — Switch models anytime via `.env` — Gemma, Llama, Mistral, and more.
- **Gemma 4 12B support** — Defaults to `koboldcpp/gemma-4-12b-it-qat-q4_0`.
- **Weather & Forecast** — Current conditions, 3-day forecast, sunrise/sunset (free, no API key).
- **Location & Time** — IP-based geolocation, current time, timezone detection.
- **System Information** — CPU, RAM, disk, GPU, hostname, IP, uptime.
- **Network Status** — Internet connectivity, ping latency, DNS check, gateway.
- **Battery Status** — Charge level, charging state, remaining time (laptops).
- **Speed Test** — Internet download/upload speed test (optional).
- **Web search** — Search the web using DuckDuckGo (free, no API key needed).
- **File tools** — Read, write, and list files directly from the chat.
- **Persistent memory** — Conversations, user facts, and preferences are saved to disk.
- **Location memory** — "My location is Charlotte, NC" — remembered for weather and time.
- **Streaming responses** — See tokens appear in real time as the model generates them.
- **`.env` configuration** — AI backend settings live in a `.env` file; change servers or models without editing code.
- **Tool logging** — Every tool execution is logged with name and duration.
- **Error handling** — Startup health check detects offline servers; tools never crash.
- **Modular design** — Separate `brain/`, `memory/`, `tools/`, and `voice/` packages.
- **Colored terminal UI** — User input, assistant replies, timestamps, errors, and status messages each have a distinct color.
- **Timestamps** — Every message is prefixed with a `[HH:MM:SS]` timestamp.
- **Slash commands** — Built-in commands for tools, system status, and help.

---

## Requirements

- **Python** 3.10 or later
- An **OpenAI-compatible backend** — install KoboldCpp, vLLM, or any server that exposes an OpenAI-compatible API
- A **model** served by your backend (default: `koboldcpp/gemma-4-12b-it-qat-q4_0`)

### Setting up KoboldCpp (recommended)

1. Download the latest KoboldCpp executable from [the releases page](https://github.com/LostRuins/koboldcpp/releases).
2. Place your GGUF model file (e.g., `gemma-4-12b-it-qat-q4_0.gguf`) in the same directory.
3. Run:
   ```bash
   ./koboldcpp --model gemma-4-12b-it-qat-q4_0.gguf --port 5001
   ```
4. KoboldCpp automatically exposes an OpenAI-compatible API at `http://localhost:5001/v1`.

> **Note:** KoboldCpp can run on a separate GPU-equipped machine on your LAN.  
> Just replace `localhost` with the server's hostname or IP in `.env`.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/USERNAME/jarvis-ai.git
cd jarvis-ai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure your AI backend — copy and edit the example
cat > .env << 'EOF'
AI_BASE_URL=http://192.168.1.194:5001/v1
AI_API_KEY=local
AI_MODEL=koboldcpp/gemma-4-12b-it-qat-q4_0
EOF
```

> Change `AI_BASE_URL` and `AI_MODEL` in `.env` to match your backend.  
> If KoboldCpp runs on the same machine, use `http://localhost:5001/v1`.

---

## Usage

```bash
# Make sure your AI backend is running (e.g. KoboldCpp on port 5001)
# Then start JARVIS (from the repository root)
python -m jarvis.main
```

Type your messages at the `You:` prompt. Use `/help` to see available commands.
Press `Ctrl+C` or type `exit` to quit.

### Examples

| You say | JARVIS does |
|---|---|
| `hello` | Greets you conversationally |
| `What system am I on?` | Calls `system_info` — shows OS, CPU, RAM, disk, GPU |
| `What's the weather?` | Calls `weather` — temperature, humidity, wind, conditions |
| `What time is it?` | Calls `time` — local time and date |
| `Where am I?` | Calls `location` — city, region, country, timezone |
| `Is the internet working?` | Calls `network_status` — ping, DNS, gateway |
| `Battery status?` | Calls `battery` — percentage, charging, remaining time |
| `My location is Charlotte NC` | Saves location to memory |
| `Search the web for Python` | Calls `web_search` — DuckDuckGo results |
| `Create a file called test.txt with content hello` | Calls `write_file` |
| `Read test.txt` | Calls `read_file` |
| `Run a speed test` | Calls `speed_test` — download/upload/ping |

### Slash Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/tools` | List all registered tools |
| `/tool <name> <json>` | Run a tool directly |
| `/clear` | Clear conversation history |
| `/status` | Show system information |
| `/set location <loc>` | Save your location for weather/time |

### Tools

| Category | Tool | Description |
|---|---|---|
| **System** | `system_info` | OS, CPU, RAM, disk, GPU, hostname, IP, uptime |
| | `battery` | Battery percentage, charging, remaining time |
| **Weather** | `weather` | Current temperature, feels like, humidity, wind, conditions |
| | `forecast` | Multi-day high/low, conditions, chance of rain |
| | `sunrise_sunset` | Sunrise, sunset, daylight hours |
| **Location** | `location` | City, region, country, timezone, coordinates |
| | `time` | Local time, date, timezone |
| **Network** | `network_status` | Internet, ping latency, DNS, gateway |
| | `speed_test` | Download/upload speed test |
| **Web** | `web_search` | Search the web via DuckDuckGo |
| | `web_fetch` | Fetch and extract text from a URL |
| **Files** | `read_file` | Read file contents |
| | `write_file` | Write content to a file |
| | `list_files` | List directory contents |

### Configuration Quick Reference

JARVIS reads AI settings from the `.env` file at the project root:

| Setting | Example | What it does |
|---|---|---|
| `AI_BASE_URL` | `http://192.168.1.194:5001/v1` | Your OpenAI-compatible API endpoint |
| `AI_API_KEY` | `local` | API key (most local backends accept any value) |
| `AI_MODEL` | `koboldcpp/gemma-4-12b-it-qat-q4_0` | Model name as reported by the backend |

You can also override any setting with an environment variable — env vars take precedence over `.env`.

### Full Configuration Reference

All settings can be set in `.env` or overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `AI_BASE_URL` | `http://192.168.1.194:5001/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | `local` | API key for the backend |
| `AI_MODEL` | `koboldcpp/gemma-4-12b-it-qat-q4_0` | Model name |
| `AI_TIMEOUT` | `120` | Request timeout in seconds |
| `DEFAULT_LOCATION` | `""` | Default location for weather/time |
| `USE_IP_LOCATION` | `true` | Auto-detect location by IP |
| `MAX_CONTEXT_TURNS` | `10` | Conversation pairs sent to the LLM |
| `ENABLE_STREAMING` | `true` | Enable token-by-token streaming |
| `ENABLE_COLORS` | `true` | Enable colored terminal output |
| `ENABLE_TOOLS` | `true` | Enable the tool framework |

---

## Project Structure

```
jarvis/
├── jarvis/                  # Main Python package
│   ├── brain/               # LLM interaction & prompt building
│   │   ├── client.py        # OpenAI client singleton
│   │   └── processor.py     # Prompt builder, AI calls, tool parsing
│   ├── memory/              # Memory persistence
│   │   ├── conversations.py # Conversation history
│   │   ├── facts.py         # User facts storage (location, etc.)
│   │   ├── memory.py        # Backward-compatible wrapper
│   │   └── preferences.py   # User preferences storage
│   ├── tools/               # Extensible tool framework
│   │   ├── base.py          # Abstract Tool base class
│   │   ├── registry.py      # Tool registration & execution
│   │   ├── file_tools.py    # Read, write, list files
│   │   ├── web_tools.py     # Web search & fetch
│   │   ├── system_tools.py  # System info & battery
│   │   ├── weather_tools.py # Weather, forecast, sunrise/sunset
│   │   ├── location_tools.py# Location & time
│   │   └── network_tools.py # Network status & speed test
│   ├── voice/               # Voice interface (future)
│   │   └── __init__.py
│   ├── config.py            # Central configuration
│   └── main.py              # Entry point
├── .env                     # AI configuration (not committed)
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

---

## Roadmap

- [x] OpenAI-compatible backend (KoboldCpp / vLLM)
- [x] Persistent conversation memory
- [x] Streaming responses
- [x] Configurable settings via `.env`
- [x] Colored terminal interface
- [x] Error handling & logging
- [x] **Tool framework (web search, file ops, system info)**
- [x] **User facts & preferences storage**
- [x] **Timestamps & slash commands**
- [x] **Weather, forecast & sunrise/sunset**
- [x] **Location & time**
- [x] **Network status & speed test**
- [x] **Battery status**
- [x] **Location memory**
- [x] **Tool execution logging**
- [ ] Voice interaction
- [ ] Website generation
- [ ] Image generation
- [ ] Long-term memory / RAG
- [ ] Autonomous agent mode
- [ ] Desktop automation
- [ ] GUI / web interface

---

## Credits

JARVIS is powered by the open-source LLM community. Built with Python.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
