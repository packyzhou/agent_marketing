from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.user import User
from ...models.tenant import Tenant
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

@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all tenants with pagination"""
    query = db.query(Tenant).join(User, Tenant.user_id == User.id)
    if status:
        query = query.filter(Tenant.status == status)

    tenants = query.offset(skip).limit(limit).all()
    return [
        TenantResponse(
            id=tenant.id,
            app_key=tenant.app_key,
            app_secret=tenant.app_secret[:10] + "...",
            tenant_name=tenant.tenant_name,
            status=tenant.status.value,
            user_id=tenant.user_id,
            username=tenant.user.username,
            bound_users=tenant.bound_users,
            created_at=tenant.created_at.isoformat()
        )
        for tenant in tenants
    ]

@router.get("/tenants/{tenant_id}")
async def get_tenant_detail(
    tenant_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed tenant information including bound users"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    bound_users_list = []
    if tenant.bound_users:
        try:
            bound_users_list = json.loads(tenant.bound_users)
        except:
            pass

    return {
        "id": tenant.id,
        "app_key": tenant.app_key,
        "app_secret": tenant.app_secret,
        "tenant_name": tenant.tenant_name,
        "status": tenant.status.value,
        "user_id": tenant.user_id,
        "username": tenant.user.username,
        "bound_users": bound_users_list,
        "created_at": tenant.created_at.isoformat()
    }
