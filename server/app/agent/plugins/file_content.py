"""Builtin MCP plugin: get file content.

Runs as an MCP stdio server (FastMCP). Exposes tools to read a text file and
list a directory. Access can be confined to a base directory via the
AGENT_FILE_BASE_DIR environment variable (set through the plugin config_json).

Run standalone:  python file_content.py
"""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("file_content")

_MAX_CHARS = 8000


def _base_dir() -> Path | None:
    raw = os.environ.get("AGENT_FILE_BASE_DIR", "").strip()
    if not raw:
        return None
    return Path(raw).resolve()


def _resolve_within_base(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()
    base = _base_dir()
    if base is not None and base not in candidate.parents and candidate != base:
        raise PermissionError(f"Path {candidate} is outside the allowed base dir {base}")
    return candidate


@mcp.tool()
def read_file(path: str, max_chars: int = _MAX_CHARS) -> str:
    """Read a UTF-8 text file and return its content.

    Args:
        path: File path to read.
        max_chars: Maximum characters to return (default 8000).
    """
    try:
        target = _resolve_within_base(path)
        if not target.exists() or not target.is_file():
            return f"Error: file not found: {target}"
        text = target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path}: {exc}"
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + "\n...[truncated]"
    return text


@mcp.tool()
def list_dir(path: str = ".") -> str:
    """List entries of a directory (one per line, dirs suffixed with '/').

    Args:
        path: Directory path to list (default current dir).
    """
    try:
        target = _resolve_within_base(path)
        if not target.exists() or not target.is_dir():
            return f"Error: directory not found: {target}"
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = [f"{e.name}/" if e.is_dir() else e.name for e in entries]
    except Exception as exc:  # noqa: BLE001
        return f"Error listing {path}: {exc}"
    return "\n".join(lines) if lines else "(empty)"


if __name__ == "__main__":
    mcp.run()
