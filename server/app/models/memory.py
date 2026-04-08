from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class MemoryMeta(Base):
    __tablename__ = "tb_memory_meta"

    app_key = Column(String(64), primary_key=True, index=True)
    last_processed_round = Column(Integer, default=0)
    kv_file_path = Column(String(255), nullable=True)
    digest_file_path = Column(String(255), nullable=True)
    total_duration_seconds = Column(BigInteger, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
