import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("文件列表服务器")

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    将 YYYY-MM-DD 字符串转为 datetime 对象（当天 00:00:00）。
    如果 date_str 为空或空字符串，返回 None。
    如果格式错误，也返回 None。
    """
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

@mcp.tool()
async def list_directory(
    dir_path: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    根据用户输入的路径，以 JSON 字符串列出该目录下的所有文件名和最新更新时间。
    可选地根据文件的修改时间筛选日期范围。如果 start_date 或 end_date 为空/空字符串，则不限制对应边界。

    参数:
        dir_path: 要查询的目录路径，例如 "./out" 或 "/home/user/documents"
        start_date: 起始日期 (YYYY-MM-DD)，为空则不设下限
        end_date: 结束日期 (YYYY-MM-DD)，为空则不设上限

    返回:
        JSON 字符串，形如 [{"filename": "...", "updateDate": "..."}]。
    """
    target_dir = Path(dir_path).expanduser().resolve()
    if not target_dir.is_dir():
        return json.dumps([{"error": f"提供的路径 '{dir_path}' 不存在或不是一个目录。"}], ensure_ascii=False)

    start = parse_date(start_date)
    end = parse_date(end_date)
    if end is not None:
        end = end.replace(hour=23, minute=59, second=59)

    result = []
    try:
        for item in target_dir.iterdir():
            if not item.is_file():
                continue
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            # 日期筛选：如果 start 存在且 mtime < start 则跳过；如果 end 存在且 mtime > end 则跳过
            if start is not None and mtime < start:
                continue
            if end is not None and mtime > end:
                continue
            mod_time_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            result.append({"filename": item.name, "updateDate": mod_time_str})
    except Exception as e:
        return json.dumps([{"error": f"读取目录时发生错误: {str(e)}"}], ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")