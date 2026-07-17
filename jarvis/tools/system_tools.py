import os
import platform
import shutil
from tools.base import Tool


class SystemInfoTool(Tool):
    def __init__(self):
        super().__init__("system_info", "Get OS, CPU, disk, and Python version info.")

    def execute(self) -> dict:
        info = {
            "os": platform.system(),
            "os_version": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cwd": os.getcwd(),
            "cpu_count": os.cpu_count(),
        }
        try:
            du = shutil.disk_usage(os.path.expanduser("~"))
            info["disk_total_gb"] = round(du.total / (1024**3), 1)
            info["disk_free_gb"] = round(du.free / (1024**3), 1)
            info["disk_used_gb"] = round(du.used / (1024**3), 1)
        except Exception:
            pass
        return info
