# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-07-18

### Added

- **OpenAI-compatible backend** — Switched from Ollama to configurable OpenAI-compatible API (KoboldCpp, vLLM, etc.).
- **`.env` configuration** — `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` are now stored in `.env` instead of hardcoded in Python.
- **KoboldCpp / Gemma 4 12B support** — Defaults to `koboldcpp/gemma-4-12b-it-qat-q4_0`.
- **Graceful offline error** — Shows "Gemma AI server unavailable at {URL}" when backend is unreachable.
- **`temperature=0.7`** — Set on all AI requests for consistent output.
- **Remote AI server support** — JARVIS can connect to a backend running on any machine on your LAN.

### Changed

- `jarvis/brain/client.py` — New OpenAI client singleton using `from openai import OpenAI`.
- `jarvis/brain/processor.py` — `ask_ollama` → `ask_ai`, `ask_ollama_stream` → `ask_ai_stream`; uses `client.chat.completions.create()`.
- `jarvis/config.py` — `OLLAMA_*` variables replaced with `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`; loads `.env` via `python-dotenv`.
- `jarvis/main.py` — `check_ollama` → `check_ai`; error messages include the configured URL; logs failures to file.
- `jarvis/requirements.txt` — Removed `ollama` package, added `python-dotenv`.
- `README.md` / `CHANGELOG.md` — All Ollama references removed.

### Removed

- All `import ollama` and `ollama.Client()` usage from the codebase.
- Hardcoded model/server values from Python source.
- `ollama` Python package dependency.

## [1.1.0] - 2026-07-17

### Added

- **Tool framework** — Abstract `Tool` base class with registration, lookup,
  and execution via `tools/registry.py`.
- **File tools** — `read_file`, `write_file`, `list_files` for reading,
  creating, and navigating the filesystem.
- **Web search** — `web_search` (via DuckDuckGo, free, no API key) and
  `web_fetch` (fetch and extract text from URLs).
- **System info tool** — `system_info` reports OS, CPU, disk, and Python
  details.
- **Slash commands** — `/help`, `/tools`, `/tool`, `/clear`, `/status`
  for direct tool invocation and system management.
- **LLM-level tool calling** — The model can autonomously invoke tools by
  outputting `TOOL_CALL: tool_name({...})` in its response.
- **Separated memory** — Conversation history, user facts, and preferences
  are now stored in separate JSON files under `memory/`.
- **Terminal timestamps** — All output lines are prefixed with `[HH:MM:SS]`
  timestamps.
- **`ENABLE_TOOLS`** environment variable to toggle the tool framework
  (default: `true`).

### Changed

- `tools/tools.py` stub replaced with full `tools/` package (`base.py`,
  `registry.py`, `file_tools.py`, `web_tools.py`, `system_tools.py`).
- `memory/memory.py` is now a backward-compatible wrapper around the new
  `memory/conversations.py` module.
- System prompt dynamically includes tool descriptions when tools are
  enabled.
- `README.md` updated with tool documentation, new commands, and revised
  project structure.
- `requirements.txt` now includes `requests`, `ddgs`, and
  `beautifulsoup4` for web tool functionality.
- **All imports converted to relative package imports** — project runs via
  `python -m jarvis.main` from any directory.
- **DuckDuckGo library updated** — migrated from deprecated
  `duckduckgo_search` to `ddgs`.
- **OpenAI client lifecycle** — module-level singleton client with `get_client()`
  eliminates `ResourceWarning: unclosed socket`.
- **System prompt strengthened** — tools are only invoked when the user
  explicitly requests an actionable task; greetings and casual conversation
  skip tool execution entirely.
- **Tool descriptions improved** — each tool description explicitly states
  when it should be used, preventing model misuse.
- **Runtime tool call validation** — pre-execution intent guard checks user
  input against keyword patterns per tool; blocks mismatched or unsolicited
  tool calls before they execute.
- **Greeting/casual conversation filter** — `_is_casual()` detects greetings,
  thanks, farewells, and small talk, and bypasses the entire tool pipeline
  so the model responds conversationally.

### Removed

- Old `tools/tools.py` stub file (replaced by the new tool package).
- Deprecated `duckduckgo_search` dependency (replaced by `ddgs`).
- Old top-level absolute imports.

## [1.0.0] - 2026-07-16

### Added

- First public release of JARVIS.
- Local AI assistant powered by an OpenAI-compatible backend.
- Persistent conversation memory with configurable context window.
- Streaming token-by-token responses with real-time terminal output.
- Colored terminal UI (user, assistant, error, and status colors).
- Configuration via environment variables or `config.py`.
- Startup health check — detects whether the AI backend is reachable and provides clear setup instructions.
- Automatic error logging to `logs/errors.log` with timestamps.
- Modular architecture: `brain/`, `memory/`, `tools/`, `voice/` packages.
- Graceful handling of missing models, connection errors, and keyboard interrupts.
- `AI_TIMEOUT` support to configure request timeout.
- Context limiting — only the last N conversation turns are sent to the LLM.
- Clean `Ctrl+C` / `Ctrl+D` exit.
