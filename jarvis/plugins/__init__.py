"""JARVIS Plugins — external tools loaded automatically at startup.

To create a plugin:

1.  Create a Python file in this directory (or a subdirectory with
    ``__init__.py``).

2.  Subclass ``jarvis.tools.base.Tool`` and implement the abstract
    ``execute(**kwargs) -> dict`` method.

    .. code-block:: python

        from jarvis.tools.base import Tool

        class HelloPlugin(Tool):
            def __init__(self):
                super().__init__(
                    name="hello",
                    description="A friendly greeting plugin",
                )

            def execute(self, name: str = "World") -> dict:
                return {"message": f"Hello, {name}!"}

3.  Add a module-level ``risk`` attribute or set ``self.risk`` in
    ``__init__``:

    .. code-block:: python

        self.risk = "safe"   # one of safe / write / sensitive / destructive

4.  Restart JARVIS. The plugin is discovered and registered automatically.

See ``jarvis/plugins/examples/`` for complete examples.
"""
