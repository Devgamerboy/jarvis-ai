# JARVIS

**A free AI assistant powered by KoboldCpp / OpenAI API.**

JARVIS is a beginner-friendly, modular AI assistant. It connects to any
OpenAI-compatible backend (KoboldCpp, vLLM, etc.) to serve
open-source language models.

---

## Features

- **Local AI** — Runs on your machine or LAN via any OpenAI-compatible backend. No cloud, no data leaks.
- **Tool framework** — Web search, file read/write, system info, and more.
  Extensible via a simple `Tool` base class.
- **Web search** — Search the web using DuckDuckGo (free, no API key needed).
- **File tools** — Read, write, and list files directly from the chat.
- **Persistent memory** — Conversations, user facts, and preferences are saved
  to disk.
- **Streaming responses** — See tokens appear in real time as the model
  generates them.
- **Configurable** — Model, base URL, API key, context length, colors, streaming,
  tools, and more are adjustable via environment variables or `config.py`.
- **Error handling** — Startup health check detects missing models or offline
  servers and shows clear instructions.
- **Modular design** — Separate `brain/`, `memory/`, `tools/`, and `voice/`
  packages make the codebase easy to navigate and extend.
- **Colored terminal UI** — User input, assistant replies, timestamps, errors,
  and status messages each have a distinct color.
- **Timestamps** — Every message is prefixed with a `[HH:MM:SS]` timestamp.
- **Slash commands** — Built-in commands for tools, system status, and help.
- **Logging** — Errors are automatically logged to `logs/errors.log` with
  timestamps.

---

## Requirements

- **Python** 3.10 or later
- An **OpenAI-compatible backend** (KoboldCpp, vLLM, etc.)
- A **model** served by your backend (default: `koboldcpp/gemma-4-12b-it-qat-q4_0`)

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
```

---

## Usage

```bash
# Make sure your AI backend is running (e.g. KoboldCpp on port 5001)
# Then start JARVIS (from the repository root)
python -m jarvis.main
```

Type your messages at the `You:` prompt. Use `/help` to see available commands.
Press `Ctrl+C` or type `exit` to quit.

### Slash Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/tools` | List all registered tools |
| `/tool <name> <json>` | Run a tool directly (e.g. `/tool web_search {"query":"weather"}`) |
| `/clear` | Clear conversation history |
| `/status` | Show system information (OS, CPU, disk, Python) |

### Tools

| Tool | Description |
|---|---|
| `web_search` | Search the web via DuckDuckGo |
| `web_fetch` | Fetch and extract text from a URL |
| `read_file` | Read file contents |
| `write_file` | Write content to a file |
| `list_files` | List directory contents |
| `system_info` | Show OS, CPU, disk, and Python info |

### Configuration

All settings can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `AI_BASE_URL` | `http://192.168.1.194:5001/v1` | OpenAI-compatible API endpoint |
| `AI_API_KEY` | `local` | API key for the backend |
| `AI_MODEL` | `koboldcpp/gemma-4-12b-it-qat-q4_0` | Model name |
| `AI_TIMEOUT` | `120` | Request timeout in seconds |
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
│   │   └── processor.py
│   ├── memory/              # Memory persistence
│   │   ├── conversations.py # Conversation history
│   │   ├── facts.py         # User facts storage
│   │   ├── memory.py        # Backward-compatible wrapper
│   │   └── preferences.py   # User preferences storage
│   ├── tools/               # Extensible tool framework
│   │   ├── base.py          # Abstract Tool base class
│   │   ├── registry.py      # Tool registration & execution
│   │   ├── file_tools.py    # Read, write, list files
│   │   ├── web_tools.py     # Web search & fetch
│   │   └── system_tools.py  # System information
│   ├── voice/               # Voice interface (future)
│   │   └── __init__.py
│   ├── config.py            # Central configuration
│   └── main.py              # Entry point
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── .gitignore
```

---

## Roadmap

- [x] Local AI via OpenAI-compatible backend (KoboldCpp / vLLM)
- [x] Persistent conversation memory
- [x] Streaming responses
- [x] Configurable settings
- [x] Colored terminal interface
- [x] Error handling & logging
- [x] **Tool framework (web search, file ops, system info)**
- [x] **User facts & preferences storage**
- [x] **Timestamps & slash commands**
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
