from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


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
    referral_id: Optional[int] = None

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
        password = value.strip() if value else ""
        if not password:
            raise ValueError("password is required")
        if not password.isdigit() or len(password) <= 6:
            raise ValueError("password must be numeric and longer than 6 digits")
        return password

    @field_validator("referral_id", mode="before")
    @classmethod
    def normalize_referral_id(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.isdigit():
                return int(text)
            raise ValueError("referral_id must be a positive integer")
        if isinstance(value, int):
            if value <= 0:
                raise ValueError("referral_id must be a positive integer")
            return value
        raise ValueError("referral_id must be a positive integer")


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    phone: Optional[str]
    real_name: Optional[str]
    role: str
    group_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
