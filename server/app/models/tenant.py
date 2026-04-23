from sqlalchemy import Column, String, BigInteger, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class TenantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Tenant(Base):
    __tablename__ = "tb_tenant"

    app_key = Column(String(64), primary_key=True, index=True)
    app_secret = Column(String(128), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    tenant_name = Column(String(100), nullable=True)
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    group_binding_json = Column(Text, nullable=True)
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
