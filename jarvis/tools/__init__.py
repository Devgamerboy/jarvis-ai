from tools.base import Tool
from tools.registry import register, get, list_all, execute
from tools.file_tools import ReadFileTool, WriteFileTool, ListFilesTool
from tools.web_tools import WebSearchTool, WebFetchTool
from tools.system_tools import SystemInfoTool


def register_all():
    register(ReadFileTool())
    register(WriteFileTool())
    register(ListFilesTool())
    register(WebSearchTool())
    register(WebFetchTool())
    register(SystemInfoTool())
