"""Clipboard tool — read, copy, and clear the system clipboard."""

import subprocess
import shutil

from .base import Tool


def _have(command: str) -> bool:
    return shutil.which(command) is not None


def _get_clipboard():
    if _have("xclip"):
        result = subprocess.run(["xclip", "-o", "-selection", "clipboard"], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    if _have("wl-paste"):
        result = subprocess.run(["wl-paste"], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    return None


def _set_clipboard(text: str):
    if _have("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, timeout=5)
        return True
    if _have("wl-copy"):
        subprocess.run(["wl-copy"], input=text, text=True, timeout=5)
        return True
    return False


class ClipboardReadTool(Tool):
    def __init__(self):
        super().__init__("clipboard_read", "Read and display the current clipboard contents.", category="Desktop", risk="sensitive")

    def execute(self) -> dict:
        try:
            content = _get_clipboard()
            if content is None:
                return {"error": "Clipboard access not supported on this desktop (requires xclip or wl-clipboard)."}
            return {"content": content, "length": len(content)}
        except Exception as e:
            return {"error": f"Clipboard read failed: {e}"}


class ClipboardCopyTool(Tool):
    def __init__(self):
        super().__init__("clipboard_copy", "Copy text to the clipboard.", category="Desktop", risk="sensitive")

    def execute(self, text: str = "") -> dict:
        if not text:
            return {"error": "Text to copy is required."}
        try:
            ok = _set_clipboard(text)
            if not ok:
                return {"error": "Clipboard write not supported on this desktop (requires xclip or wl-clipboard)."}
            return {"copied": text[:100], "length": len(text)}
        except Exception as e:
            return {"error": f"Clipboard copy failed: {e}"}


class ClipboardClearTool(Tool):
    def __init__(self):
        super().__init__("clipboard_clear", "Clear the clipboard contents. Requires confirmation.", category="Desktop", risk="destructive")

    def execute(self) -> dict:
        try:
            ok = _set_clipboard("")
            if not ok:
                return {"error": "Clipboard write not supported on this desktop (requires xclip or wl-clipboard)."}
            return {"message": "Clipboard cleared."}
        except Exception as e:
            return {"error": f"Clipboard clear failed: {e}"}
