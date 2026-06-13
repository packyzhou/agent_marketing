"""Example custom MCP plugin: list a directory and (optionally) save it to the DB.

Paste this into the "Agent Plugin Editor" as a *custom* plugin. It exposes two
tools:

  list_files(path)      -> returns the file/dir NAMES under `path` as a JSON list.
                           Pure read, no network — ideal for debugging. To debug:
                           set Tool Name = list_files and Tool Args = {"path": "/some/dir"}.

  scan_and_save(path)   -> lists the entries AND persists them to the database via
                           POST /api/agent/file-records (writes tb_file_scan_record),
                           returning the names plus the saved record id.
                           NOTE: this calls back into the platform, so the server must
                           run with >=2 workers (a single --reload worker will stall).

Environment (auto-provided by the agent runtime; override via config_json "env"):
  AGENT_APP_KEY   the owning tenant app_key (injected automatically)
  AGENT_API_BASE  platform base URL, default http://127.0.0.1:8000

Run standalone:  python scan_and_save_plugin.py
"""

import json
import os
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("file_scan_saver")

API_BASE = os.environ.get("AGENT_API_BASE", "http://127.0.0.1:8000").rstrip("/")
APP_KEY = os.environ.get("AGENT_APP_KEY", os.environ.get("APP_KEY", ""))


def _scan(path: str):
    """Return (resolved_target, entries) or raise a readable error."""
    target = Path(path).expanduser()
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {target}")
    entries = []
    for p in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        entries.append(
            {
                "name": p.name,
                "is_dir": p.is_dir(),
                "size": p.stat().st_size if p.is_file() else None,
            }
        )
    return target, entries


@mcp.tool()
def list_files(path: str) -> str:
    """List the file and directory names directly under `path`.

    Args:
        path: Absolute or ~-relative directory path on the machine running the server.

    Returns:
        A JSON object: {"path", "count", "files": [names...]} where directory
        names are suffixed with "/".
    """
    try:
        target, entries = _scan(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return str(exc)
    except PermissionError:
        return f"Permission denied: {path}"
    names = [f"{e['name']}/" if e["is_dir"] else e["name"] for e in entries]
    return json.dumps(
        {"path": str(target), "count": len(names), "files": names},
        ensure_ascii=False,
    )


@mcp.tool()
def scan_and_save(path: str) -> str:
    """List the entries under `path` AND save the listing to the database.

    Args:
        path: Absolute or ~-relative directory path to scan.
    """
    try:
        target, entries = _scan(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return str(exc)
    except PermissionError:
        return f"Permission denied: {path}"

    names = [f"{e['name']}/" if e["is_dir"] else e["name"] for e in entries]
    if not APP_KEY:
        return json.dumps(
            {"path": str(target), "count": len(names), "files": names, "saved": False,
             "note": "AGENT_APP_KEY not set; listing only"},
            ensure_ascii=False,
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
        return json.dumps(
            {"path": str(target), "count": len(names), "files": names, "saved": False,
             "error": str(exc)},
            ensure_ascii=False,
        )

    return json.dumps(
        {"path": str(target), "count": len(names), "files": names, "saved": True,
         "record_id": saved.get("id")},
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run()
