import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("文件列表内容读取器")

def parse_date_if_provided(date_str: Optional[str]) -> Optional[datetime]:
    """
    如果 date_str 有效（非空且非空字符串），返回对应日期的 00:00:00；
    否则返回 None（表示未提供，不限制）。
    """
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

@mcp.tool()
async def read_files_by_date_range(
    file_list: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    根据给定的文件列表，读取每个文件的内容，并根据修改时间筛选日期范围。
    若 start_date 或 end_date 为空/空字符串，则对应边界不限制。
    若两者都为空，则读取所有文件（不过滤日期）。

    参数:
        file_list: 文件路径列表，例如 ["/path/to/a.txt", "/path/to/b.yaml"]
        start_date: 起始日期 (YYYY-MM-DD)，为空则无下限
        end_date: 结束日期 (YYYY-MM-DD)，为空则无上限

    返回:
        [{"source": "原始文件路径", "content": "文件内容"}, ...]
    """
    start = parse_date_if_provided(start_date)
    end = parse_date_if_provided(end_date)
    # 如果 end 有效，设为当天 23:59:59
    if end is not None:
        end = end.replace(hour=23, minute=59, second=59)

    results = []
    for file_path_str in file_list:
        file_path = Path(file_path_str).expanduser().resolve()
        if not file_path.is_file():
            results.append({
                "source": file_path_str,
                "content": f"[错误: 文件不存在或不是普通文件]"
            })
            continue

        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        # 筛选条件：只有 start 非 None 且 mtime < start 时跳过
        if start is not None and mtime < start:
            continue
        # 只有 end 非 None 且 mtime > end 时跳过
        if end is not None and mtime > end:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            content = f"[读取失败: {str(e)}]"

        results.append({
            "source": file_path_str,
            "content": content
        })

    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")