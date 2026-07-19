"""Desktop launcher — open approved applications, URLs, and folders."""

import os
import shutil
import subprocess

from .base import Tool


_APP_ALIASES = {
    "browser": "firefox",
    "firefox": "firefox",
    "chrome": "google-chrome",
    "chromium": "chromium-browser",
    "terminal": "gnome-terminal",
    "code": "code",
    "vscode": "code",
    "files": "nautilus",
    "nautilus": "nautilus",
    "calculator": "gnome-calculator",
    "settings": "gnome-control-center",
}


def _find_app(app: str) -> str | None:
    app = app.lower().strip()
    cmd = _APP_ALIASES.get(app)
    if cmd and shutil.which(cmd):
        return cmd
    if shutil.which(app):
        return app
    return None


class LaunchAppTool(Tool):
    def __init__(self):
        super().__init__(
            "launch_app",
            "Launch an approved desktop application (browser, terminal, code editor, etc.).",
            category="Desktop",
            risk="write",
        )

    def execute(self, app: str = "") -> dict:
        if not app:
            return {"error": "Application name is required."}
        cmd = _find_app(app)
        if cmd is None:
            return {"error": f"Application '{app}' not found or not in approved list."}
        try:
            subprocess.Popen([cmd])
            return {"app": app, "command": cmd, "message": f"Launched {app}."}
        except Exception as e:
            return {"error": f"Failed to launch {app}: {e}"}


class OpenUrlTool(Tool):
    def __init__(self):
        super().__init__(
            "open_url",
            "Open a URL in the default web browser.",
            category="Desktop",
            risk="write",
        )

    def execute(self, url: str = "") -> dict:
        if not url:
            return {"error": "URL is required."}
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", url])
            elif shutil.which("open"):
                subprocess.Popen(["open", url])
            else:
                import webbrowser
                webbrowser.open(url)
            return {"url": url, "message": f"Opened {url}."}
        except Exception as e:
            return {"error": f"Failed to open URL: {e}"}
