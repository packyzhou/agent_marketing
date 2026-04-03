from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    referral_id: Optional[int] = None

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
