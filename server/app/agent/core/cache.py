"""Per-appKey resolved-flow cache.

We cache the *resolved configuration* (flow fields + materialized plugin specs),
not live MCP subprocesses — those are short-lived and opened per request inside
the runner. Invalidating an appKey forces the next request to re-read the DB and
re-materialize plugin scripts, which is how "update the Agent instance for this
appKey" is realized after an orchestrator/plugin edit.
"""

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .plugin_runtime import PluginSpec


@dataclass
class ResolvedSubAgent:
    name: str
    instructions: str
    model: Optional[str]
    plugin_ids: List[int] = field(default_factory=list)
    tool_name: Optional[str] = None
    tool_description: Optional[str] = None


@dataclass
class ResolvedFlow:
    app_key: str
    name: str
    instructions: str
    mode: str
    model: Optional[str]
    max_turns: int
    enabled: bool
    sub_agents: List[ResolvedSubAgent] = field(default_factory=list)
    # plugin_id -> PluginSpec for every enabled plugin attached to this appKey
    plugins: Dict[int, PluginSpec] = field(default_factory=dict)


_CACHE: Dict[str, ResolvedFlow] = {}
_LOCK = threading.Lock()


def get(app_key: str) -> Optional[ResolvedFlow]:
    with _LOCK:
        return _CACHE.get(app_key)


def put(app_key: str, flow: ResolvedFlow) -> None:
    with _LOCK:
        _CACHE[app_key] = flow


def invalidate(app_key: str) -> None:
    with _LOCK:
        _CACHE.pop(app_key, None)


def clear() -> None:
    with _LOCK:
        _CACHE.clear()
