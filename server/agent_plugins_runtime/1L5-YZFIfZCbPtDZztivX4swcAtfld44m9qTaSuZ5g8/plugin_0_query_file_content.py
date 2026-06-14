import os
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("简易文件内容读取器")

@mcp.tool()
async def read_all_files_content(dir_path: str) -> List[Dict[str, str]]:
    """
    递归遍历指定目录下的所有文件，读取每个文件的内容（文本模式），
    返回 [{"source": "文件相对路径", "content": "文件内容"}]。
    """
    target = Path(dir_path).expanduser().resolve()
    if not target.is_dir():
        return [{"source": "error", "content": f"路径 '{dir_path}' 不存在或不是目录"}]
    
    results = []
    for file_path in target.rglob('*'):   # 递归所有文件
        if not file_path.is_file():
            continue
        
        # 获取相对于目标目录的路径作为 source
        rel_path = str(file_path.relative_to(target))
        
        # 尝试读取文本内容（UTF-8，忽略无法解码的字符）
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            content = f"[读取失败: {str(e)}]"
        
        results.append({
            "source": rel_path,
            "content": content
        })
    
    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")