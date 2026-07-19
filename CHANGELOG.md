# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.4.0-development] - 2026-07-18

### Added

- **Dynamic tool discovery** — Tools are automatically discovered from `jarvis/tools/` and `jarvis/plugins/` packages at startup. No manual registration needed for new tools.
- **Plugin API** — Documented plugin interface under `jarvis/plugins/`. Drop a `Tool` subclass in the plugins directory and it is loaded automatically. Example plugin included.
- **Tool chaining** — Multi-step execution plans with bounded steps, intermediate result storage, intent validation, and clean failure handling.
- **Permission system** — Four risk levels (safe, write, sensitive, destructive). Safe tools run automatically; write tools auto-confirm (configurable); sensitive and destructive tools require user confirmation via terminal prompt.
- **Calculator tool** — Safe arithmetic without `eval`. Supports addition, subtraction, multiplication, division, percentages (X% of Y), powers, square roots, and parentheses.
- **Unit conversion tool** — Convert length, weight/mass, volume, temperature (F/C/K), speed, and area with natural expression parsing (e.g. "5 miles to km").
- **Currency conversion tool** — Live exchange rates via open.er-api.com with caching. Supports USD, EUR, GBP, and 150+ currencies.
- **News tool** — Fetch headlines by topic (general, technology, AI, sports, or custom query). Falls back to RSS feeds when no API key is available.
- **Notes tool** — Create, list, read, update, delete, and search notes stored as JSON files in `jarvis/notes/`.
- **Clipboard tool** — Read, copy, and clear the system clipboard (supports X11 via xclip and Wayland via wl-clipboard).
- **Screenshot tool** — Capture the screen using gnome-screenshot, scrot, or ImageMagick.
- **Enhanced file tools** — `create_dir`, `copy_file`, `move_file`, `search_files` (glob), `search_content` (text in files), `delete_file`, `open_file` (desktop default app).
- **Process manager** — `list_processes`, `search_processes`, `terminate_process` (guarded — no system-critical or root termination).
- **Desktop launcher** — `launch_app` (approved applications with configurable allowlist) and `open_url` (default browser).
- **Smarter memory** — Improved `/memory`, `/remember`, `/forget` commands; memory prefix categorization.
- **Improved /tools command** — Tools grouped by category (Web, Weather & Location, System, Network, Files, Desktop, Productivity, Utilities, Plugins) with risk levels shown.
- **Improved personality** — Friendly welcome message; remembers user name ("my name is ..."); does not claim success without tool confirmation.
- **Better logging** — Separate log files: `errors.log` (warnings+), `tools.log` (all tool usage), `security.log` (permission decisions). Tool duration and success/failure logged.
- **Example config** — `config.example.json` documents all available settings.
- **40 total tools** — Up from 14 in v1.3.
- **61 automated tests** — Unit tests for discovery, registry, permissions, calculator, unit conversion, notes, file safety, chaining, greetings, and tool validation.

### Changed

- All v1.3 tools now include `category` and `risk` metadata for better grouping.
- Tool base class (`base.py`) extended with `category`, `risk`, and `parameter_schema()`.
- Registry (`registry.py`) added `list_by_category()`, `list_names()`, and permission-aware `execute()`.
- Configuration (`config.py`) split into dedicated loggers for tool, security, and error events.
- Dynamic system prompt generation uses discovered tool categories instead of hardcoded lists.
- Main loop (`main.py`) integrates permission checks, smarter greeting handling, and name memory.

### Fixed

- All tool modules handle import errors gracefully without crashing startup.
- File operations prevent path traversal via `os.path.normpath()`.
- Calculator uses safe AST parsing — no `eval()` on untrusted input.

## [1.3.0] - 2026-07-18

### Added

- **Weather tool** — `weather(location)` fetches current temperature, feels like, humidity, wind, conditions, cloud cover, visibility, and UV index via wttr.in (no API key needed).
- **Forecast tool** — `forecast(location)` returns up to 4 days of high/low, conditions, chance of rain, sunrise, and sunset.
- **Sunrise/Sunset tool** — `sunrise_sunset(location)` returns sunrise time, sunset time, and daylight hours via the sunrise-sunset.org API.
- **Location tool** — `location()` returns city, region, country, timezone, coordinates, ISP, and org via ip-api.com (no API key).
- **Time tool** — `time(location)` returns local time, date, and timezone; falls back to IP-based location.
- **Network Status tool** — `network_status()` checks internet connectivity, ping latency, DNS resolution, and gateway reachability.
- **Speed Test tool** — `speed_test()` runs an internet speed test via speedtest-cli (optional package).
- **Battery tool** — `battery()` reports charge percentage, charging state, and remaining time via psutil; gracefully reports "No battery detected" on desktops.
- **Improved system_info** — Now includes CPU usage %, memory details (total/used/available/usage %), disk usage %, GPU detection (NVIDIA via nvidia-smi), hostname, IP address, and uptime.
- **Location memory** — "My location is Charlotte, NC" saves to facts; `/set location <loc>` command; weather/time tools use stored location automatically.
- **Tool logging** — Every tool execution is logged with name and duration to the console.
- **Configuration options** — `DEFAULT_LOCATION`, `USE_IP_LOCATION` added to `.env` / config.
- **14 total tools** — JARVIS now has rich desktop assistant capabilities.

### Changed

- Banner version updated to `v1.3.0` and subtitle to `Desktop AI Assistant`.
- `tools/__init__.py` now registers all 14 tools.
- `brain/processor.py` prompt rebuilt with categorized tools (System, Weather, Location, Network, Web, Files) and more examples for better AI tool selection.
- `main.py` added `/set location` command and "my location is" natural language handler.
- `main.py` tool keywords expanded for all new tools.
- `requirements.txt` added `psutil`, `speedtest-cli`.

### Fixed

- All tools handle network errors gracefully — no tracebacks to user.

## [1.2.0] - 2026-07-18

### Added

- **OpenAI-compatible backend** — Switched from Ollama to configurable OpenAI-compatible API (KoboldCpp, vLLM, etc.).
- **`.env` configuration** — `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` are now stored in `.env` instead of hardcoded.
- **KoboldCpp / Gemma 4 12B support** — Defaults to `koboldcpp/gemma-4-12b-it-qat-q4_0`.
- **Graceful offline error** — Shows "Gemma AI server unavailable" when backend is unreachable.
- **`temperature=0.7`** — Set on all AI requests for consistent output.
- **Remote AI server support** — JARVIS can connect to a backend running on any machine on your LAN.

### Changed

- `jarvis/brain/client.py` — New OpenAI client singleton using `from openai import OpenAI`.
- `jarvis/brain/processor.py` — Uses `client.chat.completions.create()` with OpenAI SDK.
- `jarvis/config.py` — All `OLLAMA_*` variables replaced with `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`; loads `.env` via `python-dotenv`.
- `jarvis/main.py` — `check_ai()` uses OpenAI `models.list()`; error message includes the configured URL.

### Removed

- All `import ollama` and `ollama.Client()` usage.
- `ollama` Python package dependency.

## [1.1.0] - 2026-07-17

### Added

- **Tool framework** — Abstract `Tool` base class with registration, lookup, and execution via `tools/registry.py`.
- **File tools** — `read_file`, `write_file`, `list_files` for reading, creating, and navigating the filesystem.
- **Web search** — `web_search` (via DuckDuckGo, free, no API key) and `web_fetch` (fetch and extract text from URLs).
- **System info tool** — `system_info` reports OS, CPU, disk, and Python details.
- **Slash commands** — `/help`, `/tools`, `/tool`, `/clear`, `/status` for direct tool invocation and system management.
- **LLM-level tool calling** — The model can autonomously invoke tools by outputting `TOOL_CALL: tool_name({...})` in its response.
- **Separated memory** — Conversation history, user facts, and preferences are now stored in separate JSON files under `memory/`.
- **Terminal timestamps** — All output lines are prefixed with `[HH:MM:SS]` timestamps.
- **`ENABLE_TOOLS`** environment variable to toggle the tool framework (default: `true`).

### Changed

- `tools/tools.py` stub replaced with full `tools/` package.
- System prompt dynamically includes tool descriptions when tools are enabled.
- All imports converted to relative package imports.
- Runtime tool call validation with keyword intent guard.
- Greeting/casual conversation detection (`_is_casual()`).

## [1.0.0] - 2026-07-16

### Added

- First public release of JARVIS.
- Local AI assistant powered by an OpenAI-compatible backend.
- Persistent conversation memory with configurable context window.
- Streaming token-by-token responses with real-time terminal output.
- Colored terminal UI (user, assistant, error, and status colors).
- Configuration via environment variables or `config.py`.
- Startup health check — detects whether the AI backend is reachable.
- Automatic error logging to `logs/errors.log` with timestamps.
- Modular architecture: `brain/`, `memory/`, `tools/`, `voice/` packages.
- Graceful handling of missing models, connection errors, and keyboard interrupts.
- Context limiting — only the last N conversation turns are sent to the LLM.
- Clean `Ctrl+C` / `Ctrl+D` exit.
