from sqlalchemy import Column, String, BigInteger, Text, DateTime, Enum as SQLEnum
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
    code = Column(String(50), nullable=False, unique=True, index=True)
    base_url = Column(String(255), nullable=False)
    config_guide = Column(Text, nullable=True)
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())

class ProviderKey(Base):
    __tablename__ = "tb_provider_key"

    id = Column(BigInteger, primary_key=True, index=True)
    app_key = Column(String(64), nullable=False, index=True)
    provider_id = Column(BigInteger, nullable=False)
    api_key = Column(String(255), nullable=False)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
