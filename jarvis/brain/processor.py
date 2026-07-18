import json
import re


from ..config import (
    AI_MODEL,
    SYSTEM_PROMPT,
    MAX_CONTEXT_TURNS,
    ENABLE_TOOLS,
)
from .client import get_client

MAX_TOOL_ROUNDS = 3


def _build_prompt():
    if not ENABLE_TOOLS:
        return SYSTEM_PROMPT
    try:
        from ..tools import list_all
        tools = list_all()
        if not tools:
            return SYSTEM_PROMPT

        usage_examples = {
            "system_info": 'TOOL_CALL: system_info()',
            "battery": 'TOOL_CALL: battery()',
            "weather": 'TOOL_CALL: weather({"location": "Charlotte, NC"})',
            "forecast": 'TOOL_CALL: forecast({"location": "Charlotte, NC"})',
            "sunrise_sunset": 'TOOL_CALL: sunrise_sunset({"location": "Charlotte, NC"})',
            "location": 'TOOL_CALL: location()',
            "time": 'TOOL_CALL: time()',
            "network_status": 'TOOL_CALL: network_status()',
            "speed_test": 'TOOL_CALL: speed_test()',
            "web_search": 'TOOL_CALL: web_search({"query": "Python programming"})',
            "web_fetch": 'TOOL_CALL: web_fetch({"url": "https://example.com"})',
            "read_file": 'TOOL_CALL: read_file({"path": "/etc/os-release"})',
            "write_file": 'TOOL_CALL: write_file({"path": "/tmp/test.txt", "content": "hello"})',
            "list_files": 'TOOL_CALL: list_files({"path": "/home"})',
        }

        tool_category = {
            "system": ["system_info", "battery"],
            "weather": ["weather", "forecast", "sunrise_sunset"],
            "location": ["location", "time"],
            "network": ["network_status", "speed_test"],
            "web": ["web_search", "web_fetch"],
            "files": ["read_file", "write_file", "list_files"],
        }

        category_descriptions = {
            "system": "System Information & Power",
            "weather": "Weather, Forecast & Sun Times",
            "location": "Location & Time",
            "network": "Network & Internet",
            "web": "Web Search & Fetch",
            "files": "File Operations",
        }

        parts = [
            SYSTEM_PROMPT,
            "",
            "## Tool Usage Guidelines",
            "",
            "You have access to tools across several categories. Call a tool when the user asks for something that requires live data.",
            "For greetings, casual conversation, thanks, or goodbyes — just reply conversationally. Be friendly and natural.",
            "Never call a tool for greetings or chit-chat.",
            "",
            "IMPORTANT: When the user asks a factual question that a tool can answer, you MUST call the tool.",
            "NEVER invent or guess system information, hardware details, weather data, search results, or file contents.",
            "Base your answer ONLY on the data the tool returns.",
            "",
            "Examples of when to call each tool:",
            "",
            '  "What is outside like?" —→ weather',
            '  "Do I need an umbrella?" —→ weather (check chance of rain)',
            '  "What is the forecast?" —→ forecast',
            '  "When does the sun rise?" —→ sunrise_sunset',
            '  "Where am I?" —→ location',
            '  "What time is it?" —→ time',
            '  "How is my system?" —→ system_info',
            '  "How much RAM do I have?" —→ system_info',
            '  "What is my CPU?" —→ system_info',
            '  "Battery status?" —→ battery',
            '  "Is the internet working?" —→ network_status',
            '  "Run a speed test" —→ speed_test',
            '  "Search the web for ..." —→ web_search',
            "",
            "To call a tool, output exactly one line:",
            '    TOOL_CALL: tool_name({"param": "value"})',
            "    For tools with no parameters:",
            "    TOOL_CALL: tool_name()",
            "After the tool runs, summarize the result naturally.",
            "",
            "## Available Tools",
        ]

        for cat_key, cat_tools in tool_category.items():
            parts.append(f"\n### {category_descriptions[cat_key]}")
            for t_name in cat_tools:
                tool_spec = next((t for t in tools if t["name"] == t_name), None)
                if tool_spec:
                    hint = usage_examples.get(t_name)
                    if hint:
                        parts.append(f"  {t_name} — {tool_spec['description']}")
                        parts.append(f"    Example: {hint}")
                    else:
                        parts.append(f"  {t_name} — {tool_spec['description']}")

        return "\n".join(parts)
    except Exception:
        return SYSTEM_PROMPT


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


def ask_ai(messages, **_ignored):
    from ..config import AI_BASE_URL
    try:
        response = get_client().chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.7,
            stream=False,
        )
    except Exception as e:
        raise RuntimeError(f"AI request failed at {AI_BASE_URL}: {e}")
    return response.choices[0].message.content


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


def build_messages(user_input, memory_log, max_turns=MAX_CONTEXT_TURNS):
    messages = [{"role": "system", "content": _build_prompt()}]

    if max_turns > 0:
        recent = memory_log[-max_turns:]
    else:
        recent = memory_log

    for entry in recent:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})

    messages.append({"role": "user", "content": user_input})
    return messages
