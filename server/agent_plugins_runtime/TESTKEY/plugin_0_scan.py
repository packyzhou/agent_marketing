"""Example custom MCP plugin: scan a directory and save the listing to the DB.

Paste this into the "Agent Plugin Editor" as a *custom* plugin. It exposes one
tool, `scan_and_save(path)`, which:
  1. lists the files/dirs directly under `path`, and
  2. persists the listing through the platform API
     (POST /api/agent/file-records), which writes a row to tb_file_scan_record.

Environment (auto-provided by the agent runtime; both optional to override via
the plugin's config_json "env"):
  AGENT_APP_KEY   the owning tenant app_key (injected automatically)
  AGENT_API_BASE  platform base URL, default http://127.0.0.1:8000

Run standalone:  python scan_and_save_plugin.py
"""

import os
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("file_scan_saver")

API_BASE = os.environ.get("AGENT_API_BASE", "http://127.0.0.1:8000").rstrip("/")
APP_KEY = os.environ.get("AGENT_APP_KEY", os.environ.get("APP_KEY", ""))


@mcp.tool()
def scan_and_save(path: str) -> str:
    """List the entries under a directory path and save them to the database.

    Args:
        path: Absolute or ~-relative directory path to scan.
    """
    target = Path(path).expanduser()
    if not target.exists():
        return f"Path not found: {target}"
    if not target.is_dir():
        return f"Not a directory: {target}"

    entries = []
    try:
        for p in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            entries.append(
                {
                    "name": p.name,
                    "is_dir": p.is_dir(),
                    "size": p.stat().st_size if p.is_file() else None,
                }
            )
    except PermissionError:
        return f"Permission denied: {target}"

    if not APP_KEY:
        return (
            f"Found {len(entries)} entries under {target}, but AGENT_APP_KEY is not set "
            f"so nothing was saved. Set it via the plugin config_json env."
        )

    try:
        resp = httpx.post(
            f"{API_BASE}/api/agent/file-records",
            json={"app_key": APP_KEY, "path": str(target), "files": entries},
            timeout=20.0,
        )
        resp.raise_for_status()
        saved = resp.json()
    except Exception as exc:  # noqa: BLE001 - report a readable error to the model
        return f"Listed {len(entries)} entries under {target} but failed to save: {exc}"

    return (
        f"Found {len(entries)} entries under {target} and saved them as "
        f"record #{saved.get('id')} (file_count={saved.get('file_count')})."
    )


if __name__ == "__main__":
    mcp.run()
