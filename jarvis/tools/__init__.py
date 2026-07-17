from .base import Tool
from .registry import register, get, list_all, execute
from .file_tools import ReadFileTool, WriteFileTool, ListFilesTool
from .web_tools import WebSearchTool, WebFetchTool
from .system_tools import SystemInfoTool


def register_all():
    register(ReadFileTool())
    register(WriteFileTool())
    register(ListFilesTool())
    register(WebSearchTool())
    register(WebFetchTool())
    register(SystemInfoTool())
