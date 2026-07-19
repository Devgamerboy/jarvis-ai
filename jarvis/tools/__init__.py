"""JARVIS tool framework — automated discovery + legacy manual registration."""

import logging

logger = logging.getLogger("jarvis.tools")

from .base import Tool
from .registry import register, get, list_all, list_by_category, list_names, execute
from .discovery import discover_tools

_AUTO_LOAD_PACKAGES = ["jarvis.tools", "jarvis.plugins"]


def register_all():
    registered_names: list[str] = []

    # 1. Discover from tools and plugins
    found = discover_tools(_AUTO_LOAD_PACKAGES)
    registered_names.extend(found)

    if registered_names:
        logger.info("Auto-registered tools: %s", ", ".join(registered_names))

    return registered_names
