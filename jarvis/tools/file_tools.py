import os
from tools.base import Tool


class ReadFileTool(Tool):
    def __init__(self):
        super().__init__("read_file", "Read the contents of a file at a given path.")

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
        super().__init__("write_file", "Write content to a file. Creates parent directories.")

    def execute(self, path: str, content: str) -> dict:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"path": path, "written": len(content)}


class ListFilesTool(Tool):
    def __init__(self):
        super().__init__("list_files", "List files and directories at a given path.")

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
