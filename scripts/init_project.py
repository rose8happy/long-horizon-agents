#!/usr/bin/env python3
"""Compatibility entry point for the bundled project initializer."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runtime = Path(__file__).resolve().parents[1] / "skills/long-horizon-agents/scripts/init_project.py"
    runpy.run_path(str(runtime), run_name="__main__")
