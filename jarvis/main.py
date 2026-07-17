"""JARVIS — Local AI Assistant

Entry point for the JARVIS REPL.  Handles startup checks, the
interactive loop, streaming output, and error logging.
"""

import os
import sys
import logging
import ollama
from brain.processor import ask_ollama, ask_ollama_stream, build_messages
from memory.memory import add_entry, load_memory
from config import (
    ASSISTANT_NAME,
    ENABLE_STREAMING,
    ENABLE_COLORS,
    LOG_DIR,
    MAX_CONTEXT_TURNS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


# ---------------------------------------------------------------------------
# Terminal color helpers
# ---------------------------------------------------------------------------

def _color(code, text):
    """Wrap *text* in an ANSI escape code if colors are enabled."""
    if not ENABLE_COLORS:
        return text
    return f"\033[{code}m{text}\033[0m"


def cyan(text):
    return _color("36", text)


def green(text):
    return _color("32", text)


def red(text):
    return _color("31", text)


def yellow(text):
    return _color("33", text)


# ---------------------------------------------------------------------------
# Initialization helpers
# ---------------------------------------------------------------------------

def setup_logging():
    """Create the logs directory and configure Python's logging module.

    Only ERROR-level messages are written to ``logs/errors.log``.
    Normal conversation is never logged.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "errors.log"),
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def print_banner():
    """Display the startup banner with version and credits."""
    banner = f"""
{'=' * 36}
      {green(ASSISTANT_NAME + ' v1.0.0')}
    {green('Local AI Assistant')}
    {yellow('Powered by Ollama')}
{'=' * 36}
"""
    print(banner)


def check_ollama():
    """Verify that the Ollama server is reachable.

    Returns:
        True if the server responds, False otherwise.

    Prints a helpful message with fix instructions when the server
    cannot be reached.
    """
    try:
        ollama.Client(host=OLLAMA_BASE_URL).list()
    except ollama.RequestError:
        print(red(f"Error: Cannot connect to Ollama at {OLLAMA_BASE_URL}"))
        print(yellow("Start Ollama with: ollama serve"))
        print(yellow("Or install it from https://ollama.com"))
        return False
    except ollama.ResponseError as e:
        print(red(f"Error: {e.error}"))
        return False
    return True


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    """Run the JARVIS interactive REPL."""
    setup_logging()
    print_banner()

    if not check_ollama():
        sys.exit(1)

    print(yellow("Type 'exit' to quit.\n"))

    while True:
        try:
            user_input = input(cyan("You: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(green("Goodbye."))
            break

        if user_input.lower() in ("exit", "quit"):
            print(green("Goodbye."))
            break

        if not user_input:
            continue

        memory = load_memory()
        messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS)

        try:
            if ENABLE_STREAMING:
                full_reply = ""
                print(green(f"{ASSISTANT_NAME}: "), end="", flush=True)
                for chunk in ask_ollama_stream(messages):
                    content = chunk["message"]["content"]
                    if content:
                        print(content, end="", flush=True)
                        full_reply += content
                print()
            else:
                full_reply = ask_ollama(messages)
                print(green(f"{ASSISTANT_NAME}: {full_reply}"))
        except RuntimeError as e:
            print(red(f"Error: {e}"))
            logging.error(str(e))
            continue

        add_entry(user_input, full_reply)


if __name__ == "__main__":
    main()
