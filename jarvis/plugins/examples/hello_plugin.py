"""Example plugin: a friendly greeting tool."""

from jarvis.tools.base import Tool


class HelloPlugin(Tool):
    """A minimal example plugin — adds a 'hello' tool."""

    def __init__(self):
        super().__init__(
            name="hello",
            description="A friendly greeting plugin — says hello to the user.",
        )
        self.risk = "safe"

    def execute(self, name: str = "World") -> dict:
        return {"message": f"Hello, {name}!"}
