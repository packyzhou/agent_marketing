"""Agent module.

A self-contained OpenAI Agents SDK integration that runs alongside the original
AsyncOpenAI chat proxy. Activated per request via the `use_agent` flag.

Layout:
    core/repository.py      DB access for flow config + plugin refs
    core/plugin_runtime.py  Materialize MCP plugin scripts + debug-run them
    core/factory.py         Build Agent instances (single / tool / handoff)
    core/runner.py          Run an agent, yield OpenAI-compatible chunks
    core/cache.py           Per-appKey resolved-spec cache + invalidation
    service.py              Public facade used by the chat proxy + admin API
    plugins/                Bundled builtin MCP stdio plugin scripts
"""
