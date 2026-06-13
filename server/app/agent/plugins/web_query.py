"""Builtin MCP plugin: query website.

Runs as an MCP stdio server (FastMCP). Exposes tools to fetch a web page and
return readable text, or to fetch JSON from an HTTP endpoint.

Run standalone:  python web_query.py
"""

import re

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("web_query")

_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")
_BLANK_RE = re.compile(r"\n\s*\n+")

_TIMEOUT = 20.0
_DEFAULT_HEADERS = {"User-Agent": "agent-marketing-bot/1.0"}


def _html_to_text(html: str) -> str:
    html = _TAG_RE.sub(" ", html)
    text = _HTML_TAG_RE.sub(" ", html)
    text = _WS_RE.sub(" ", text)
    text = _BLANK_RE.sub("\n\n", text)
    return text.strip()


@mcp.tool()
def fetch_url(url: str, max_chars: int = 4000) -> str:
    """Fetch a web page and return its readable text content.

    Args:
        url: Absolute http(s) URL to fetch.
        max_chars: Maximum characters of text to return (default 4000).
    """
    if not url.lower().startswith(("http://", "https://")):
        return "Error: url must start with http:// or https://"
    try:
        with httpx.Client(timeout=_TIMEOUT, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            body = resp.text
    except Exception as exc:  # noqa: BLE001 - surface a readable error to the model
        return f"Error fetching {url}: {exc}"

    text = body if "json" in content_type or "text/plain" in content_type else _html_to_text(body)
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + "\n...[truncated]"
    return text


@mcp.tool()
def http_get_json(url: str) -> str:
    """Fetch a JSON HTTP endpoint and return the raw JSON text.

    Args:
        url: Absolute http(s) URL returning JSON.
    """
    if not url.lower().startswith(("http://", "https://")):
        return "Error: url must start with http:// or https://"
    try:
        with httpx.Client(timeout=_TIMEOUT, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching {url}: {exc}"


if __name__ == "__main__":
    mcp.run()
