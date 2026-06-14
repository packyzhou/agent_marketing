"""Admin API for the agent module.

Powers the web console's "Agent Orchestrator" (flow config + plugin
association) and "Agent Plugin Editor" (edit / debug / save). Every write
invalidates the cached resolved flow so the appKey's Agent instance is rebuilt
on the next chat request.
"""

import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...agent import service as agent_service
from ...agent.core import repository
from ...agent.core.plugin_runtime import BUILTIN_PLUGINS
from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.utils import dt_to_local_str
from ...models.agent_flow import AgentFlowConfig, AgentPluginRef
from ...models.user import User

router = APIRouter()

VALID_MODES = {"single", "tool", "handoff"}
VALID_PLUGIN_TYPES = {"builtin", "custom"}


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #


class SubAgentSchema(BaseModel):
    name: str
    instructions: str = ""
    model: Optional[str] = None
    plugin_ids: List[int] = []
    tool_name: Optional[str] = None
    tool_description: Optional[str] = None


class FlowConfigUpsert(BaseModel):
    name: str = "Agent"
    instructions: Optional[str] = None
    mode: str = "single"
    model: Optional[str] = None
    max_turns: int = 10
    sub_agents: List[SubAgentSchema] = []
    enabled: bool = True


class FlowConfigResponse(BaseModel):
    id: int
    app_key: str
    name: str
    instructions: Optional[str]
    mode: str
    model: Optional[str]
    max_turns: int
    sub_agents: List[Any]
    enabled: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class PluginUpsert(BaseModel):
    plugin_name: str
    description: Optional[str] = None
    plugin_type: str = "custom"
    builtin_key: Optional[str] = None
    script_content: Optional[str] = None
    config_json: Optional[Any] = None
    enabled: bool = True
    sort_order: int = 0


class PluginResponse(BaseModel):
    id: int
    flow_config_id: int
    app_key: str
    plugin_name: str
    description: Optional[str]
    plugin_type: str
    builtin_key: Optional[str]
    script_content: Optional[str]
    config_json: Optional[str]
    enabled: bool
    sort_order: int
    created_at: Optional[str]
    updated_at: Optional[str]


class PluginDebugRequest(BaseModel):
    app_key: str
    plugin_name: str = "debug_plugin"
    plugin_type: str = "custom"
    builtin_key: Optional[str] = None
    script_content: Optional[str] = None
    config_json: Optional[Any] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    plugin_id: Optional[int] = None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _describe_exception(exc: BaseException, _depth: int = 0) -> str:
    """Flatten exceptions, unwrapping ExceptionGroup (anyio TaskGroup) sub-exceptions.

    MCP stdio runs inside an anyio TaskGroup, so a plugin failure (e.g. a missing
    import in the script) surfaces as the opaque "unhandled errors in a TaskGroup
    (N sub-exceptions)". This recurses into the real sub-exceptions so the UI shows
    e.g. "ModuleNotFoundError: No module named 'trafilatura'".
    """
    subs = getattr(exc, "exceptions", None)
    if subs and _depth < 5:
        inner = "; ".join(_describe_exception(s, _depth + 1) for s in subs)
        return inner or f"{type(exc).__name__}: {exc}"
    text = str(exc).strip()
    return f"{type(exc).__name__}: {text}" if text else type(exc).__name__


def _normalize_config_json(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


def _flow_to_response(config: AgentFlowConfig) -> FlowConfigResponse:
    try:
        sub_agents = json.loads(config.sub_agents) if config.sub_agents else []
        if not isinstance(sub_agents, list):
            sub_agents = []
    except (json.JSONDecodeError, TypeError):
        sub_agents = []
    return FlowConfigResponse(
        id=config.id,
        app_key=config.app_key,
        name=config.name,
        instructions=config.instructions,
        mode=config.mode,
        model=config.model,
        max_turns=config.max_turns,
        sub_agents=sub_agents,
        enabled=bool(config.enabled),
        created_at=dt_to_local_str(config.created_at),
        updated_at=dt_to_local_str(config.updated_at),
    )


def _plugin_to_response(plugin: AgentPluginRef) -> PluginResponse:
    return PluginResponse(
        id=plugin.id,
        flow_config_id=plugin.flow_config_id,
        app_key=plugin.app_key,
        plugin_name=plugin.plugin_name,
        description=plugin.description,
        plugin_type=plugin.plugin_type,
        builtin_key=plugin.builtin_key,
        script_content=plugin.script_content,
        config_json=plugin.config_json,
        enabled=bool(plugin.enabled),
        sort_order=plugin.sort_order,
        created_at=dt_to_local_str(plugin.created_at),
        updated_at=dt_to_local_str(plugin.updated_at),
    )


# --------------------------------------------------------------------------- #
# Builtins catalog
# --------------------------------------------------------------------------- #


@router.get("/agent/plugin-builtins")
async def list_builtin_plugins(current_user: User = Depends(get_current_user)):
    catalog = {
        "web_query": "查询网站：抓取网页正文文本 / 拉取 JSON 接口 (fetch_url, http_get_json)",
        "file_content": "获取文件内容：读取文本文件 / 列出目录 (read_file, list_dir)",
    }
    return [
        {"builtin_key": key, "description": catalog.get(key, key)}
        for key in BUILTIN_PLUGINS
    ]


# --------------------------------------------------------------------------- #
# Flow config
# --------------------------------------------------------------------------- #


@router.get("/agent/flows/{app_key}", response_model=Optional[FlowConfigResponse])
async def get_flow(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = repository.get_flow_config(db, app_key)
    return _flow_to_response(config) if config else None


@router.put("/agent/flows/{app_key}", response_model=FlowConfigResponse)
async def upsert_flow(
    app_key: str,
    data: FlowConfigUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (data.mode or "single") not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"mode must be one of {sorted(VALID_MODES)}")
    fields = {
        "name": (data.name or "Agent").strip(),
        "instructions": data.instructions,
        "mode": data.mode or "single",
        "model": (data.model or None),
        "max_turns": max(1, int(data.max_turns or 10)),
        "sub_agents": json.dumps([s.model_dump() for s in data.sub_agents], ensure_ascii=False),
        "enabled": bool(data.enabled),
    }
    config = repository.upsert_flow_config(db, app_key, fields)
    agent_service.invalidate(app_key)
    return _flow_to_response(config)


@router.delete("/agent/flows/{app_key}")
async def delete_flow(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = repository.delete_flow_config(db, app_key)
    agent_service.invalidate(app_key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Flow config not found")
    return {"message": "Deleted"}


@router.post("/agent/flows/{app_key}/refresh")
async def refresh_flow(
    app_key: str,
    current_user: User = Depends(get_current_user),
):
    agent_service.invalidate(app_key)
    return {"message": "Agent instance cache invalidated; will rebuild on next request"}


# --------------------------------------------------------------------------- #
# Plugins
# --------------------------------------------------------------------------- #


@router.get("/agent/flows/{app_key}/plugins", response_model=List[PluginResponse])
async def list_plugins(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [_plugin_to_response(p) for p in repository.list_plugins(db, app_key)]


@router.post("/agent/flows/{app_key}/plugins", response_model=PluginResponse)
async def create_plugin(
    app_key: str,
    data: PluginUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (data.plugin_type or "custom") not in VALID_PLUGIN_TYPES:
        raise HTTPException(status_code=400, detail="plugin_type must be 'builtin' or 'custom'")
    if not (data.plugin_name or "").strip():
        raise HTTPException(status_code=400, detail="plugin_name cannot be empty")
    if data.plugin_type == "builtin" and (data.builtin_key or "") not in BUILTIN_PLUGINS:
        raise HTTPException(status_code=400, detail="Unknown builtin_key")
    if data.plugin_type == "custom" and not (data.script_content or "").strip():
        raise HTTPException(status_code=400, detail="Custom plugin requires script_content")

    config = repository.get_flow_config(db, app_key)
    if not config:
        # Auto-create a default flow config so plugins can be attached immediately.
        config = repository.upsert_flow_config(
            db, app_key, {"name": "Agent", "mode": "single", "enabled": True}
        )
    plugin = repository.create_plugin(
        db,
        {
            "flow_config_id": config.id,
            "app_key": app_key,
            "plugin_name": data.plugin_name.strip(),
            "description": data.description,
            "plugin_type": data.plugin_type,
            "builtin_key": (data.builtin_key or None),
            "script_content": data.script_content,
            "config_json": _normalize_config_json(data.config_json),
            "enabled": bool(data.enabled),
            "sort_order": int(data.sort_order or 0),
        },
    )
    agent_service.invalidate(app_key)
    return _plugin_to_response(plugin)


@router.put("/agent/plugins/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: int,
    data: PluginUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = repository.get_plugin(db, plugin_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Plugin not found")
    if (data.plugin_type or "custom") not in VALID_PLUGIN_TYPES:
        raise HTTPException(status_code=400, detail="plugin_type must be 'builtin' or 'custom'")
    plugin = repository.update_plugin(
        db,
        plugin_id,
        {
            "plugin_name": (data.plugin_name or existing.plugin_name).strip(),
            "description": data.description,
            "plugin_type": data.plugin_type,
            "builtin_key": (data.builtin_key or None),
            "script_content": data.script_content,
            "config_json": _normalize_config_json(data.config_json),
            "enabled": bool(data.enabled),
            "sort_order": int(data.sort_order or 0),
        },
    )
    agent_service.invalidate(existing.app_key)
    return _plugin_to_response(plugin)


@router.delete("/agent/plugins/{plugin_id}")
async def delete_plugin(
    plugin_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = repository.get_plugin(db, plugin_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Plugin not found")
    app_key = existing.app_key
    repository.delete_plugin(db, plugin_id)
    agent_service.invalidate(app_key)
    return {"message": "Deleted"}


@router.post("/agent/plugins/debug")
async def debug_plugin(
    data: PluginDebugRequest,
    current_user: User = Depends(get_current_user),
):
    if (data.plugin_type or "custom") == "builtin" and (data.builtin_key or "") not in BUILTIN_PLUGINS:
        raise HTTPException(status_code=400, detail="Unknown builtin_key")
    if (data.plugin_type or "custom") == "custom" and not (data.script_content or "").strip():
        raise HTTPException(status_code=400, detail="Custom plugin requires script_content")
    try:
        result = await agent_service.debug_plugin_run(
            plugin_id=data.plugin_id or 0,
            app_key=data.app_key,
            plugin_name=data.plugin_name or "debug_plugin",
            plugin_type=data.plugin_type or "custom",
            builtin_key=data.builtin_key,
            script_content=data.script_content,
            config_json=_normalize_config_json(data.config_json),
            tool_name=data.tool_name,
            tool_args=data.tool_args,
        )
    except Exception as exc:  # noqa: BLE001 - return the error to the editor UI
        raise HTTPException(status_code=400, detail=f"Debug failed: {_describe_exception(exc)}")
    return result
