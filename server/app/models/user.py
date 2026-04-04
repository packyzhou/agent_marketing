from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime, Date, Boolean
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class RoleType(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class Role(Base):
    __tablename__ = "tb_role"

    code = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role_type = Column(String(20), nullable=False, default=RoleType.USER.value)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class User(Base):
    __tablename__ = "tb_user"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True, index=True)
    real_name = Column(String(50), nullable=True)
    referral_id = Column(BigInteger, nullable=True)
    group_id = Column(BigInteger, nullable=True)
    role = Column(String(50), nullable=False, default=UserRole.USER.value)
    created_at = Column(DateTime, server_default=func.now())

class Group(Base):
    __tablename__ = "tb_group"

    id = Column(BigInteger, primary_key=True, index=True)
    group_name = Column(String(100), nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class GroupMemberAppBinding(Base):
    __tablename__ = "tb_group_member_app_binding"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    owner_user_id = Column(BigInteger, nullable=False, index=True)
    member_id = Column(BigInteger, nullable=False, index=True)
    app_key = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
