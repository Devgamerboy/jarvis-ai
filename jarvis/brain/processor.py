"""LLM communication and prompt construction.

Sends messages to Ollama, handles streaming, and builds
conversation prompts with configurable context windows.
"""

import ollama
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_KEEP_ALIVE,
    SYSTEM_PROMPT,
    MAX_CONTEXT_TURNS,
)


def _get_client():
    """Return a configured Ollama client."""
    return ollama.Client(host=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)


def ask_ollama(messages, keep_alive=OLLAMA_KEEP_ALIVE):
    """Send messages to Ollama and return the full assistant reply.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        keep_alive: Duration to keep the model loaded.

    Returns:
        The assistant's response text.
    """
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
    """Send messages to Ollama and stream the response token by token.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        keep_alive: Duration to keep the model loaded.

    Yields:
        Response chunks from Ollama, each containing a message fragment.
    """
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
    """Build the full message list sent to the LLM.

    Only the most recent ``max_turns`` conversation pairs are included
    to keep prompt size manageable.  The full history is still persisted
    to disk by the memory module.

    Args:
        user_input: The current user message.
        memory_log: List of past {user, assistant} dicts.
        max_turns: Number of recent conversation pairs to include.

    Returns:
        A list of message dicts ready for the Ollama chat API.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if max_turns > 0:
        recent = memory_log[-max_turns:]
    else:
        recent = memory_log

    for entry in recent:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})

    messages.append({"role": "user", "content": user_input})
    return messages
