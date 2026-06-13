from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class FileScanRecord(Base):
    """目录扫描结果记录。

    由 Agent 插件「扫描目录并保存」通过 /api/agent/file-records 接口写入：
    给定一个路径，列出其下文件/目录清单并持久化，便于后续查询与审计。
    """

    __tablename__ = "tb_file_scan_record"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    app_key = Column(String(64), nullable=False, index=True)
    scan_path = Column(String(1024), nullable=False)
    file_count = Column(Integer, nullable=False, default=0)
    files = Column(Text, nullable=True)  # JSON: [{"name","is_dir","size"}, ...]
    created_at = Column(DateTime, server_default=func.now())
