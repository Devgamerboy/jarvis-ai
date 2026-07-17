import os
import platform
import shutil
import sys
from tools.base import Tool


def _read_cpu_info():
    try:
        model = None
        cores = 0
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                elif line.startswith("processor"):
                    cores += 1
        parts = []
        if model:
            parts.append(model)
        if cores:
            parts.append(f"{cores} cores")
        return " / ".join(parts)
    except Exception:
        pass
    return "Unavailable"


def _read_memory():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return f"{round(kb / (1024 ** 2), 1)} GB"
    except Exception:
        pass
    try:
        import psutil
        return f"{round(psutil.virtual_memory().total / (1024 ** 3), 1)} GB"
    except ImportError:
        pass
    return "Unavailable"


def _disk_info():
    try:
        du = shutil.disk_usage(os.path.expanduser("~"))
        total = round(du.total / (1024 ** 3), 1)
        free = round(du.free / (1024 ** 3), 1)
        used = round(du.used / (1024 ** 3), 1)
        return f"{total} GB total ({free} GB free, {used} GB used)"
    except Exception:
        pass
    return "Unavailable"


class SystemInfoTool(Tool):
    def __init__(self):
        super().__init__("system_info", "Get OS, CPU, memory, disk, and Python version info.")

    def execute(self) -> dict:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "architecture": platform.machine(),
            "cpu": _read_cpu_info(),
            "memory": _read_memory(),
            "disk": _disk_info(),
            "python": sys.version.split()[0],
        }
