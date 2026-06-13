"""Public facade for the agent module.

Used by:
  - the chat proxy (run_agent) when request.use_agent is true
  - the admin API (resolve/invalidate + plugin debug) for orchestrator / editor
"""

import json
from typing import Any, AsyncIterator, Dict, List, Optional

from ..core.database import SessionLocal
from ..core.threadpool import run_blocking
from .core import cache, repository
from .core.cache import ResolvedFlow, ResolvedSubAgent
from .core.plugin_runtime import build_plugin_spec, debug_plugin
from .core.runner import run_flow


def _parse_sub_agents(raw: Optional[str]) -> List[ResolvedSubAgent]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    subs: List[ResolvedSubAgent] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        plugin_ids = item.get("plugin_ids") or []
        try:
            plugin_ids = [int(x) for x in plugin_ids]
        except (TypeError, ValueError):
            plugin_ids = []
        subs.append(
            ResolvedSubAgent(
                name=str(item.get("name") or "SubAgent"),
                instructions=str(item.get("instructions") or ""),
                model=item.get("model") or None,
                plugin_ids=plugin_ids,
                tool_name=item.get("tool_name") or None,
                tool_description=item.get("tool_description") or None,
            )
        )
    return subs


def _resolve_flow_blocking(app_key: str) -> Optional[ResolvedFlow]:
    db = SessionLocal()
    try:
        config = repository.get_flow_config(db, app_key)
        if not config or not config.enabled:
            return None

        plugins: Dict[int, Any] = {}
        for p in repository.list_enabled_plugins(db, app_key):
            try:
                plugins[p.id] = build_plugin_spec(
                    plugin_id=p.id,
                    app_key=app_key,
                    plugin_name=p.plugin_name,
                    plugin_type=p.plugin_type,
                    builtin_key=p.builtin_key,
                    script_content=p.script_content,
                    config_json=p.config_json,
                )
            except Exception as exc:  # skip a broken plugin, keep the flow usable
                print(f"[agent] skip plugin {p.id} ({p.plugin_name}): {exc}")

        return ResolvedFlow(
            app_key=app_key,
            name=config.name or "Agent",
            instructions=config.instructions or "",
            mode=config.mode or "single",
            model=config.model,
            max_turns=int(config.max_turns or 10),
            enabled=bool(config.enabled),
            sub_agents=_parse_sub_agents(config.sub_agents),
            plugins=plugins,
        )
    finally:
        db.close()


def has_enabled_flow_blocking(app_key: str) -> bool:
    db = SessionLocal()
    try:
        config = repository.get_flow_config(db, app_key)
        return bool(config and config.enabled)
    finally:
        db.close()


async def get_resolved_flow(app_key: str, force_reload: bool = False) -> Optional[ResolvedFlow]:
    if not force_reload:
        cached = cache.get(app_key)
        if cached is not None:
            return cached
    flow = await run_blocking(_resolve_flow_blocking, app_key)
    if flow is not None:
        cache.put(app_key, flow)
    return flow


def invalidate(app_key: str) -> None:
    """Drop the cached resolved flow so the next request rebuilds the instance."""
    cache.invalidate(app_key)


async def run_agent(
    app_key: str,
    messages: List[dict],
    model_label: str,
    extra_instructions: Optional[str] = None,
    stream: bool = False,
) -> AsyncIterator[Dict[str, Any]]:
    flow = await get_resolved_flow(app_key)
    if flow is None:
        raise RuntimeError(f"No enabled agent flow configured for app_key={app_key}")
    async for chunk in run_flow(
        flow,
        messages,
        model_label=model_label,
        extra_instructions=extra_instructions,
        stream=stream,
    ):
        yield chunk


async def debug_plugin_run(
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
) -> Dict[str, Any]:
    return await debug_plugin(
        plugin_id=plugin_id,
        app_key=app_key,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        builtin_key=builtin_key,
        script_content=script_content,
        config_json=config_json,
        tool_name=tool_name,
        tool_args=tool_args,
    )
