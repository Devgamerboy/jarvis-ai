"""Central configuration for JARVIS.

All settings can be overridden with environment variables or a .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AI provider settings
AI_BASE_URL = os.getenv("AI_BASE_URL", "http://192.168.1.194:5001/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "local")
AI_MODEL = os.getenv("AI_MODEL", "koboldcpp/gemma-4-12b-it-qat-q4_0")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))

# Assistant settings
ASSISTANT_NAME = "JARVIS"
SYSTEM_PROMPT = "You are JARVIS, a helpful and intelligent AI assistant."

# Memory settings
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "conversations.json")
MAX_MEMORY_LINES = 50

# Tool settings
ENABLE_TOOLS = os.getenv("ENABLE_TOOLS", "true").lower() == "true"

# Context settings
MAX_CONTEXT_TURNS = int(os.getenv("MAX_CONTEXT_TURNS", "10"))

# UI settings
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
ENABLE_COLORS = os.getenv("ENABLE_COLORS", "true").lower() == "true"

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Location defaults
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "")
USE_IP_LOCATION = os.getenv("USE_IP_LOCATION", "true").lower() == "true"
