import os
import asyncio
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建一个MCP服务器实例
mcp = FastMCP("文件列表服务器")

@mcp.tool()
async def list_directory(dir_path: str) -> list[dict]:
    """
    根据用户输入的路径，以JSON格式列出该目录下的所有文件名和最新更新时间。
    
    参数:
        dir_path: 要查询的目录路径，例如 "./out" 或 "/home/user/documents"
    
    返回:
        包含字典的列表，每个字典代表一个文件，包含"filename"和"updateDate"键。
    """
    target_dir = Path(dir_path).expanduser().resolve()
    result = []
    if not target_dir.is_dir():
        return [{"error": f"提供的路径 '{dir_path}' 不存在或不是一个目录。"}]
    try:
        for item in target_dir.iterdir():
            if item.is_file():
                stat = item.stat()
                # 将时间戳转换为可读格式
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                result.append({
                    "filename": item.name,
                    "updateDate": mod_time
                })
        return result
    except Exception as e:
        return [{"error": f"读取目录时发生错误: {str(e)}"}]

if __name__ == "__main__":
    # 运行 MCP 服务器，默认通过标准输入输出（stdio）传输
    mcp.run(transport="stdio")
