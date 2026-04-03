from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import secrets
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.user import User
from ...models.tenant import Tenant, TenantStatus
from pydantic import BaseModel

router = APIRouter()

class TenantResponse(BaseModel):
    id: int
    app_key: str
    app_secret: str
    tenant_name: Optional[str]
    status: str
    user_id: int
    username: str
    bound_users: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    user_id: int
    tenant_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class TenantUpdate(BaseModel):
    user_id: Optional[int] = None
    tenant_name: Optional[str] = None
    status: Optional[str] = None


def _normalize_status(status: Optional[str]) -> Optional[TenantStatus]:
    if status is None:
        return None
    status_value = str(status).upper()
    if status_value not in [TenantStatus.ACTIVE.value, TenantStatus.INACTIVE.value]:
        raise HTTPException(status_code=400, detail="Invalid status")
    return TenantStatus(status_value)


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all tenants with pagination"""
    query = db.query(Tenant, User).join(User, Tenant.user_id == User.id)
    if status:
        query = query.filter(Tenant.status == str(status).upper())

    rows = query.offset(skip).limit(limit).all()
    return [
        TenantResponse(
            id=skip + index + 1,
            app_key=tenant.app_key,
            app_secret=tenant.app_secret[:10] + "...",
            tenant_name=tenant.tenant_name,
            status=tenant.status.value,
            user_id=tenant.user_id,
            username=user.username,
            bound_users=tenant.group_binding_json,
            created_at=tenant.created_at.isoformat()
        )
        for index, (tenant, user) in enumerate(rows)
    ]

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    owner = db.query(User).filter(User.id == tenant_data.user_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")

    app_key = secrets.token_urlsafe(32)
    while db.query(Tenant).filter(Tenant.app_key == app_key).first():
        app_key = secrets.token_urlsafe(32)
    app_secret = secrets.token_urlsafe(48)
    status = _normalize_status(tenant_data.status) or TenantStatus.ACTIVE

    tenant = Tenant(
        app_key=app_key,
        app_secret=app_secret,
        user_id=tenant_data.user_id,
        tenant_name=(tenant_data.tenant_name or "").strip() or None,
        status=status,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return TenantResponse(
        id=1,
        app_key=tenant.app_key,
        app_secret=tenant.app_secret[:10] + "...",
        tenant_name=tenant.tenant_name,
        status=tenant.status.value,
        user_id=tenant.user_id,
        username=owner.username,
        bound_users=tenant.group_binding_json,
        created_at=tenant.created_at.isoformat(),
    )


@router.get("/tenants/{app_key}")
async def get_tenant_detail(
    app_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed tenant information including bound users"""
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    owner = db.query(User).filter(User.id == tenant.user_id).first()

    bound_users_list = []
    if tenant.group_binding_json:
        try:
            bound_users_list = json.loads(tenant.group_binding_json)
        except:
            pass

    return {
        "id": 0,
        "app_key": tenant.app_key,
        "app_secret": tenant.app_secret,
        "tenant_name": tenant.tenant_name,
        "status": tenant.status.value,
        "user_id": tenant.user_id,
        "username": owner.username if owner else "",
        "bound_users": bound_users_list,
        "created_at": tenant.created_at.isoformat()
    }


@router.put("/tenants/{app_key}", response_model=TenantResponse)
async def update_tenant(
    app_key: str,
    tenant_data: TenantUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant_data.user_id is not None:
        owner = db.query(User).filter(User.id == tenant_data.user_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")
        tenant.user_id = tenant_data.user_id

    if tenant_data.tenant_name is not None:
        tenant.tenant_name = (tenant_data.tenant_name or "").strip() or None

    normalized_status = _normalize_status(tenant_data.status)
    if normalized_status:
        tenant.status = normalized_status

    db.commit()
    db.refresh(tenant)
    owner = db.query(User).filter(User.id == tenant.user_id).first()
    return TenantResponse(
        id=1,
        app_key=tenant.app_key,
        app_secret=tenant.app_secret[:10] + "...",
        tenant_name=tenant.tenant_name,
        status=tenant.status.value,
        user_id=tenant.user_id,
        username=owner.username if owner else "",
        bound_users=tenant.group_binding_json,
        created_at=tenant.created_at.isoformat(),
    )


@router.post("/tenants/{app_key}/disable")
async def disable_tenant(
    app_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.status = TenantStatus.INACTIVE
    db.commit()
    return {"message": "Tenant disabled"}
