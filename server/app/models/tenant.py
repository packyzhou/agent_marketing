from sqlalchemy import Column, String, BigInteger, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class Tenant(Base):
    __tablename__ = "tb_tenant"

    app_key = Column(String(64), primary_key=True, index=True)
    app_secret = Column(String(128), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    group_binding_json = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
