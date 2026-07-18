import subprocess
import socket

from .base import Tool


def _internet_connectivity() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        return False


def _ping_latency(host: str = "8.8.8.8") -> str:
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "3", host],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "time=" in line:
                    ms = line.split("time=")[1].split()[0]
                    return ms
        return "Unavailable"
    except Exception:
        return "Unavailable"


def _dns_working() -> bool:
    try:
        socket.getaddrinfo("google.com", 80)
        return True
    except Exception:
        return False


def _gateway_reachable() -> str:
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            gateway = result.stdout.split()[2]
            ping = _ping_latency(gateway)
            return f"Reachable (ping: {ping})" if ping != "Unavailable" else "Unreachable"
        return "No default gateway found"
    except Exception:
        return "Unavailable"


class NetworkStatusTool(Tool):
    def __init__(self):
        super().__init__(
            "network_status",
            "Only when the user explicitly asks about network connectivity, internet status, ping, DNS, or gateway."
        )

    def execute(self) -> dict:
        return {
            "internet": _internet_connectivity(),
            "ping_latency": _ping_latency(),
            "dns_working": _dns_working(),
            "gateway": _gateway_reachable(),
        }


class SpeedTestTool(Tool):
    def __init__(self):
        super().__init__(
            "speed_test",
            "Only when the user explicitly asks to run an internet speed test."
        )

    def execute(self) -> dict:
        try:
            import speedtest
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            download = round(st.download() / 1_000_000, 1)
            upload = round(st.upload() / 1_000_000, 1)
            ping = round(st.results.ping, 1)
            return {
                "download": f"{download} Mbps",
                "upload": f"{upload} Mbps",
                "ping": f"{ping} ms",
            }
        except ImportError:
            return {"error": "speedtest-cli not installed. Run: pip install speedtest-cli"}
        except Exception as e:
            return {"error": f"Speed test failed: {e}"}
