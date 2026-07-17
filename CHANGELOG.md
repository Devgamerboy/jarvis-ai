# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-07-16

### Added

- First public release of JARVIS.
- Local AI assistant powered by Ollama.
- Persistent conversation memory with configurable context window.
- Streaming token-by-token responses with real-time terminal output.
- Colored terminal UI (user, assistant, error, and status colors).
- Configuration via environment variables or `config.py`.
- Startup health check — detects whether Ollama is running and provides clear setup instructions.
- Automatic error logging to `logs/errors.log` with timestamps.
- Modular architecture: `brain/`, `memory/`, `tools/`, `voice/` packages.
- Graceful handling of missing models, connection errors, and keyboard interrupts.
- `OLLAMA_KEEP_ALIVE` support to keep the model loaded between requests.
- Context limiting — only the last N conversation turns are sent to the LLM.
- Clean `Ctrl+C` / `Ctrl+D` exit.
