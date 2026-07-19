"""Screenshot tool — capture the screen and save to disk."""

import os
import subprocess
import shutil
from datetime import datetime

from .base import Tool


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


class ScreenshotTool(Tool):
    def __init__(self):
        super().__init__(
            "screenshot",
            "Take a screenshot of the current screen and save it to a file.",
            category="Desktop",
            risk="sensitive",
        )

    def execute(self) -> dict:
        try:
            ss_dir = os.path.join(os.path.dirname(__file__), "..", "screenshots")
            os.makedirs(ss_dir, exist_ok=True)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(ss_dir, filename)

            if _have("gnome-screenshot"):
                subprocess.run(
                    ["gnome-screenshot", "-f", filepath],
                    capture_output=True, timeout=10, check=True,
                )
            elif _have("scrot"):
                subprocess.run(
                    ["scrot", filepath],
                    capture_output=True, timeout=10, check=True,
                )
            elif _have("import"):  # ImageMagick
                subprocess.run(
                    ["import", "-window", "root", filepath],
                    capture_output=True, timeout=10, check=True,
                )
            else:
                return {"error": "No screenshot utility found (install gnome-screenshot, scrot, or ImageMagick)."}

            if os.path.isfile(filepath):
                size_kb = round(os.path.getsize(filepath) / 1024, 1)
                return {"path": filepath, "size_kb": size_kb, "message": f"Screenshot saved to {filepath}"}
            return {"error": "Screenshot file was not created."}

        except subprocess.TimeoutExpired:
            return {"error": "Screenshot tool timed out."}
        except subprocess.CalledProcessError as e:
            return {"error": f"Screenshot failed: {e.stderr or e}"}
        except Exception as e:
            return {"error": f"Screenshot failed: {e}"}
