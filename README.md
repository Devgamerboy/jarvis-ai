# JARVIS

**A free AI assistant powered by KoboldCpp / OpenAI API.**

JARVIS is a beginner-friendly, modular AI assistant. It connects to any
OpenAI-compatible backend (KoboldCpp, vLLM, etc.) to serve
open-source language models.

---

## Features

- **OpenAI-compatible backend** — Connects to KoboldCpp, vLLM, or any OpenAI-compatible API.
- **Remote AI server** — Run the AI on a separate machine on your LAN (e.g., a desktop with a GPU).
- **Configurable models** — Switch models anytime via `.env` — Gemma, Llama, Mistral, and more.
- **Gemma 4 12B support** — Defaults to `koboldcpp/gemma-4-12b-it-qat-q4_0`.
- **Tool framework** — Web search, file read/write, system info, and more.
  Extensible via a simple `Tool` base class.
- **Web search** — Search the web using DuckDuckGo (free, no API key needed).
- **File tools** — Read, write, and list files directly from the chat.
- **Persistent memory** — Conversations, user facts, and preferences are saved
  to disk.
- **Streaming responses** — See tokens appear in real time as the model
  generates them.
- **`.env` configuration** — AI backend settings live in a `.env` file; change servers or models without editing code.
- **Configurable** — Base URL, API key, model, context length, colors, streaming,
  tools, and more are adjustable via environment variables or `.env`.
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
# (uses KoboldCpp at 192.168.1.194:5001 by default)
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

### Configuration Quick Reference

JARVIS reads AI settings from the `.env` file at the project root:

| Setting | Example | What it does |
|---|---|---|
| `AI_BASE_URL` | `http://192.168.1.194:5001/v1` | Your OpenAI-compatible API endpoint |
| `AI_API_KEY` | `local` | API key (most local backends accept any value) |
| `AI_MODEL` | `koboldcpp/gemma-4-12b-it-qat-q4_0` | Model name as reported by the backend |

You can also override any setting with an environment variable — env vars take precedence over `.env`.

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

### Full Configuration Reference

All settings can be set in `.env` or overridden with environment variables:

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
