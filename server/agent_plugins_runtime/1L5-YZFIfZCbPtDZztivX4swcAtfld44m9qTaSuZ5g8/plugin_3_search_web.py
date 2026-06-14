"""
网页搜索 MCP 插件（爬虫版，无需 API Key）

功能:
    - 双引擎: DuckDuckGo(默认, 耐爬) / Google(易被风控)
    - 抓取每条结果的网页正文(trafilatura 提取), 内容更详细
    - 检索时带中文语言参数(优先中文结果, 但不强制过滤)
    - 输出 [{title, content}], 数量由 num_results 决定(上限 30)
    - 失败兜底: 正文抓取失败时回退到搜索摘要, content 永不为空

依赖:
    pip install httpx selectolax trafilatura mcp

运行(调试):
    python web_search_mcp.py
"""

import sys
import asyncio
import random
import urllib.parse
from typing import List, Dict

import httpx
import trafilatura
from selectolax.parser import HTMLParser
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("网页搜索爬虫")

# ---------------- 配置 ----------------
MAX_RESULTS = 30          # 整体返回上限
FETCH_CONCURRENCY = 5     # 并发抓正文上限, 太高易被封

# 轮换 User-Agent, 降低被识别为爬虫的概率
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]


# ---------------- 工具函数 ----------------
def _headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    }


def _clean_link(href: str) -> str:
    """还原跳转链接里的真实 URL(DuckDuckGo 的 uddg、Google 的 /url?q=)。"""
    if not href:
        return ""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    qs = urllib.parse.parse_qs(parsed.query)
    if "uddg" in qs:                          # DuckDuckGo 跳转
        return qs["uddg"][0]
    if "/url" in parsed.path and "q" in qs:   # Google 跳转
        return qs["q"][0]
    return href


async def _fetch(url: str) -> str:
    """抓搜索结果页, 带随机延时模拟人类停顿。"""
    await asyncio.sleep(random.uniform(0.5, 1.5))
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.text


async def _fetch_article(url: str, sem: asyncio.Semaphore, max_chars: int) -> str:
    """抓单个网页并提取正文, 失败返回空串(让上层回退到摘要)。"""
    if not url:
        return ""
    async with sem:
        try:
            await asyncio.sleep(random.uniform(0.2, 0.6))
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=_headers())
                resp.raise_for_status()
            # trafilatura.extract 是 CPU 密集型同步函数, 放线程里跑避免阻塞事件循环
            text = await asyncio.to_thread(
                trafilatura.extract, resp.text,
                include_comments=False, include_tables=False,
            )
            return text.strip()[:max_chars] if text else ""
        except Exception:
            return ""


# ---------------- 结果页解析 ----------------
def _parse_google(html: str, limit: int) -> List[Dict[str, str]]:
    """解析 Google 结果页。注意: class 名会变, 失效时需重新抓页面调整选择器。"""
    tree = HTMLParser(html)
    out: List[Dict[str, str]] = []
    for node in tree.css("div.g, div.tF2Cxc, div.MjjYud"):
        title_node = node.css_first("h3")
        link_node = node.css_first("a")
        snippet_node = node.css_first("div.VwiC3b, div.IsZvec, span.aCOpRe")
        if not title_node or not link_node:
            continue
        out.append({
            "title": title_node.text(strip=True),
            "link": _clean_link(link_node.attributes.get("href", "")),
            "content": snippet_node.text(strip=True) if snippet_node else "",
        })
        if len(out) >= limit:
            break
    return out


def _parse_duckduckgo(html: str, limit: int) -> List[Dict[str, str]]:
    """解析 DuckDuckGo HTML 版结果页, 结构比 Google 稳定。"""
    tree = HTMLParser(html)
    out: List[Dict[str, str]] = []
    for node in tree.css("div.result, div.web-result"):
        title_node = node.css_first("a.result__a")
        snippet_node = node.css_first("a.result__snippet, div.result__snippet")
        if not title_node:
            continue
        out.append({
            "title": title_node.text(strip=True),
            "link": _clean_link(title_node.attributes.get("href", "")),
            "content": snippet_node.text(strip=True) if snippet_node else "",
        })
        if len(out) >= limit:
            break
    return out


# ---------------- MCP 工具 ----------------
@mcp.tool()
async def search_web(
    keyword: str,
    num_results: int = 10,
    engine: str = "duckduckgo",
    full_content: bool = True,
    max_chars: int = 3000,
) -> List[Dict[str, str]]:
    """
    通过爬取搜索引擎网页结果获取内容(无需 API Key)。检索时带中文语言参数, 优先返回中文。

    参数:
        keyword:      搜索关键字, 例如 "英伟达 财报 2026"
        num_results:  返回数量, 1-30
        engine:       "duckduckgo"(默认, 耐爬) 或 "google"(易被风控)
        full_content: True 抓取原网页正文(详细) / False 只返回摘要(快)
        max_chars:    每条正文最大字符数, 防止单条过长

    返回:
        [{"title": 标题, "content": 正文或摘要}, ...]
        出错时返回 [{"title": "错误标记", "content": 原因}]
    """
    if not keyword or not keyword.strip():
        return [{"title": "错误", "content": "关键字不能为空"}]

    limit = max(1, min(num_results, MAX_RESULTS))
    q = urllib.parse.quote_plus(keyword)

    # 1) 抓搜索结果页(带中文语言参数, 优先中文; 不强制过滤)
    try:
        if engine == "google":
            html = await _fetch(
                f"https://www.google.com/search?q={q}&num={limit + 5}&hl=zh-CN&lr=lang_zh-CN"
            )
            if "unusual traffic" in html or "/sorry/" in html:
                return [{"title": "被风控", "content": "Google 触发验证码, 建议改用 duckduckgo 引擎"}]
            results = _parse_google(html, limit)
        else:
            html = await _fetch(f"https://html.duckduckgo.com/html/?q={q}&kl=cn-zh")
            results = _parse_duckduckgo(html, limit)
    except httpx.HTTPStatusError as e:
        return [{"title": "请求失败", "content": f"HTTP {e.response.status_code}"}]
    except Exception as e:
        return [{"title": "请求异常", "content": str(e)}]

    if not results:
        return [{"title": "无结果", "content": "未解析到结果(页面结构可能已变或被风控)"}]

    # 2) 抓正文: 并发请求每条结果链接, 失败则保留原摘要
    if full_content:
        sem = asyncio.Semaphore(FETCH_CONCURRENCY)
        articles = await asyncio.gather(*[
            _fetch_article(r["link"], sem, max_chars) for r in results
        ])
        for r, body in zip(results, articles):
            if body:
                r["content"] = body

    # 3) 只返回 title + content
    return [{"title": r["title"], "content": r["content"]} for r in results]


if __name__ == "__main__":
    # 用 except* 拆开 TaskGroup 包装, 把真正的异常打到 stderr(不能用 stdout, 会破坏协议)
    try:
        mcp.run(transport="stdio")
    except* Exception as eg:
        for i, exc in enumerate(eg.exceptions, 1):
            print(f"[子异常 {i}] {type(exc).__name__}: {exc}", file=sys.stderr)
        raise