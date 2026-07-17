"""Central configuration for JARVIS.

All settings can be overridden with environment variables.
"""

import os

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")

# Assistant settings
ASSISTANT_NAME = "JARVIS"
SYSTEM_PROMPT = "You are JARVIS, a helpful and intelligent AI assistant."

# Memory settings
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory", "conversations.json")
MAX_MEMORY_LINES = 50

# Context settings
MAX_CONTEXT_TURNS = int(os.getenv("MAX_CONTEXT_TURNS", "10"))

# UI settings
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
ENABLE_COLORS = os.getenv("ENABLE_COLORS", "true").lower() == "true"

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
