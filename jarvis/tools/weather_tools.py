from .base import Tool


def _get_location() -> str:
    from ..config import DEFAULT_LOCATION
    if DEFAULT_LOCATION:
        return DEFAULT_LOCATION
    from ..memory.facts import get_fact
    stored = get_fact("location")
    if stored:
        return stored
    return ""


def _fetch_weather(location: str = "") -> dict:
    import requests
    import urllib.parse

    loc = location or _get_location()
    if not loc:
        try:
            ip_resp = requests.get("http://ip-api.com/json", timeout=10)
            ip_data = ip_resp.json()
            loc = f"{ip_data.get('city', '')} {ip_data.get('region', '')}"
        except Exception:
            return {"error": "Could not determine location. Set DEFAULT_LOCATION in .env or tell me your location."}

    try:
        resp = requests.get(
            f"https://wttr.in/{urllib.parse.quote(loc)}?format=j1",
            timeout=15,
            headers={"User-Agent": "curl/7.68.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]
        return {
            "location": loc,
            "temperature": current.get("temp_F", "N/A") + "°F",
            "feels_like": current.get("FeelsLikeF", "N/A") + "°F",
            "humidity": current.get("humidity", "N/A") + "%",
            "wind": f"{current.get('windspeedMiles', 'N/A')} mph {current.get('winddir16Point', '')}",
            "conditions": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
            "cloud_cover": current.get("cloudcover", "N/A") + "%",
            "visibility": current.get("visibility", "N/A") + " miles",
            "uv_index": current.get("uvIndex", "N/A"),
        }
    except ImportError:
        return {"error": "requests not installed. Run: pip install requests"}
    except Exception as e:
        return {"error": f"Weather fetch failed: {e}"}


def _fetch_forecast(location: str = "") -> dict:
    import requests
    import urllib.parse

    loc = location or _get_location()
    if not loc:
        try:
            ip_resp = requests.get("http://ip-api.com/json", timeout=10)
            ip_data = ip_resp.json()
            loc = f"{ip_data.get('city', '')} {ip_data.get('region', '')}"
        except Exception:
            return {"error": "Could not determine location."}

    try:
        resp = requests.get(
            f"https://wttr.in/{urllib.parse.quote(loc)}?format=j1",
            timeout=15,
            headers={"User-Agent": "curl/7.68.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        days = []
        for i, day in enumerate(data.get("weather", [])[:4]):
            date = day.get("date", "Unknown")
            astro = day.get("astronomy", [{}])[0]
            hours = day.get("hourly", [])
            high = max((int(h.get("tempF", "0")) for h in hours), default=0)
            low = min((int(h.get("tempF", "999")) for h in hours), default=0)
            desc = hours[len(hours)//2].get("weatherDesc", [{}])[0].get("value", "") if hours else ""
            days.append({
                "date": date,
                "high": f"{high}°F",
                "low": f"{low}°F",
                "conditions": desc,
                "sunrise": astro.get("sunrise", "N/A"),
                "sunset": astro.get("sunset", "N/A"),
                "chance_of_rain": hours[len(hours)//2].get("chanceofrain", "N/A") + "%" if hours else "N/A",
            })
        return {"location": loc, "forecast": days}
    except ImportError:
        return {"error": "requests not installed. Run: pip install requests"}
    except Exception as e:
        return {"error": f"Forecast fetch failed: {e}"}


def _fetch_sunrise_sunset(location: str = "") -> dict:
    import requests

    loc = location or _get_location()
    if not loc:
        return {"error": "Could not determine location."}

    try:
        import urllib.parse
        geo = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(loc)}&format=json&limit=1",
            timeout=10,
            headers={"User-Agent": "JARVIS/1.3"}
        )
        geo.raise_for_status()
        geo_data = geo.json()
        if not geo_data:
            return {"error": f"Could not find coordinates for {loc}"}
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        from datetime import datetime as dt
        today = dt.now().strftime("%Y-%m-%d")
        ss_resp = requests.get(
            f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={today}&formatted=0",
            timeout=10
        )
        ss_resp.raise_for_status()
        ss_data = ss_resp.json()["results"]
        sunrise = ss_data["sunrise"]
        sunset = ss_data["sunset"]
        from datetime import datetime, timezone
        sunrise_local = datetime.fromisoformat(sunrise).astimezone(tz=None).strftime("%I:%M %p")
        sunset_local = datetime.fromisoformat(sunset).astimezone(tz=None).strftime("%I:%M %p")
        day_length = ss_data["day_length"]
        hours = int(day_length) // 3600
        minutes = (int(day_length) % 3600) // 60
        return {
            "location": loc,
            "sunrise": sunrise_local,
            "sunset": sunset_local,
            "daylight_hours": f"{hours}h {minutes}m",
        }
    except ImportError:
        return {"error": "requests not installed. Run: pip install requests"}
    except Exception as e:
        return {"error": f"Sunrise/sunset fetch failed: {e}"}


class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            "weather",
            "Only when the user explicitly asks about the current weather, temperature, conditions outside, or what it is like outside."
        )

    def execute(self, location: str = "") -> dict:
        return _fetch_weather(location)


class ForecastTool(Tool):
    def __init__(self):
        super().__init__(
            "forecast",
            "Only when the user explicitly asks about the weather forecast, prediction, or what weather to expect in the coming days."
        )

    def execute(self, location: str = "") -> dict:
        return _fetch_forecast(location)


class SunriseSunsetTool(Tool):
    def __init__(self):
        super().__init__(
            "sunrise_sunset",
            "Only when the user explicitly asks about sunrise, sunset, or daylight hours."
        )

    def execute(self, location: str = "") -> dict:
        return _fetch_sunrise_sunset(location)
