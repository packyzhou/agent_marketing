from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class SystemPrompt(Base):
    __tablename__ = "tb_system_prompt"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_type = Column(String(100), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
