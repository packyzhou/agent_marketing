from sqlalchemy import Column, String, BigInteger, Integer, Date, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class TokenSummary(Base):
    __tablename__ = "tb_token_summary"

    app_key = Column(String(64), primary_key=True, index=True)
    total_tokens = Column(BigInteger, default=0)
    last_month_tokens = Column(BigInteger, default=0)
    current_month_tokens = Column(BigInteger, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class TokenDaily(Base):
    __tablename__ = "tb_token_daily"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    app_key = Column(String(64), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    token_count = Column(BigInteger, default=0)
    request_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class TokenConversation(Base):
    __tablename__ = "tb_token_conversation"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    app_key = Column(String(64), nullable=False, index=True)
    round_number = Column(Integer, nullable=False, index=True)
    provider_name = Column(String(128))
    model_name = Column(String(128))
    prompt_tokens = Column(BigInteger, default=0)
    completion_tokens = Column(BigInteger, default=0)
    total_tokens = Column(BigInteger, default=0)
    created_at = Column(DateTime, server_default=func.now(), index=True)
