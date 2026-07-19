"""Test dynamic tool discovery."""

import pytest
from jarvis.tools.discovery import discover_tools
from jarvis.tools.registry import list_all


class TestDiscovery:
    def test_discover_builtin_tools(self):
        found = discover_tools(["jarvis.tools"])
        names = [t for t in found]
        assert "read_file" in names
        assert "write_file" in names
        assert "weather" in names

    def test_unknown_package_does_not_crash(self):
        found = discover_tools(["jarvis.does_not_exist"])
        assert found == []

    def test_all_tools_have_required_attributes(self):
        discover_tools(["jarvis.tools"])
        for spec in list_all():
            assert "name" in spec
            assert "description" in spec
            assert "category" in spec
            assert "risk" in spec

    def test_register_all(self):
        from jarvis.tools import register_all
        names = register_all()
        assert len(names) >= 14  # at least the original 14 tools
