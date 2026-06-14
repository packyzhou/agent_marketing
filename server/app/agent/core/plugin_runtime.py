"""MCP plugin runtime.

Two responsibilities:
  1. Materialize a plugin (builtin or custom) into a runnable MCP stdio script and
     produce the launch params consumed by agents.mcp.MCPServerStdio.
  2. Debug-run a plugin standalone (list tools / call a tool) for the plugin editor.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Bundled builtin plugin scripts live next to this package.
BUILTIN_DIR = Path(__file__).resolve().parents[1] / "plugins"
# Custom plugin scripts are written here, namespaced per appKey.
RUNTIME_DIR = Path("./agent_plugins_runtime")

# builtin_key -> bundled script filename
BUILTIN_PLUGINS: Dict[str, str] = {
    "web_query": "web_query.py",
    "file_content": "file_content.py",
}


@dataclass
class PluginSpec:
    """Everything needed to launch one plugin as an MCP stdio server."""

    plugin_id: int
    name: str
    description: str
    command: str
    args: List[str]
    env: Dict[str, str] = field(default_factory=dict)

    def to_mcp_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"command": self.command, "args": list(self.args)}
        if self.env:
            params["env"] = {**os.environ, **self.env}
        return params


def _safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in {"_", "-"} else "_" for c in (value or "plugin"))


def _parse_config_json(config_json: Optional[str]) -> Dict[str, Any]:
    if not config_json:
        return {}
    try:
        data = json.loads(config_json)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def resolve_script_path(
    *,
    plugin_id: int,
    app_key: str,
    plugin_name: str,
    plugin_type: str,
    builtin_key: Optional[str],
    script_content: Optional[str],
) -> Path:
    """Return a runnable script path, writing custom scripts to disk as needed."""
    if (plugin_type or "").lower() == "builtin":
        filename = BUILTIN_PLUGINS.get((builtin_key or "").strip())
        if not filename:
            raise ValueError(f"Unknown builtin plugin: {builtin_key!r}")
        path = BUILTIN_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Builtin plugin script missing: {path}")
        return path

    if not script_content or not script_content.strip():
        raise ValueError("Custom plugin has empty script_content")

    target_dir = RUNTIME_DIR / _safe_name(app_key)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"plugin_{plugin_id}_{_safe_name(plugin_name)}.py"
    # Rewrite only when content changed to avoid churn.
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing != script_content:
        path.write_text(script_content, encoding="utf-8")
    return path


def build_plugin_spec(
    *,
    plugin_id: int,
    app_key: str,
    plugin_name: str,
    plugin_type: str,
    builtin_key: Optional[str],
    script_content: Optional[str],
    config_json: Optional[str],
) -> PluginSpec:
    script_path = resolve_script_path(
        plugin_id=plugin_id,
        app_key=app_key,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        builtin_key=builtin_key,
        script_content=script_content,
    )
    cfg = _parse_config_json(config_json)
    env = {str(k): str(v) for k, v in (cfg.get("env") or {}).items()}
    # Always expose the owning appKey so plugins can attribute data they persist
    # back through the platform API (config_json env can still override it).
    env.setdefault("AGENT_APP_KEY", app_key or "")
    extra_args = [str(a) for a in (cfg.get("args") or [])]
    command = cfg.get("command") or sys.executable
    return PluginSpec(
        plugin_id=plugin_id,
        name=plugin_name,
        description=plugin_name if not plugin_type else (plugin_name or ""),
        command=command,
        args=[str(script_path), *extra_args],
        env=env,
    )


async def debug_plugin(
    *,
    plugin_id: int,
    app_key: str,
    plugin_name: str,
    plugin_type: str,
    builtin_key: Optional[str],
    script_content: Optional[str],
    config_json: Optional[str],
    tool_name: Optional[str] = None,
    tool_args: Optional[Dict[str, Any]] = None,
    timeout_seconds: float = 30.0,
) -> Dict[str, Any]:
    """Launch the plugin as an MCP stdio server, list tools, optionally call one.

    Returns a JSON-serializable dict: {tools: [...], called: {...} | None}.
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "mcp package is not installed. Run: pip install mcp openai-agents"
        ) from exc

    import asyncio

    spec = build_plugin_spec(
        plugin_id=plugin_id,
        app_key=app_key,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        builtin_key=builtin_key,
        script_content=script_content,
        config_json=config_json,
    )
    server_params = StdioServerParameters(
        command=spec.command,
        args=spec.args,
        env=spec.env or None,
    )

    print(
        "[plugin debug] 插件输入 | "
        f"app_key:{app_key} | plugin:{plugin_name} | type:{plugin_type} | "
        f"builtin_key:{builtin_key} | command:{spec.command} | args:{spec.args} | "
        f"env_keys:{sorted(spec.env.keys())} | tool_name:{tool_name} | "
        f"tool_args:{json.dumps(tool_args or {}, ensure_ascii=False)}"
    )

    async def _run() -> Dict[str, Any]:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                tools = [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "input_schema": getattr(t, "inputSchema", None),
                    }
                    for t in listed.tools
                ]
                called = None
                if tool_name:
                    print(
                        f"[plugin debug] 调用工具前 | tool_name:{tool_name} | "
                        f"tool_args:{json.dumps(tool_args or {}, ensure_ascii=False)}"
                    )
                    result = await session.call_tool(tool_name, tool_args or {})
                    called = {
                        "tool": tool_name,
                        "args": tool_args or {},
                        "is_error": bool(getattr(result, "isError", False)),
                        "content": _serialize_tool_content(result),
                    }
                return {"tools": tools, "called": called}

    return await asyncio.wait_for(_run(), timeout=timeout_seconds)


def _serialize_tool_content(result: Any) -> Any:
    """Flatten MCP CallToolResult content blocks into plain JSON."""
    blocks = getattr(result, "content", None)
    if blocks is None:
        return None
    out = []
    for block in blocks:
        text = getattr(block, "text", None)
        if text is not None:
            out.append({"type": "text", "text": text})
            continue
        data = getattr(block, "data", None)
        if data is not None:
            out.append({"type": getattr(block, "type", "data"), "data": str(data)[:2000]})
            continue
        out.append({"type": getattr(block, "type", "unknown"), "repr": str(block)[:2000]})
    return out
