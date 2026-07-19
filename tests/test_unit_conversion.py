"""Test unit conversion tool."""

from jarvis.tools.unit_conversion_tool import UnitConvertTool


class TestUnitConvert:
    def setup_method(self):
        self.tool = UnitConvertTool()

    def test_miles_to_km(self):
        r = self.tool.execute(value=5, from_unit="miles", to_unit="km")
        assert abs(r["value"] - 8.04672) < 0.01

    def test_cups_to_ml(self):
        r = self.tool.execute(value=7, from_unit="cups", to_unit="ml")
        assert r["value"] > 1600

    def test_fahrenheit_to_celsius(self):
        r = self.tool.execute(value=80, from_unit="f", to_unit="c")
        assert abs(r["value"] - 26.67) < 0.1

    def test_pounds_to_kg(self):
        r = self.tool.execute(value=150, from_unit="pounds", to_unit="kg")
        assert abs(r["value"] - 68.04) < 0.1

    def test_expression_parsing(self):
        r = self.tool.execute(expression="5 miles to km")
        assert abs(r["value"] - 8.04672) < 0.01

    def test_unknown_unit(self):
        r = self.tool.execute(value=1, from_unit="zzz", to_unit="km")
        assert "Unknown unit" in r.get("error", "")

    def test_incompatible_units(self):
        r = self.tool.execute(value=1, from_unit="kg", to_unit="km")
        assert "Cannot convert" in r.get("error", "")
