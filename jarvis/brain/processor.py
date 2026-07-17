import json
import re
import ollama
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_KEEP_ALIVE,
    SYSTEM_PROMPT,
    MAX_CONTEXT_TURNS,
    ENABLE_TOOLS,
)

TOOL_CALL_RE = re.compile(
    r'TOOL_CALL:\s*(\w+)\s*\(\s*(\{.*?\})\s*\)', re.DOTALL
)


def _get_client():
    return ollama.Client(host=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)


def _build_prompt():
    if not ENABLE_TOOLS:
        return SYSTEM_PROMPT
    try:
        from tools import list_all
        tools = list_all()
        if not tools:
            return SYSTEM_PROMPT
        lines = [
            SYSTEM_PROMPT,
            "",
            "You have access to tools you can use to help the user.",
            "When you need to use a tool, output exactly one line with this format:",
            'TOOL_CALL: tool_name({"param": "value"})',
            "The tool will run and you will see the result.",
            "Then continue your answer based on the tool result.",
            "",
            "Available tools:",
        ]
        for t in tools:
            lines.append(f"  {t['name']} — {t['description']}")
        return "\n".join(lines)
    except Exception:
        return SYSTEM_PROMPT


def parse_tool_calls(text: str) -> list[tuple[str, dict]]:
    calls = []
    for match in TOOL_CALL_RE.finditer(text):
        name = match.group(1)
        try:
            args = json.loads(match.group(2))
        except json.JSONDecodeError:
            args = {}
        calls.append((name, args))
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
