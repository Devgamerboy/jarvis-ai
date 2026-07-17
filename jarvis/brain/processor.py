import atexit
import json
import re


import ollama
from ..config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_KEEP_ALIVE,
    SYSTEM_PROMPT,
    MAX_CONTEXT_TURNS,
    ENABLE_TOOLS,
)

MAX_TOOL_ROUNDS = 3

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = ollama.Client(host=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)
        atexit.register(_close_client)
    return _client

def _close_client():
    global _client
    if _client is not None:
        try:
            _client.close()
        except Exception:
            pass
        _client = None


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
            "web_search": 'TOOL_CALL: web_search({"query": "Python programming"})',
            "read_file": 'TOOL_CALL: read_file({"path": "/etc/os-release"})',
            "write_file": 'TOOL_CALL: write_file({"path": "/tmp/note.txt", "content": "hello"})',
            "list_files": 'TOOL_CALL: list_files({"path": "/home"})',
            "web_fetch": 'TOOL_CALL: web_fetch({"url": "https://example.com"})',
        }

        parts = [
            SYSTEM_PROMPT,
            "",
            "## Tool Usage Guidelines",
            "",
            "You have access to tools for system info, file operations, and web lookups.",
            "Only call a tool when the user explicitly asks for something that requires one:",
            "- system_info: only when asked about system, OS, CPU, memory, or hardware",
            "- web_search: only when asked to search the web or look something up online",
            "- web_fetch: only when given a specific URL to fetch",
            "- read_file: only when asked to read, open, or view a file",
            "- write_file: only when asked to create, write, or save a file",
            "- list_files: only when asked to list files or directories",
            "",
            "For greetings, casual conversation, thanks, or goodbyes — just reply conversationally. Be friendly and natural.",
            "Never call a tool for greetings or chit-chat.",
            "",
            "IMPORTANT: When the user asks a factual question that a tool can answer (system info, search, file read), you MUST call the tool.",
            "NEVER invent or guess system information, hardware details, search results, or file contents.",
            "Base your answer ONLY on the data the tool returns.",
            "",
            "To call a tool, output exactly one line:",
            '    TOOL_CALL: tool_name({"param": "value"})',
            "    For tools with no parameters:",
            "    TOOL_CALL: tool_name()",
            "After the tool runs, summarize the result naturally.",
            "",
            "## Examples",
            "",
            'User: hello',
            'Assistant: Hey there! How can I help you today?',
            "",
            'User: hi jarvis',
            'Assistant: Hi! What can I do for you?',
            "",
            'User: good morning',
            'Assistant: Good morning! Hope you are having a great day. How can I assist?',
            "",
            'User: What system am I on?',
            'Assistant: TOOL_CALL: system_info()',
            "",
            'User: Search the web for Python news',
            'Assistant: TOOL_CALL: web_search({"query": "Python news"})',
            "",
'User: Create a file called test.txt with content "hello"',
'Assistant: TOOL_CALL: write_file({"path": "/tmp/test.txt", "content": "hello"})',
"",
'User: Read the file /tmp/test.txt',
'Assistant: TOOL_CALL: read_file({"path": "/tmp/test.txt"})',
"",
"Available tools:",
        ]

        for t in tools:
            hint = usage_examples.get(t["name"])
            if hint:
                parts.append(f"  {t['name']} — {t['description']}")
                parts.append(f"    Call: {hint}")
            else:
                parts.append(f"  {t['name']} — {t['description']}")

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


def ask_ollama(messages, keep_alive=OLLAMA_KEEP_ALIVE):
    try:
        response = _get_client().chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=False,
            keep_alive=keep_alive,
        )
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise RuntimeError(
                f"Model '{OLLAMA_MODEL}' not found. "
                f"Pull it with: ollama pull {OLLAMA_MODEL}"
            )
        raise RuntimeError(f"Ollama error (HTTP {e.status_code}): {e.error}")
    except ollama.RequestError as e:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            f"Is it running? ({e.error})"
        )
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")
    return response["message"]["content"]


def ask_ollama_stream(messages, keep_alive=OLLAMA_KEEP_ALIVE):
    try:
        stream = _get_client().chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=True,
            keep_alive=keep_alive,
        )
        for chunk in stream:
            yield chunk
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise RuntimeError(
                f"Model '{OLLAMA_MODEL}' not found. "
                f"Pull it with: ollama pull {OLLAMA_MODEL}"
            )
        raise RuntimeError(f"Ollama error (HTTP {e.status_code}): {e.error}")
    except ollama.RequestError as e:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            f"Is it running? ({e.error})"
        )
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")


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
