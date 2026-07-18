import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime

from .base import Tool


def _read_cpu_info() -> dict:
    try:
        model = None
        cores = 0
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                elif line.startswith("processor"):
                    cores += 1
        return {"model": model or "Unavailable", "cores": cores}
    except Exception:
        return {"model": "Unavailable", "cores": 0}


def _cpu_usage() -> str:
    try:
        with open("/proc/stat") as f:
            line = f.readline()
        parts = [int(x) for x in line.split()[1:]]
        total = sum(parts)
        idle = parts[3]
        return f"{round((1 - idle / total) * 100, 1)}%"
    except Exception:
        return "Unavailable"


def _memory_info() -> dict:
    try:
        with open("/proc/meminfo") as f:
            data = {}
            for line in f:
                parts = line.split()
                if parts[0] in ("MemTotal:", "MemAvailable:", "MemFree:"):
                    data[parts[0].rstrip(":")] = int(parts[1])
        total_gb = round(data["MemTotal"] / (1024 ** 2), 1)
        available_gb = round(data.get("MemAvailable", 0) / (1024 ** 2), 1)
        used_gb = round(total_gb - available_gb, 1)
        usage_pct = round((1 - data.get("MemAvailable", 0) / data["MemTotal"]) * 100, 1) if data.get("MemAvailable") else 0
        return {
            "total": f"{total_gb} GB",
            "used": f"{used_gb} GB",
            "available": f"{available_gb} GB",
            "usage": f"{usage_pct}%",
        }
    except Exception:
        return {"total": "Unavailable", "used": "Unavailable", "available": "Unavailable", "usage": "Unavailable"}


def _disk_info() -> dict:
    try:
        du = shutil.disk_usage(os.path.expanduser("~"))
        total = round(du.total / (1024 ** 3), 1)
        free = round(du.free / (1024 ** 3), 1)
        used = round(du.used / (1024 ** 3), 1)
        usage_pct = round((du.used / du.total) * 100, 1)
        return {"total": f"{total} GB", "used": f"{used} GB", "free": f"{free} GB", "usage": f"{usage_pct}%"}
    except Exception:
        return {"total": "Unavailable", "used": "Unavailable", "free": "Unavailable", "usage": "Unavailable"}


def _gpu_info() -> str:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            return ", ".join(lines) if lines else "Unavailable"
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["rocm-smi", "--showproductname"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "AMD GPU detected"
    except Exception:
        pass
    return "Unavailable"


def _hostname() -> str:
    return socket.gethostname()


def _ip_address() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"


def _uptime() -> str:
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.readline().split()[0])
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    except Exception:
        return "Unavailable"


class SystemInfoTool(Tool):
    def __init__(self):
        super().__init__(
            "system_info",
            "Only when the user explicitly asks about their system, OS, CPU, memory, hardware, computer specifications, hostname, GPU, or uptime."
        )

    def execute(self) -> dict:
        cpu = _read_cpu_info()
        mem = _memory_info()
        disk = _disk_info()
        return {
            "os": f"{platform.system()} {platform.release()}",
            "kernel": platform.version(),
            "architecture": platform.machine(),
            "hostname": _hostname(),
            "ip_address": _ip_address(),
            "uptime": _uptime(),
            "cpu": cpu["model"],
            "cpu_cores": cpu["cores"],
            "cpu_usage": _cpu_usage(),
            "memory": mem,
            "disk": disk,
            "gpu": _gpu_info(),
            "python": sys.version.split()[0],
        }


class BatteryTool(Tool):
    def __init__(self):
        super().__init__(
            "battery",
            "Only when the user explicitly asks about battery status, charge level, or power."
        )

    def execute(self) -> dict:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery is None:
                return {"available": False, "message": "No battery detected — this appears to be a desktop system."}
            pct = round(battery.percent, 1)
            charging = battery.power_plugged
            remaining = str(datetime.utcfromtimestamp(battery.secsleft)) if battery.secsleft != -1 and battery.secsleft is not None else "N/A"
            return {
                "available": True,
                "percentage": f"{pct}%",
                "charging": charging,
                "remaining": remaining,
            }
        except ImportError:
            return {"available": False, "error": "psutil not installed. Run: pip install psutil"}
        except Exception as e:
            return {"available": False, "error": str(e)}
