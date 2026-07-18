from .base import Tool


class LocationTool(Tool):
    def __init__(self):
        super().__init__(
            "location",
            "Only when the user explicitly asks about their current location, where they are, city, region, country, or timezone."
        )

    def execute(self) -> dict:
        try:
            import requests
            resp = requests.get("http://ip-api.com/json", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {
                "city": data.get("city", "Unavailable"),
                "region": data.get("regionName", "Unavailable"),
                "country": data.get("country", "Unavailable"),
                "timezone": data.get("timezone", "Unavailable"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp", "Unavailable"),
                "org": data.get("org", "Unavailable"),
            }
        except ImportError:
            return {"error": "requests not installed. Run: pip install requests"}
        except Exception as e:
            return {"error": f"Location lookup failed: {e}"}


class TimeTool(Tool):
    def __init__(self):
        super().__init__(
            "time",
            "Only when the user explicitly asks about the current time, date, what time it is, or the current date."
        )

    def execute(self, location: str = "") -> dict:
        from datetime import datetime
        from ..config import DEFAULT_LOCATION
        from ..memory.facts import get_fact

        loc = location or DEFAULT_LOCATION or get_fact("location") or ""
        now = datetime.now()

        result = {
            "local_time": now.strftime("%I:%M:%S %p"),
            "date": now.strftime("%A, %B %d, %Y"),
            "timezone": now.astimezone().tzname() or "UTC",
            "timestamp": now.isoformat(),
        }

        if loc:
            result["location"] = loc

        if not location and not loc:
            try:
                import requests
                ip_resp = requests.get("http://ip-api.com/json", timeout=10)
                ip_data = ip_resp.json()
                result["approximate_location"] = f"{ip_data.get('city', '')}, {ip_data.get('regionName', '')}"
            except Exception:
                pass

        return result
