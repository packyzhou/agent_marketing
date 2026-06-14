import asyncio
import random
import urllib.parse
from typing import List, Dict

import httpx
from selectolax.parser import HTMLParser
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("网页搜索爬虫")

MAX_RESULTS = 30

# 轮换 User-Agent，降低被识别为爬虫的概率
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]


def _headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    }


async def _fetch(url: str) -> str:
    """带随机延时和重试的请求，尽量降低被封概率。"""
    await asyncio.sleep(random.uniform(0.5, 1.5))  # 模拟人类停顿
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.text


def _parse_google(html: str, limit: int) -> List[Dict[str, str]]:
    """解析 Google 结果页。注意：class 名会变，失效时需重新抓页面调整选择器。"""
    tree = HTMLParser(html)
    results: List[Dict[str, str]] = []

    # Google 每条结果通常包在 div.g 内；这里多给几个备选选择器
    for node in tree.css("div.g, div.tF2Cxc, div.MjjYud"):
        title_node = node.css_first("h3")
        # 摘要常见容器
        snippet_node = node.css_first("div.VwiC3b, div.IsZvec, span.aCOpRe")
        if not title_node:
            continue
        title = title_node.text(strip=True)
        content = snippet_node.text(strip=True) if snippet_node else ""
        if title:
            results.append({"title": title, "content": content})
        if len(results) >= limit:
            break
    return results


def _parse_duckduckgo(html: str, limit: int) -> List[Dict[str, str]]:
    """解析 DuckDuckGo HTML 版结果页，结构比 Google 稳定得多。"""
    tree = HTMLParser(html)
    results: List[Dict[str, str]] = []
    for node in tree.css("div.result, div.web-result"):
        title_node = node.css_first("a.result__a")
        snippet_node = node.css_first("a.result__snippet, div.result__snippet")
        if not title_node:
            continue
        title = title_node.text(strip=True)
        content = snippet_node.text(strip=True) if snippet_node else ""
        if title:
            results.append({"title": title, "content": content})
        if len(results) >= limit:
            break
    return results


@mcp.tool()
async def search_web(
    keyword: str,
    num_results: int = 10,
    engine: str = "duckduckgo",
) -> List[Dict[str, str]]:
    """
    通过爬取搜索引擎网页结果获取内容（无需 API Key）。

    参数:
        keyword:     搜索关键字
        num_results: 返回数量，1-30
        engine:      "google" 或 "duckduckgo"（默认，更耐爬）

    返回:
        [{"title": 标题, "content": 摘要}, ...]
        出错时返回 [{"title": "错误", "content": 原因}]
    """
    if not keyword or not keyword.strip():
        return [{"title": "错误", "content": "关键字不能为空"}]

    limit = max(1, min(num_results, MAX_RESULTS))
    q = urllib.parse.quote_plus(keyword)

    try:
        if engine == "google":
            # num 多取一些以防被过滤掉部分
            url = f"https://www.google.com/search?q={q}&num={limit + 5}&hl=zh-CN"
            html = await _fetch(url)
            if "Our systems have detected unusual traffic" in html or "/sorry/" in html:
                return [{"title": "被风控", "content": "Google 触发验证码，建议改用 duckduckgo 引擎或加代理"}]
            results = _parse_google(html, limit)
        else:
            url = f"https://html.duckduckgo.com/html/?q={q}"
            html = await _fetch(url)
            results = _parse_duckduckgo(html, limit)

    except httpx.HTTPStatusError as e:
        return [{"title": "请求失败", "content": f"HTTP {e.response.status_code}"}]
    except Exception as e:
        return [{"title": "请求异常", "content": str(e)}]

    if not results:
        return [{"title": "无结果", "content": "未解析到结果（可能页面结构已变或被风控）"}]
    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")