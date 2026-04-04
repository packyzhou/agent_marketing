from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.deps import get_current_admin_user, get_role_name, get_role_type
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
    role_name: str
    role_type: str
    referral_id: Optional[str]
    group_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class UserPageResponse(BaseModel):
    total: int
    items: List[UserResponse]


class UserDetailResponse(UserResponse):
    tenant_count: int
    referral_count: int


def _to_user_response(db: Session, user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=getattr(user, "email", None),
        phone=user.phone,
        real_name=user.real_name,
        role=str(user.role),
        role_name=get_role_name(db, user.role),
        role_type=get_role_type(db, user.role),
        referral_id=str(user.referral_id) if user.referral_id is not None else None,
        group_id=str(user.group_id) if user.group_id is not None else None,
        created_at=user.created_at.isoformat()
    )


@router.get("/users", response_model=UserPageResponse)
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
        query = query.filter(User.role == str(role).upper())

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return UserPageResponse(total=total, items=[_to_user_response(db, user) for user in users])

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
        **_to_user_response(db, user).model_dump(),
        tenant_count=tenant_count,
        referral_count=referral_count
    )
