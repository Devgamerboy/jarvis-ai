"""Central configuration for JARVIS.

All settings can be overridden with environment variables or a .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AI provider settings
AI_BASE_URL = os.getenv("AI_BASE_URL", "http://pop-os.local:5001/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "local")
AI_MODEL = os.getenv("AI_MODEL", "koboldcpp/gemma-4-12b-it-qat-q4_0")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "90"))
AI_CONNECT_TIMEOUT = int(os.getenv("AI_CONNECT_TIMEOUT", "10"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "1"))

# Assistant settings
ASSISTANT_NAME = "JARVIS"
SYSTEM_PROMPT = "You are JARVIS, a helpful and intelligent AI assistant."

# Memory settings
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "conversations.json")
MAX_MEMORY_LINES = 50
NOTES_DIR = os.getenv("NOTES_DIR", os.path.join(os.path.dirname(__file__), "notes"))

# Tool settings
ENABLE_TOOLS = os.getenv("ENABLE_TOOLS", "true").lower() == "true"
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
MAX_CHAIN_STEPS = int(os.getenv("MAX_CHAIN_STEPS", "5"))

# Permission settings
AUTO_CONFIRM_WRITE = os.getenv("AUTO_CONFIRM_WRITE", "true").lower() == "true"
APPROVED_DIRS = os.getenv("APPROVED_DIRS", "").split(",") if os.getenv("APPROVED_DIRS") else []
APPROVED_APPS = os.getenv("APPROVED_APPS", "").split(",") if os.getenv("APPROVED_APPS") else []

# Context settings
MAX_CONTEXT_TURNS = int(os.getenv("MAX_CONTEXT_TURNS", "10"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "8"))
MAX_PROMPT_CHARS = int(os.getenv("MAX_PROMPT_CHARS", "12000"))

# Routing settings
ENABLE_DETERMINISTIC_ROUTING = os.getenv("ENABLE_DETERMINISTIC_ROUTING", "true").lower() == "true"

# UI settings
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
ENABLE_COLORS = os.getenv("ENABLE_COLORS", "true").lower() == "true"

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PERFORMANCE_LOGGING = os.getenv("PERFORMANCE_LOGGING", "true").lower() == "true"

# Location defaults
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "")
USE_IP_LOCATION = os.getenv("USE_IP_LOCATION", "true").lower() == "true"

# Currency cache
CURRENCY_CACHE_TTL = int(os.getenv("CURRENCY_CACHE_TTL", "300"))
