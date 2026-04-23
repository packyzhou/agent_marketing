from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.deps import get_role_name, get_role_type
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.snowflake import generate_snowflake_id
from ...models.user import User, Group
from .schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()


def _ensure_owned_group(db: Session, owner_id: int, username: str):
    group = db.query(Group).filter(Group.owner_id == owner_id).first()
    if group:
        return group
    group = Group(
        # id=generate_snowflake_id(),
        group_name=f"{username}的团队",
        owner_id=owner_id,
    )
    db.add(group)
    db.flush()
    return group


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 检查手机号是否已存在
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=400, detail="Phone number already registered"
            )

    # 创建新用户
    new_user_id = generate_snowflake_id()
    user = User(
        id=new_user_id,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
        real_name=user_data.real_name,
        referral_id=None,
    )

    owned_group = _ensure_owned_group(db, new_user_id, user_data.username)
    referrer = None
    if user_data.referrer_phone:
        referrer = (
            db.query(User)
            .filter(User.phone == user_data.referrer_phone, User.id != new_user_id)
            .first()
        )
        if not referrer:
            raise HTTPException(status_code=400, detail="Referrer phone not found")
        referrer_group = _ensure_owned_group(db, referrer.id, referrer.username)
        if referrer.group_id != referrer_group.id:
            referrer.group_id = referrer_group.id
        user.referral_id = referrer.id
        user.group_id = referrer_group.id
    else:
        user.group_id = owned_group.id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": str(user.role),
        "role_name": get_role_name(db, user.role),
        "role_type": get_role_type(db, user.role),
        "username": user.username,
    }
