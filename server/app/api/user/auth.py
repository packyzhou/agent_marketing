from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.snowflake import generate_snowflake_id
from ...models.user import User, Group
from .schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()

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
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # 创建新用户
    new_user_id = generate_snowflake_id()
    user = User(
        id=new_user_id,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
        real_name=user_data.real_name,
        referral_id=None
    )

    # 如果有推荐人，且推荐人存在，则自动加入推荐人的分组
    if user_data.referral_id:
        referrer = db.query(User).filter(User.id == user_data.referral_id).first()
        if referrer:
            user.referral_id = user_data.referral_id
            if referrer.group_id:
                # 推荐人已有分组，加入该分组
                user.group_id = referrer.group_id
            else:
                # 推荐人没有分组，为推荐人创建分组
                group = Group(
                    group_name=f"{referrer.username}的团队",
                    owner_id=referrer.id
                )
                db.add(group)
                db.flush()
                referrer.group_id = group.id
                user.group_id = group.id

    if not user.group_id:
        # 没有有效推荐人，为自己创建分组
        group = Group(
            group_name=f"{user_data.username}的团队",
            owner_id=new_user_id
        )
        db.add(group)
        db.flush()
        user.group_id = group.id

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
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
    }
