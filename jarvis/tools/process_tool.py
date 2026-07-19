"""Process manager — list, search, and terminate processes."""

import os
import signal

from .base import Tool


_CRITICAL_PROCESSES = {"systemd", "init", "kernel", "kthreadd"}


class ListProcessesTool(Tool):
    def __init__(self):
        super().__init__(
            "list_processes",
            "List running processes with PID, name, CPU, and memory usage.",
            category="System",
        )

    def execute(self) -> dict:
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    pinfo = proc.info
                    processes.append({
                        "pid": pinfo["pid"],
                        "name": pinfo["name"],
                        "cpu": f"{pinfo['cpu_percent']:.1f}%",
                        "memory": f"{pinfo['memory_percent']:.1f}%",
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"processes": sorted(processes, key=lambda p: p["pid"])[:50], "count": min(len(processes), 50)}
        except ImportError:
            return {"error": "psutil not installed. Run: pip install psutil"}
        except Exception as e:
            return {"error": f"Failed to list processes: {e}"}


class SearchProcessesTool(Tool):
    def __init__(self):
        super().__init__(
            "search_processes",
            "Search for running processes by name.",
            category="System",
        )

    def execute(self, name: str = "") -> dict:
        if not name:
            return {"error": "Process name to search is required."}
        try:
            import psutil
            results = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    if name.lower() in proc.info["name"].lower():
                        pinfo = proc.info
                        results.append({
                            "pid": pinfo["pid"],
                            "name": pinfo["name"],
                            "cpu": f"{pinfo['cpu_percent']:.1f}%",
                            "memory": f"{pinfo['memory_percent']:.1f}%",
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"query": name, "processes": results, "count": len(results)}
        except ImportError:
            return {"error": "psutil not installed. Run: pip install psutil"}
        except Exception as e:
            return {"error": f"Process search failed: {e}"}


class TerminateProcessTool(Tool):
    def __init__(self):
        super().__init__(
            "terminate_process",
            "Terminate a running process by PID. Requires confirmation. Cannot kill system-critical processes.",
            category="System",
            risk="destructive",
        )

    def execute(self, pid: int = 0) -> dict:
        if not pid:
            return {"error": "PID is required."}
        try:
            import psutil
            proc = psutil.Process(pid)
            pname = proc.name()

            if pname.lower() in _CRITICAL_PROCESSES:
                return {"error": f"Refusing to terminate system-critical process: {pname}"}

            if os.geteuid() == 0:
                return {"error": "JARVIS should not be run as root. Cannot terminate processes."}

            proc.terminate()
            return {"pid": pid, "name": pname, "message": f"Process '{pname}' (PID {pid}) terminated."}
        except psutil.NoSuchProcess:
            return {"error": f"No process with PID {pid} found."}
        except psutil.AccessDenied:
            return {"error": f"Access denied to terminate PID {pid}."}
        except ImportError:
            return {"error": "psutil not installed. Run: pip install psutil"}
        except Exception as e:
            return {"error": f"Failed to terminate process: {e}"}
