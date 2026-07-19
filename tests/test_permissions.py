"""Test permission system."""

from jarvis.tools.permissions import (
    RISK_SAFE,
    RISK_WRITE,
    RISK_SENSITIVE,
    RISK_DESTRUCTIVE,
    requires_confirmation,
)


class TestPermissions:
    def test_safe_no_confirmation(self):
        assert requires_confirmation(RISK_SAFE) is False

    def test_write_auto_confirm(self):
        assert requires_confirmation(RISK_WRITE, auto_confirm_write=True) is False

    def test_write_no_auto_confirm(self):
        assert requires_confirmation(RISK_WRITE, auto_confirm_write=False) is True

    def test_sensitive_requires_confirmation(self):
        assert requires_confirmation(RISK_SENSITIVE) is True

    def test_destructive_requires_confirmation(self):
        assert requires_confirmation(RISK_DESTRUCTIVE) is True

    def test_unknown_level_falls_back(self):
        assert requires_confirmation("unknown") is False
