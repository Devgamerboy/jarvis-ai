"""Enhanced file operations — copy, move, rename, search, delete, and open."""

import os
import shutil
import glob as glob_mod

from .base import Tool


def _safe_path(path: str) -> str:
    return os.path.normpath(os.path.expanduser(path))


class CreateDirTool(Tool):
    def __init__(self):
        super().__init__("create_dir", "Create a new directory at the given path.", category="Files", risk="write")

    def execute(self, path: str = "") -> dict:
        if not path:
            return {"error": "Path is required."}
        p = _safe_path(path)
        os.makedirs(p, exist_ok=True)
        return {"path": p, "message": f"Directory created: {p}"}


class CopyFileTool(Tool):
    def __init__(self):
        super().__init__("copy_file", "Copy a file or directory from source to destination.", category="Files", risk="write")

    def execute(self, source: str = "", destination: str = "") -> dict:
        if not source or not destination:
            return {"error": "Both source and destination are required."}
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not os.path.exists(src):
            return {"error": f"Source not found: {src}"}
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return {"source": src, "destination": dst, "message": f"Copied to {dst}"}


class MoveFileTool(Tool):
    def __init__(self):
        super().__init__("move_file", "Move or rename a file or directory.", category="Files", risk="write")

    def execute(self, source: str = "", destination: str = "") -> dict:
        if not source or not destination:
            return {"error": "Both source and destination are required."}
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not os.path.exists(src):
            return {"error": f"Source not found: {src}"}
        if os.path.exists(dst):
            return {"error": f"Destination already exists: {dst}"}
        shutil.move(src, dst)
        return {"source": src, "destination": dst, "message": f"Moved to {dst}"}


class SearchFilesTool(Tool):
    def __init__(self):
        super().__init__("search_files", "Search for files by name pattern (e.g. '*.txt').", category="Files")

    def execute(self, pattern: str = "", path: str = ".") -> dict:
        if not pattern:
            return {"error": "Search pattern is required (e.g. '*.txt')."}
        search_path = _safe_path(path)
        matches = glob_mod.glob(os.path.join(search_path, pattern), recursive=True)
        return {"pattern": pattern, "path": search_path, "matches": sorted(matches), "count": len(matches)}


class SearchContentTool(Tool):
    def __init__(self):
        super().__init__("search_content", "Search file contents for a text string.", category="Files")

    def execute(self, text: str = "", path: str = ".") -> dict:
        if not text:
            return {"error": "Search text is required."}
        search_path = _safe_path(path)
        results = []
        for root, _dirs, files in os.walk(search_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        for lineno, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                results.append({"file": fpath, "line": lineno, "match": line.strip()[:120]})
                except Exception:
                    pass
        return {"text": text, "path": search_path, "matches": results, "count": len(results)}


class DeleteFileTool(Tool):
    def __init__(self):
        super().__init__("delete_file", "Delete a file or empty directory. Requires confirmation.", category="Files", risk="destructive")

    def execute(self, path: str = "") -> dict:
        if not path:
            return {"error": "Path is required."}
        p = _safe_path(path)
        if not os.path.exists(p):
            return {"error": f"Path not found: {p}"}
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            os.rmdir(p)  # only removes empty directories
        return {"path": p, "message": f"Deleted: {p}"}


class OpenFileTool(Tool):
    def __init__(self):
        super().__init__("open_file", "Open a file, folder, or URL with the default desktop application.", category="Desktop")

    def execute(self, path: str = "") -> dict:
        if not path:
            return {"error": "Path or URL is required."}
        p = _safe_path(path)
        if not os.path.exists(p) and not path.startswith(("http://", "https://")):
            return {"error": f"Path not found: {p}"}
        try:
            import subprocess
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", p])
            elif shutil.which("open"):  # macOS
                subprocess.Popen(["open", p])
            else:
                return {"error": "No desktop opener found (install xdg-utils)."}
            return {"path": p, "message": f"Opened: {p}"}
        except Exception as e:
            return {"error": f"Failed to open: {e}"}
