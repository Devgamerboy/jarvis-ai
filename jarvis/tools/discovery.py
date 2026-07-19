"""Dynamic tool discovery — finds Tool subclasses in given package paths."""

import importlib
import inspect
import logging
import pkgutil
import sys

from .base import Tool
from .registry import register

logger = logging.getLogger("jarvis.discovery")


def discover_tools(package_paths: list[str]) -> list[str]:
    """Scan each dotted package path for Tool subclasses and register them.

    Returns a list of tool names that were successfully registered.
    Logs failures per module so a single broken plugin never blocks startup.
    """
    registered = []

    for pkg_path in package_paths:
        try:
            pkg = importlib.import_module(pkg_path)
        except Exception as exc:
            logger.warning("Could not import package %s: %s", pkg_path, exc)
            continue

        pkg_dir = getattr(pkg, "__path__", None)
        if not pkg_dir:
            continue

        for importer, modname, ispkg in pkgutil.iter_modules(pkg_dir):
            full_modname = f"{pkg_path}.{modname}"
            try:
                mod = importlib.import_module(full_modname)
            except Exception as exc:
                logger.error("Failed to load module %s: %s", full_modname, exc)
                continue

            for _name, cls in inspect.getmembers(mod, inspect.isclass):
                if cls is Tool:
                    continue
                if issubclass(cls, Tool) and not inspect.isabstract(cls):
                    try:
                        instance = cls()
                        register(instance)
                        registered.append(instance.name)
                        logger.info(
                            "Discovered tool '%s' from %s", instance.name, full_modname
                        )
                    except Exception as exc:
                        logger.error(
                            "Failed to instantiate %s in %s: %s",
                            cls.__name__,
                            full_modname,
                            exc,
                        )
    return registered
