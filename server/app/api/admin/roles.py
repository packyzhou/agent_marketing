from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.deps import get_current_admin_user, get_role_type
from ...core.utils import dt_to_local_str
from ...models.user import User, Role, RoleType
from pydantic import BaseModel, field_validator

router = APIRouter()


class RoleResponse(BaseModel):
    code: str
    name: str
    role_type: str
    description: Optional[str]
    is_system: bool
    user_count: int
    created_at: str


class RolePageResponse(BaseModel):
    total: int
    items: List[RoleResponse]


class RoleCreate(BaseModel):
    code: str
    name: str
    role_type: str
    description: Optional[str] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str):
        text = value.strip().upper()
        if not text:
            raise ValueError("code is required")
        return text

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        text = value.strip()
        if not text:
            raise ValueError("name is required")
        return text

    @field_validator("role_type")
    @classmethod
    def validate_role_type(cls, value: str):
        text = value.strip().upper()
        if text not in [RoleType.ADMIN.value, RoleType.USER.value]:
            raise ValueError("invalid role_type")
        return text


class RoleUpdate(BaseModel):
    name: str
    role_type: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        text = value.strip()
        if not text:
            raise ValueError("name is required")
        return text

    @field_validator("role_type")
    @classmethod
    def validate_role_type(cls, value: str):
        text = value.strip().upper()
        if text not in [RoleType.ADMIN.value, RoleType.USER.value]:
            raise ValueError("invalid role_type")
        return text


class AssignUserRoleRequest(BaseModel):
    role_code: str

    @field_validator("role_code")
    @classmethod
    def validate_role_code(cls, value: str):
        text = value.strip().upper()
        if not text:
            raise ValueError("role_code is required")
        return text


def _to_role_response(db: Session, role: Role) -> RoleResponse:
    user_count = db.query(User).filter(User.role == role.code).count()
    return RoleResponse(
        code=role.code,
        name=role.name,
        role_type=str(role.role_type).upper(),
        description=role.description,
        is_system=bool(role.is_system),
        user_count=user_count,
        created_at=dt_to_local_str(role.created_at),
    )


@router.get("/roles", response_model=RolePageResponse)
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Role)
    if keyword:
        text = keyword.strip()
        if text:
            query = query.filter(
                (Role.code.like(f"%{text}%")) | (Role.name.like(f"%{text}%"))
            )

    total = query.count()
    roles = query.order_by(Role.created_at.desc()).offset(skip).limit(limit).all()
    return RolePageResponse(total=total, items=[_to_role_response(db, role) for role in roles])


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Role).filter(Role.code == role_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role code already exists")

    role = Role(
        code=role_data.code,
        name=role_data.name,
        role_type=role_data.role_type,
        description=role_data.description,
        is_system=False,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return _to_role_response(db, role)


@router.put("/roles/{role_code}", response_model=RoleResponse)
async def update_role(
    role_code: str,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.code == role_code.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.name = role_data.name
    role.role_type = role_data.role_type
    role.description = role_data.description
    db.commit()
    db.refresh(role)
    return _to_role_response(db, role)


@router.delete("/roles/{role_code}")
async def delete_role(
    role_code: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.code == role_code.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="System role cannot be deleted")

    assigned_count = db.query(User).filter(User.role == role.code).count()
    if assigned_count > 0:
        raise HTTPException(status_code=400, detail="Role is assigned to users")

    db.delete(role)
    db.commit()
    return {"message": "Role deleted successfully"}


@router.put("/users/{user_id}/role")
async def assign_user_role(
    user_id: int,
    data: AssignUserRoleRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.code == data.role_code).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if user.id == current_user.id and get_role_type(db, data.role_code) != RoleType.ADMIN.value:
        raise HTTPException(status_code=400, detail="Current admin cannot demote self")

    user.role = role.code
    db.commit()
    return {"message": "Role assigned successfully"}
