"""Unit conversion tool — length, weight, volume, temperature, speed, area."""

from .base import Tool


_LENGTH = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
    "ft": 0.3048, "feet": 0.3048, "foot": 0.3048,
    "yd": 0.9144, "yards": 0.9144, "yard": 0.9144,
    "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
}

_WEIGHT = {
    "mg": 0.000001, "g": 0.001, "kg": 1.0, "tonne": 1000.0,
    "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
    "lb": 0.453592, "lbs": 0.453592, "pound": 0.453592, "pounds": 0.453592,
    "stone": 6.35029,
}

_VOLUME = {
    "ml": 0.001, "milliliter": 0.001, "milliliters": 0.001,
    "l": 1.0, "liter": 1.0, "liters": 1.0, "litre": 1.0, "litres": 1.0,
    "tsp": 0.00492892, "teaspoon": 0.00492892, "teaspoons": 0.00492892,
    "tbsp": 0.0147868, "tablespoon": 0.0147868, "tablespoons": 0.0147868,
    "cup": 0.236588, "cups": 0.236588,
    "pt": 0.473176, "pint": 0.473176, "pints": 0.473176,
    "qt": 0.946353, "quart": 0.946353, "quarts": 0.946353,
    "gal": 3.78541, "gallon": 3.78541, "gallons": 3.78541,
    "fl_oz": 0.0295735, "fluid_oz": 0.0295735,
}

_TEMP = {
    "c": "celsius", "celsius": "celsius",
    "f": "fahrenheit", "fahrenheit": "fahrenheit",
    "k": "kelvin", "kelvin": "kelvin",
}

_SPEED = {
    "m/s": 1.0, "meter_per_second": 1.0, "meters_per_second": 1.0,
    "km/h": 0.277778, "kph": 0.277778, "kmh": 0.277778,
    "mph": 0.44704, "mile_per_hour": 0.44704, "miles_per_hour": 0.44704,
    "knot": 0.514444, "knots": 0.514444,
}

_AREA = {
    "mm2": 0.000001, "cm2": 0.0001, "m2": 1.0, "km2": 1000000.0,
    "ha": 10000.0, "hectare": 10000.0, "hectares": 10000.0,
    "in2": 0.00064516, "ft2": 0.092903, "ac": 4046.86, "acre": 4046.86, "acres": 4046.86,
    "mi2": 2589988.1, "sq_mi": 2589988.1,
}

_CATEGORIES = {
    "length": _LENGTH,
    "weight": _WEIGHT,
    "volume": _VOLUME,
    "temperature": _TEMP,
    "speed": _SPEED,
    "area": _AREA,
}


def _find_unit(unit: str):
    unit = unit.lower().strip()
    for cat_name, table in _CATEGORIES.items():
        if unit in table:
            return cat_name, table, unit
    return None, None, None


def _convert(value: float, from_unit: str, to_unit: str) -> dict:
    from_cat, from_table, from_key = _find_unit(from_unit)
    to_cat, to_table, to_key = _find_unit(to_unit)

    if from_cat is None:
        return {"error": f"Unknown unit: '{from_unit}'"}
    if to_cat is None:
        return {"error": f"Unknown unit: '{to_unit}'"}
    if from_cat != to_cat:
        return {"error": f"Cannot convert {from_cat} to {to_cat}"}

    if from_cat == "temperature":
        result = _convert_temperature(value, from_key, to_key)
    else:
        base = value * from_table[from_key]
        result = base / to_table[to_key]

    return {
        "from": f"{value} {from_unit}",
        "to": f"{result} {to_unit}",
        "value": result,
        "unit": to_unit,
    }


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return value
    if from_unit in ("c", "celsius"):
        if to_unit in ("f", "fahrenheit"):
            return (value * 9/5) + 32
        if to_unit == "kelvin":
            return value + 273.15
    if from_unit in ("f", "fahrenheit"):
        if to_unit in ("c", "celsius"):
            return (value - 32) * 5/9
        if to_unit == "kelvin":
            return (value - 32) * 5/9 + 273.15
    if from_unit == "kelvin":
        if to_unit in ("c", "celsius"):
            return value - 273.15
        if to_unit in ("f", "fahrenheit"):
            return (value - 273.15) * 9/5 + 32
    return value


class UnitConvertTool(Tool):
    """Convert between units of length, weight, volume, temperature, speed, area."""

    def __init__(self):
        super().__init__(
            name="unit_convert",
            description="Convert units across length, weight, volume, temperature, speed, and area. Example: '5 miles to km', '80 F to C'.",
            category="Utilities",
            risk="safe",
        )

    def execute(self, value: float = 0, from_unit: str = "", to_unit: str = "", expression: str = "") -> dict:
        if expression:
            parts = expression.lower().replace(" to ", "|").replace(" in ", "|").split("|")
            if len(parts) == 2:
                vparts = parts[0].strip().split(None, 1)
                if len(vparts) == 2:
                    try:
                        value = float(vparts[0])
                        from_unit = vparts[1]
                    except ValueError:
                        pass
                    to_unit = parts[1].strip()

        if not from_unit or not to_unit:
            return {"error": "Specify from_unit and to_unit, or an expression like '5 miles to km'."}

        return _convert(value, from_unit, to_unit)
