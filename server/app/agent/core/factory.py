"""Build OpenAI Agents SDK Agent instances from a ResolvedFlow.

The agent's model client is built from agent_config.json -> system_llm
(provider / api_key / base_url / model), unless a flow/sub-agent overrides
the model name. MCP plugin servers are opened on the caller-supplied
AsyncExitStack so their subprocess lifetime spans the whole run.
"""

import json
import threading
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import ResolvedFlow
from .plugin_runtime import PluginSpec

_AGENT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "agent_config.json"

_MCP_TOOL_CACHE_SECONDS = 300
_client_cache: Dict[tuple, Any] = {}
_client_lock = threading.Lock()
_tracing_disabled = False


def _load_system_llm_config() -> dict:
    try:
        return json.loads(_AGENT_CONFIG_PATH.read_text(encoding="utf-8")).get("system_llm", {})
    except Exception:
        return {}


def _ensure_tracing_disabled() -> None:
    global _tracing_disabled
    if _tracing_disabled:
        return
    try:
        from agents import set_tracing_disabled

        set_tracing_disabled(True)
    except Exception:
        pass
    _tracing_disabled = True


def _get_openai_client(api_key: str, base_url: str):
    from openai import AsyncOpenAI

    key = (api_key or "", base_url or "")
    client = _client_cache.get(key)
    if client is not None:
        return client
    with _client_lock:
        client = _client_cache.get(key)
        if client is None:
            client = AsyncOpenAI(api_key=api_key or "not-needed", base_url=base_url or None)
            _client_cache[key] = client
        return client


def _build_model(model_name: Optional[str]):
    cfg = _load_system_llm_config()
    resolved_model = (model_name or "").strip() or cfg.get("model") or "gpt-4o-mini"
    client = _get_openai_client(cfg.get("api_key", ""), cfg.get("base_url", ""))
    try:
        from agents import OpenAIChatCompletionsModel
    except ImportError:
        from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
    return OpenAIChatCompletionsModel(model=resolved_model, openai_client=client)


_logging_server_cls = None


def _get_logging_server_cls():
    """Subclass of MCPServerStdio that logs every tool call with args + duration.

    The Agents SDK invokes server.call_tool(tool_name, arguments) for each tool
    the agent decides to run, so this captures every real plugin invocation.
    Built lazily because the SDK import is optional.
    """
    global _logging_server_cls
    if _logging_server_cls is not None:
        return _logging_server_cls

    import time

    from agents.mcp import MCPServerStdio

    class LoggingMCPServerStdio(MCPServerStdio):
        async def call_tool(self, *args, **kwargs):
            tool_name = kwargs.get("tool_name")
            if tool_name is None and args:
                tool_name = args[0]
            arguments = kwargs.get("arguments")
            if arguments is None and len(args) > 1:
                arguments = args[1]
            try:
                args_text = json.dumps(arguments or {}, ensure_ascii=False)
            except (TypeError, ValueError):
                args_text = str(arguments)

            started = time.perf_counter()
            status = "ok"
            try:
                return await super().call_tool(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - log then re-raise
                status = f"error:{type(exc).__name__}"
                raise
            finally:
                elapsed = time.perf_counter() - started
                print(f"[插件调用] [{self.name} - {tool_name}:{args_text}] [{elapsed:.3f}s] [{status}]")

    _logging_server_cls = LoggingMCPServerStdio
    return _logging_server_cls


async def _open_mcp_server(spec: PluginSpec, exit_stack: AsyncExitStack):
    server_cls = _get_logging_server_cls()

    server = server_cls(
        name=spec.name,
        params=spec.to_mcp_params(),
        cache_tools_list=True,
        client_session_timeout_seconds=30,
    )
    await exit_stack.enter_async_context(server)
    return server


async def _open_servers_for(
    plugin_ids: List[int],
    plugins: Dict[int, PluginSpec],
    exit_stack: AsyncExitStack,
    opened: Dict[int, Any],
) -> List[Any]:
    servers = []
    for pid in plugin_ids:
        spec = plugins.get(pid)
        if not spec:
            continue
        if pid not in opened:
            opened[pid] = await _open_mcp_server(spec, exit_stack)
        servers.append(opened[pid])
    return servers


async def build_agent(
    flow: ResolvedFlow,
    exit_stack: AsyncExitStack,
    extra_instructions: Optional[str] = None,
):
    """Build and return the root Agent for a resolved flow.

    All MCP plugin subprocesses are opened on `exit_stack`; the caller must keep
    the stack open for the duration of the run.
    """
    from agents import Agent

    _ensure_tracing_disabled()

    base_instructions = flow.instructions or "You are a helpful assistant."
    if extra_instructions:
        root_instructions = f"{extra_instructions}\n\n{base_instructions}"
    else:
        root_instructions = base_instructions

    opened: Dict[int, Any] = {}
    mode = (flow.mode or "single").lower()
    all_plugin_ids = list(flow.plugins.keys())

    if mode not in {"tool", "handoff"} or not flow.sub_agents:
        servers = await _open_servers_for(all_plugin_ids, flow.plugins, exit_stack, opened)
        return Agent(
            name=flow.name or "Agent",
            instructions=root_instructions,
            model=_build_model(flow.model),
            mcp_servers=servers,
        )

    # tool / handoff modes: build sub-agents first
    assigned_ids: set = set()
    sub_agent_objs = []
    for idx, sub in enumerate(flow.sub_agents):
        sub_servers = await _open_servers_for(sub.plugin_ids, flow.plugins, exit_stack, opened)
        assigned_ids.update(sub.plugin_ids)
        sub_agent_objs.append(
            (
                sub,
                Agent(
                    name=sub.name or f"SubAgent{idx + 1}",
                    instructions=sub.instructions or "You are a specialized assistant.",
                    model=_build_model(sub.model or flow.model),
                    mcp_servers=sub_servers,
                ),
            )
        )

    # Any plugins not assigned to a sub-agent attach to the orchestrator.
    orchestrator_ids = [pid for pid in all_plugin_ids if pid not in assigned_ids]
    orchestrator_servers = await _open_servers_for(
        orchestrator_ids, flow.plugins, exit_stack, opened
    )

    if mode == "tool":
        tools = [
            obj.as_tool(
                tool_name=(sub.tool_name or _slug(sub.name) or f"sub_agent_{i + 1}"),
                tool_description=(sub.tool_description or sub.instructions or sub.name or "delegate"),
            )
            for i, (sub, obj) in enumerate(sub_agent_objs)
        ]
        return Agent(
            name=flow.name or "Orchestrator",
            instructions=root_instructions,
            model=_build_model(flow.model),
            mcp_servers=orchestrator_servers,
            tools=tools,
        )

    # handoff mode
    return Agent(
        name=flow.name or "Orchestrator",
        instructions=root_instructions,
        model=_build_model(flow.model),
        mcp_servers=orchestrator_servers,
        handoffs=[obj for _, obj in sub_agent_objs],
    )


def _slug(value: Optional[str]) -> str:
    if not value:
        return ""
    return "".join(c if c.isalnum() or c == "_" else "_" for c in value).strip("_").lower()
