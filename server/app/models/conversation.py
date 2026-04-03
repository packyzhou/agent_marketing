from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class Conversation(Base):
    __tablename__ = "tb_conversation"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    app_key = Column(String(64), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
