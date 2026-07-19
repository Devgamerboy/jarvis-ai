"""Prompt building and AI interaction — supports selective tool prompts."""

import json
import re

from ..config import (
    AI_MODEL,
    SYSTEM_PROMPT,
    MAX_CONTEXT_TURNS,
    MAX_HISTORY_MESSAGES,
    MAX_PROMPT_CHARS,
    ENABLE_TOOLS,
)
from .client import get_client

# ---------------------------------------------------------------------------
# Prompt caching — rebuilt once per startup, then reused
# ---------------------------------------------------------------------------
_FULL_PROMPT_CACHE: str | None = None


def _build_prompt(tool_names: list[str] | None = None) -> str:
    """Build a system prompt listing *tool_names* (or all if ``None``).

    The full-tool-list version is cached after the first call.
    """
    if not ENABLE_TOOLS:
        return SYSTEM_PROMPT

    if tool_names is None:
        global _FULL_PROMPT_CACHE
        if _FULL_PROMPT_CACHE is not None:
            return _FULL_PROMPT_CACHE
        _FULL_PROMPT_CACHE = _build_prompt_text(None)
        return _FULL_PROMPT_CACHE

    return _build_prompt_text(tool_names)


def _build_prompt_text(tool_names: list[str] | None) -> str:
    """Build prompt text for the given tool subset (or all tools)."""
    try:
        from ..tools import list_by_category, get

        if tool_names is not None:
            specs = []
            for name in tool_names:
                t = get(name)
                if t:
                    specs.append(t.spec())
            grouped = {"Selected": specs} if specs else {}
        else:
            grouped = list_by_category()

        if not grouped:
            return SYSTEM_PROMPT

        category_order = [
            "Selected",
            "Web",
            "Weather & Location",
            "System",
            "Network",
            "Files",
            "Desktop",
            "Productivity",
            "Utilities",
            "Plugins",
        ]

        parts = [
            SYSTEM_PROMPT,
            "",
            "## Available Tools",
        ]

        for cat in category_order:
            tools_in_cat = grouped.get(cat)
            if not tools_in_cat:
                continue
            parts.append(f"\n### {cat}")
            for s in tools_in_cat:
                risk_label = s.get("risk", "safe")
                line = f"  {s['name']} — {s['description']}"
                if risk_label != "safe":
                    line += f" [{risk_label}]"
                parts.append(line)

        return "\n".join(parts)
    except Exception:
        return SYSTEM_PROMPT


def select_tools_for_query(user_input: str) -> list[str] | None:
    """Return a relevant tool subset based on user input keywords.

    Returns ``None`` when all tools should be included (broad query).
    """
    lowered = user_input.lower()

    _CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "Weather & Location": ["weather", "forecast", "temperature", "sunrise", "sunset", "rain", "humidity",
                                "wind", "location", "where am i", "time", "date", "what time", "daylight"],
        "Web": ["search", "web", "google", "duckduckgo", "look up", "find online", "fetch", "url", "http",
                "news", "headlines", "current events"],
        "System": ["system", "cpu", "memory", "ram", "disk", "gpu", "process", "battery", "charge",
                   "power", "hardware", "os", "hostname", "uptime"],
        "Network": ["internet", "network", "ping", "dns", "speed test", "bandwidth", "connectivity", "wifi"],
        "Files": ["file", "read", "write", "save", "create", "directory", "folder", "list file",
                  "copy", "move", "rename", "search file", "find file", "delete", "open file"],
        "Desktop": ["screenshot", "capture screen", "clipboard", "copy", "launch", "open app",
                    "open url", "open folder"],
        "Productivity": ["note", "remember", "write down", "save this", "my notes"],
        "Utilities": ["calculate", "compute", "math", "convert", "currency", "exchange rate"],
    }

    matched_categories = set()
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            matched_categories.add(cat)

    if not matched_categories:
        return None

    from ..tools import list_by_category
    by_cat = list_by_category()
    tool_names: list[str] = []
    for cat in matched_categories:
        specs = by_cat.get(cat, [])
        tool_names.extend(s["name"] for s in specs)

    return tool_names if tool_names else None


# ---------------------------------------------------------------------------
# Tool call parsing
# ---------------------------------------------------------------------------

_WITH_ARGS = [
    re.compile(r'(?:TOOL_CALL:\s*)?(\w+)\s*\(\s*(\{.*?\})\s*\)', re.DOTALL),
    re.compile(r'(\w+)\s*:\s*"[^"]*"\s*\(\s*(\{.*?\})\s*\)', re.DOTALL),
]

_WITHOUT_ARGS = [
    re.compile(r'(?:TOOL_CALL:\s*)?(\w+)\s*\(\s*\)', re.DOTALL),
]


def parse_tool_calls(text: str) -> list[tuple[str, dict]]:
    from ..tools import get as get_tool

    seen = set()
    calls = []

    for pattern in _WITH_ARGS:
        for match in pattern.finditer(text):
            name = match.group(1)
            if name in seen or not get_tool(name):
                continue
            seen.add(name)
            try:
                args = json.loads(match.group(2))
            except json.JSONDecodeError:
                continue
            calls.append((name, args))

    for pattern in _WITHOUT_ARGS:
        for match in pattern.finditer(text):
            name = match.group(1)
            if name in seen or not get_tool(name):
                continue
            seen.add(name)
            calls.append((name, {}))

    return calls


# ---------------------------------------------------------------------------
# AI calls
# ---------------------------------------------------------------------------

def ask_ai(messages, **_ignored):
    from ..config import AI_BASE_URL, AI_MAX_RETRIES
    last_error = None
    for attempt in range(1, AI_MAX_RETRIES + 2):
        try:
            response = get_client().chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                temperature=0.7,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            if attempt <= AI_MAX_RETRIES:
                import time as _time
                _time.sleep(1)
                continue
    raise RuntimeError(f"AI request failed at {AI_BASE_URL}: {last_error}")


def ask_ai_stream(messages, **_ignored):
    from ..config import AI_BASE_URL
    try:
        stream = get_client().chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield {"message": {"content": content}}
    except Exception as e:
        raise RuntimeError(f"AI request failed at {AI_BASE_URL}: {e}")


# ---------------------------------------------------------------------------
# Message builder — enforces MAX_HISTORY_MESSAGES and MAX_PROMPT_CHARS
# ---------------------------------------------------------------------------

def build_messages(
    user_input: str,
    memory_log: list,
    max_turns: int = MAX_CONTEXT_TURNS,
    tool_names: list[str] | None = None,
) -> list[dict]:
    """Build the message array for the LLM with size limits."""
    prompt = _build_prompt(tool_names)

    messages = [{"role": "system", "content": prompt}]

    if max_turns > 0 and memory_log:
        recent = memory_log[-max_turns:]
    else:
        recent = memory_log or []

    history_limit = min(MAX_HISTORY_MESSAGES, len(recent))
    char_budget = MAX_PROMPT_CHARS - len(prompt) - len(user_input) - 500
    added_chars = 0

    for entry in recent[-history_limit:]:
        turn_chars = len(entry["user"]) + len(entry["assistant"]) + 50
        if added_chars + turn_chars > char_budget and added_chars > 200:
            break
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})
        added_chars += turn_chars

    messages.append({"role": "user", "content": user_input})
    return messages
