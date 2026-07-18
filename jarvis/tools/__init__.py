from .base import Tool
from .registry import register, get, list_all, execute
from .file_tools import ReadFileTool, WriteFileTool, ListFilesTool
from .web_tools import WebSearchTool, WebFetchTool
from .system_tools import SystemInfoTool, BatteryTool
from .weather_tools import WeatherTool, ForecastTool, SunriseSunsetTool
from .location_tools import LocationTool, TimeTool
from .network_tools import NetworkStatusTool, SpeedTestTool


def register_all():
    register(ReadFileTool())
    register(WriteFileTool())
    register(ListFilesTool())
    register(WebSearchTool())
    register(WebFetchTool())
    register(SystemInfoTool())
    register(BatteryTool())
    register(WeatherTool())
    register(ForecastTool())
    register(SunriseSunsetTool())
    register(LocationTool())
    register(TimeTool())
    register(NetworkStatusTool())
    register(SpeedTestTool())
