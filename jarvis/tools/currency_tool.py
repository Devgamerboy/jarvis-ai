"""Currency conversion tool using a free exchange-rate API with caching."""

import json
import os
import time
from .base import Tool

from ..config import CURRENCY_CACHE_TTL

_CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "cache", "rates.json")
_CACHE_FILE = os.path.normpath(_CACHE_FILE)


def _load_cache():
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        if time.time() - data.get("timestamp", 0) < CURRENCY_CACHE_TTL:
            return data.get("rates")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def _save_cache(rates: dict):
    os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"timestamp": time.time(), "rates": rates}, f)


def _fetch_rates() -> dict | None:
    cache = _load_cache()
    if cache:
        return cache

    try:
        import requests
        resp = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates")
        if rates:
            _save_cache(rates)
        return rates
    except Exception:
        return None


class CurrencyConvertTool(Tool):
    """Convert between world currencies using live exchange rates."""

    def __init__(self):
        super().__init__(
            name="currency_convert",
            description="Convert between currencies (e.g. USD to EUR) using live exchange rates. Rates may be delayed.",
            category="Utilities",
            risk="safe",
        )

    def execute(self, value: float = 0, from_currency: str = "", to_currency: str = "", expression: str = "") -> dict:
        if expression:
            parts = expression.upper().replace(" TO ", "|").split("|")
            if len(parts) == 2:
                vparts = parts[0].strip().split(None, 1)
                if len(vparts) == 2:
                    try:
                        value = float(vparts[0])
                        from_currency = vparts[1]
                    except ValueError:
                        pass
                    to_currency = parts[1].strip()

        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()

        if not from_currency or not to_currency:
            return {"error": "Specify from_currency, to_currency, and value (or expression like '100 USD to EUR')."}

        rates = _fetch_rates()
        if rates is None:
            return {"error": "Could not fetch exchange rates. Check internet connection."}

        if from_currency not in rates:
            return {"error": f"Unknown currency: {from_currency}"}
        if to_currency not in rates:
            return {"error": f"Unknown currency: {to_currency}"}

        usd_value = value / rates[from_currency]
        result = round(usd_value * rates[to_currency], 2)

        return {
            "from": f"{value} {from_currency}",
            "to": f"{result} {to_currency}",
            "rate": round(rates[to_currency] / rates[from_currency], 6),
            "rates_timestamp": "cached — may be up to 24h delayed",
        }
