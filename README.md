# JARVIS

**A free, local AI assistant powered by Ollama.**

JARVIS is a beginner-friendly, modular AI assistant that runs entirely on your
machine. It uses [Ollama](https://ollama.com) to serve open-source language
models locally, keeping your data private and your costs at zero.

---

## Features

- **Local AI** — Runs on your machine with Ollama. No cloud, no API keys, no
  data leaks.
- **Persistent memory** — Conversations are saved to disk and restored on
  restart.
- **Streaming responses** — See tokens appear in real time as the model
  generates them.
- **Configurable** — Model, keep-alive, context length, colors, streaming, and
  more are adjustable via environment variables or `config.py`.
- **Error handling** — Startup health check detects missing models or offline
  servers and shows clear instructions.
- **Modular design** — Separate `brain/`, `memory/`, `tools/`, and `voice/`
  packages make the codebase easy to navigate and extend.
- **Colored terminal UI** — User input, assistant replies, errors, and status
  messages each have a distinct color.
- **Logging** — Errors are automatically logged to `logs/errors.log` with
  timestamps.

---

## Requirements

- **Python** 3.10 or later
- **Ollama** — [Install Ollama](https://ollama.com) for your platform
- A **model** pulled via Ollama (default: `llama3.2:3b`)

```bash
ollama pull llama3.2:3b
```

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
# Make sure Ollama is running
ollama serve

# In another terminal, start JARVIS
python jarvis/main.py
```

Type your messages at the `You:` prompt. Press `Ctrl+C` or type `exit` to quit.

### Configuration

All settings can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model name |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |
| `OLLAMA_KEEP_ALIVE` | `30m` | How long to keep model loaded |
| `MAX_CONTEXT_TURNS` | `10` | Conversation pairs sent to the LLM |
| `ENABLE_STREAMING` | `true` | Enable token-by-token streaming |
| `ENABLE_COLORS` | `true` | Enable colored terminal output |

---

## Project Structure

```
jarvis/
├── jarvis/                  # Main Python package
│   ├── brain/               # LLM interaction & prompt building
│   │   └── processor.py
│   ├── memory/              # Conversation persistence
│   │   └── memory.py
│   ├── tools/               # Extensible tool framework (future)
│   │   └── tools.py
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

## Screenshots

> *Screenshots coming soon.*

---

## Roadmap

- [x] Local AI via Ollama
- [x] Persistent conversation memory
- [x] Streaming responses
- [x] Configurable settings
- [x] Colored terminal interface
- [x] Error handling & logging
- [ ] Voice interaction
- [ ] Tool framework (web search, file ops, etc.)
- [ ] Website generation
- [ ] Image generation
- [ ] Long-term memory / RAG
- [ ] Autonomous agent mode
- [ ] Desktop automation
- [ ] GUI / web interface

---

## Credits

JARVIS is powered by [Ollama](https://ollama.com) and the open-source LLM
community. Built with Python.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
