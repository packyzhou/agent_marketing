from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class ProviderStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Provider(Base):
    __tablename__ = "tb_provider"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=False)
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())

class ProviderKey(Base):
    __tablename__ = "tb_provider_key"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False)
    provider_id = Column(BigInteger, nullable=False)
    api_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
