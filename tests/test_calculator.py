"""Test calculator tool."""

from jarvis.tools.calculator_tool import CalculatorTool


class TestCalculator:
    def setup_method(self):
        self.tool = CalculatorTool()

    def test_addition(self):
        r = self.tool.execute(expression="25 + 14")
        assert r["result"] == 39.0

    def test_multiplication(self):
        r = self.tool.execute(expression="25 * 14")
        assert r["result"] == 350.0

    def test_division(self):
        r = self.tool.execute(expression="100 / 4")
        assert r["result"] == 25.0

    def test_sqrt(self):
        r = self.tool.execute(expression="sqrt(625)")
        assert r["result"] == 25.0

    def test_power(self):
        r = self.tool.execute(expression="2 ** 10")
        assert r["result"] == 1024.0

    def test_percentage_of(self):
        r = self.tool.execute(expression="18% of 340")
        assert abs(r["result"] - 61.2) < 0.01

    def test_parentheses(self):
        r = self.tool.execute(expression="(2 + 3) * 4")
        assert r["result"] == 20.0

    def test_invalid_expression(self):
        r = self.tool.execute(expression="hello world")
        assert "error" in r
