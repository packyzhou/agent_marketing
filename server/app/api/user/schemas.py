from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def normalize_password(value: str, *, required: bool) -> Optional[str]:
    password = value.strip() if value else ""
    if not password:
        if required:
            raise ValueError("password is required")
        return None
    if len(password) <= 6:
        raise ValueError("password length must be greater than 6 characters")
    return password


class UserBase(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value or not value.strip():
            raise ValueError("username is required")
        return value.strip()


class UserCreate(UserBase):
    password: str
    phone: str
    real_name: Optional[str] = None
    referrer_phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        phone = value.strip() if value else ""
        if not phone:
            raise ValueError("phone is required")
        return phone

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        return normalize_password(value, required=True)

    @field_validator("referrer_phone")
    @classmethod
    def normalize_referrer_phone(cls, value):
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    phone: Optional[str]
    real_name: Optional[str]
    role: str
    role_name: Optional[str] = None
    role_type: Optional[str] = None
    group_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: str
    phone: str
    real_name: Optional[str] = None
    password: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_profile_username(cls, value: str):
        if not value or not value.strip():
            raise ValueError("username is required")
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_profile_phone(cls, value: str):
        phone = value.strip() if value else ""
        if not phone:
            raise ValueError("phone is required")
        return phone

    @field_validator("password")
    @classmethod
    def validate_profile_password(cls, value):
        return normalize_password(value, required=False)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    role_name: str
    role_type: str
    username: str
