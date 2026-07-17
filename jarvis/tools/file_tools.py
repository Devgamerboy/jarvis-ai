import os
from .base import Tool


class ReadFileTool(Tool):
    def __init__(self):
        super().__init__("read_file", "Only when the user explicitly asks to read, open, view, or show the contents of a file. Do NOT use for greetings or general chat.")

    def execute(self, path: str) -> dict:
        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}
        if not os.path.isfile(path):
            return {"error": f"Not a file: {path}"}
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"path": path, "content": content, "size": len(content)}


class WriteFileTool(Tool):
    def __init__(self):
        super().__init__("write_file", "Only when the user explicitly asks to create, write, save, or store something in a file. Do NOT use for any other purpose.")

    def execute(self, path: str, content: str) -> dict:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"path": path, "written": len(content)}


class ListFilesTool(Tool):
    def __init__(self):
        super().__init__("list_files", "Only when the user explicitly asks to list, show, or browse files and directories. Do NOT use for general chat.")

    def execute(self, path: str = ".") -> dict:
        if not os.path.exists(path):
            return {"error": f"Path not found: {path}"}
        if not os.path.isdir(path):
            return {"error": f"Not a directory: {path}"}
        entries = os.listdir(path)
        files, dirs = [], []
        for e in sorted(entries):
            full = os.path.join(path, e)
            (dirs if os.path.isdir(full) else files).append(e)
        return {"path": path, "directories": dirs, "files": files}
