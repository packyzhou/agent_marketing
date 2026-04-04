from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.deps import get_current_user, get_role_name, get_role_type
from ...core.security import get_password_hash
from ...models.user import User, Group
from .schemas import UserProfileUpdate, UserResponse

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        phone=current_user.phone,
        real_name=current_user.real_name,
        role=str(current_user.role),
        role_name=get_role_name(db, current_user.role),
        role_type=get_role_type(db, current_user.role),
        group_id=current_user.group_id,
        created_at=current_user.created_at,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.username == profile_data.username, User.id != current_user.id)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_phone = (
        db.query(User)
        .filter(User.phone == profile_data.phone, User.id != current_user.id)
        .first()
    )
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    current_user.username = profile_data.username
    current_user.phone = profile_data.phone
    current_user.real_name = profile_data.real_name
    if profile_data.password:
        current_user.password_hash = get_password_hash(profile_data.password)

    db.commit()
    db.refresh(current_user)

    owned_group = db.query(Group).filter(Group.owner_id == current_user.id).first()
    if owned_group:
        owned_group.group_name = f"{current_user.username}的团队"
        db.commit()
        db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        phone=current_user.phone,
        real_name=current_user.real_name,
        role=str(current_user.role),
        role_name=get_role_name(db, current_user.role),
        role_type=get_role_type(db, current_user.role),
        group_id=current_user.group_id,
        created_at=current_user.created_at,
    )
