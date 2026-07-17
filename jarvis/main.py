import json
import logging
import os
import sys
from datetime import datetime

import ollama

from brain.processor import (
    ask_ollama,
    ask_ollama_stream,
    build_messages,
    parse_tool_calls,
)
from config import (
    ASSISTANT_NAME,
    ENABLE_COLORS,
    ENABLE_STREAMING,
    ENABLE_TOOLS,
    LOG_DIR,
    MAX_CONTEXT_TURNS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from memory.memory import add_entry, load_memory


def _color(code, text):
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


def blue(text):
    return _color("34", text)


def grey(text):
    return _color("90", text)


def now():
    return datetime.now().strftime("%H:%M:%S")


def ts(text):
    return grey(f"[{now()}] ") + text


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "errors.log"),
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def print_banner():
    banner = f"""
{'=' * 38}
  {green(ASSISTANT_NAME + ' v1.1.0')}
  {green('Local AI Assistant')}
  {yellow('Powered by Ollama')}
{'=' * 38}
"""
    print(banner)


def check_ollama():
    try:
        ollama.Client(host=OLLAMA_BASE_URL).list()
    except ollama.RequestError:
        print(ts(red(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")))
        print(ts(yellow("  Start Ollama with: ollama serve")))
        print(ts(yellow("  Install from https://ollama.com")))
        return False
    except ollama.ResponseError as e:
        print(ts(red(f"Ollama error: {e.error}")))
        return False
    return True


def handle_command(cmd: str) -> bool:
    parts = cmd.strip().split(maxsplit=1)
    verb = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "/help":
        print(ts(yellow("Commands:")))
        print(ts(cyan("  /help                  ") + yellow("Show this help")))
        print(ts(cyan("  /tools                 ") + yellow("List available tools")))
        print(ts(cyan("  /tool <name> <json>    ") + yellow("Run a tool directly")))
        print(ts(cyan("  /clear                 ") + yellow("Clear conversation history")))
        print(ts(cyan("  /status                ") + yellow("Show system information")))
        print(ts(cyan("  exit / quit            ") + yellow("Exit JARVIS")))
        return True

    if verb == "/tools":
        from tools import list_all
        tools = list_all()
        if not tools:
            print(ts(yellow("No tools registered.")))
        else:
            print(ts(green(f"Available tools ({len(tools)}):")))
            for t in tools:
                print(ts(cyan(f"  {t['name']}") + grey(f" — {t['description']}")))
        return True

    if verb == "/tool":
        tool_parts = rest.split(maxsplit=1)
        if not tool_parts:
            print(ts(red("Usage: /tool <name> [json-args]")))
            return True
        tool_name = tool_parts[0]
        tool_args = {}
        if len(tool_parts) > 1:
            try:
                tool_args = json.loads(tool_parts[1])
            except json.JSONDecodeError:
                print(ts(red("Arguments must be valid JSON (e.g. /tool read_file {\"path\": \"/tmp/test\"})")))
                return True
        from tools import execute
        result = execute(tool_name, **tool_args)
        if result["success"]:
            print(ts(green("Result:")))
            print(json.dumps(result["result"], indent=2, default=str))
        else:
            print(ts(red(f"Error: {result['error']}")))
        return True

    if verb == "/clear":
        from memory.conversations import clear
        clear()
        print(ts(green("Conversation history cleared.")))
        return True

    if verb == "/status":
        from tools.system_tools import SystemInfoTool
        result = SystemInfoTool().execute()
        print(ts(cyan("System Information:")))
        for k, v in result.items():
            label = k.replace("_", " ").title()
            print(ts(f"  {label}: {v}"))
        return True

    return False


def process_tool_calls(messages, initial_response):
    from brain.processor import MAX_TOOL_ROUNDS
    from tools import execute

    text = initial_response
    for _round in range(MAX_TOOL_ROUNDS):
        calls = parse_tool_calls(text)
        if not calls:
            return text

        messages.append({"role": "assistant", "content": text})

        for name, args in calls:
            print(ts(yellow(f"  Using tool: {name}...")))
            result = execute(name, **args)
            messages.append({
                "role": "user",
                "content": f"Tool '{name}' returned: {json.dumps(result, indent=2, default=str)}"
            })

        text = ask_ollama(messages)

    return text


def stream_response(messages):
    full_reply = ""
    print(ts(green(f"{ASSISTANT_NAME}: ")), end="", flush=True)
    for chunk in ask_ollama_stream(messages):
        content = chunk["message"]["content"]
        if content:
            print(content, end="", flush=True)
            full_reply += content
    print()
    return full_reply


def main():
    setup_logging()

    if ENABLE_TOOLS:
        from tools import register_all
        register_all()

    print_banner()

    if ENABLE_TOOLS:
        from tools import list_all
        tools = list_all()
        if tools:
            print(ts(grey(f"Tools loaded: {', '.join(t['name'] for t in tools)}")))

    if not check_ollama():
        sys.exit(1)

    print(ts(yellow("Type /help for commands, 'exit' to quit.\n")))

    while True:
        try:
            user_input = input(ts(cyan("You: "))).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(ts(green("Goodbye.")))
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print(ts(green("Goodbye.")))
            break

        if user_input.startswith("/"):
            if handle_command(user_input):
                continue
            print(ts(red(f"Unknown command: {user_input}")))
            print(ts(yellow("Type /help for available commands.")))
            continue

        memory = load_memory()
        messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS)

        try:
            if ENABLE_TOOLS:
                full_reply = ask_ollama(messages)
                calls = parse_tool_calls(full_reply)
                if calls:
                    full_reply = process_tool_calls(messages, full_reply)
                print(ts(green(f"{ASSISTANT_NAME}: {full_reply}")))
            else:
                if ENABLE_STREAMING:
                    full_reply = stream_response(messages)
                else:
                    full_reply = ask_ollama(messages)
                    print(ts(green(f"{ASSISTANT_NAME}: {full_reply}")))

        except RuntimeError as e:
            print(ts(red(f"Error: {e}")))
            logging.error(str(e))
            continue

        add_entry(user_input, full_reply)


if __name__ == "__main__":
    main()
