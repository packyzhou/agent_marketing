from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.user import User
from ...models.tenant import Tenant
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    phone: Optional[str]
    real_name: Optional[str]
    role: str
    referral_id: Optional[str]
    group_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    tenant_count: int
    referral_count: int

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users with pagination"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=getattr(user, "email", None),
            phone=user.phone,
            real_name=user.real_name,
            role=user.role,
            referral_id=str(user.referral_id) if user.referral_id is not None else None,
            group_id=str(user.group_id) if user.group_id is not None else None,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tenant_count = db.query(Tenant).filter(Tenant.user_id == user.id).count()
    referral_count = db.query(User).filter(User.referral_id == user.id).count()

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=getattr(user, "email", None),
        phone=user.phone,
        real_name=user.real_name,
        role=user.role,
        referral_id=str(user.referral_id) if user.referral_id is not None else None,
        group_id=str(user.group_id) if user.group_id is not None else None,
        created_at=user.created_at.isoformat(),
        tenant_count=tenant_count,
        referral_count=referral_count
    )
