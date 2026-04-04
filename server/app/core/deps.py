from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import decode_access_token
from ..models.user import User, UserRole, Role, RoleType

security = HTTPBearer()


def get_role_type(db: Session, role_code: str | None) -> str:
    role_value = (role_code or "").strip().upper()
    if not role_value:
        return RoleType.USER.value

    role = db.query(Role).filter(Role.code == role_code).first()
    if role and role.role_type:
        return str(role.role_type).upper()

    if role_value == UserRole.ADMIN.value:
        return RoleType.ADMIN.value
    return RoleType.USER.value


def get_role_name(db: Session, role_code: str | None) -> str:
    if not role_code:
        return UserRole.USER.value
    role = db.query(Role).filter(Role.code == role_code).first()
    if role and role.name:
        return role.name
    return role_code

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Convert string user_id to integer
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if get_role_type(db, current_user.role) != RoleType.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
