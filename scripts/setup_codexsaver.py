#!/usr/bin/env python3
"""Save a DeepSeek key locally without placing it in arguments or shell history."""

from __future__ import annotations

import getpass
import os
from pathlib import Path
import sys


def main() -> int:
    runtime = Path.home() / ".local/share/codexsaver/.venv/bin/python3"
    if not runtime.is_file():
        raise SystemExit(f"CodexSaver's Python environment is missing: {runtime}")
    if Path(sys.prefix).resolve() != runtime.parent.parent.resolve():
        os.execv(str(runtime), [str(runtime), str(Path(__file__).resolve())])

    from codexsaver.config import save_provider_config
    from codexsaver.pi_agent import save_pi_deepseek_auth

    if not sys.stdin.isatty():
        raise SystemExit("Run this script in a terminal so the key can be entered privately.")
    try:
        key = getpass.getpass("DeepSeek API key (hidden): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled; no key saved.")
        return 1
    if not key:
        raise SystemExit("No key entered; no key saved.")

    provider = save_provider_config(provider="deepseek", api_key=key)
    worker = save_pi_deepseek_auth(key)
    print(f"Saved CodexSaver credentials: {provider['config_path']}")
    print(f"Saved Pi Agent credentials: {worker['path']}")
    print("Both credential files use owner-only (0600) permissions.")
    print("Restart the CodexSaver MCP server, then run a small live delegation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
