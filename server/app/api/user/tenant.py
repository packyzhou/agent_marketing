from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.snowflake import generate_snowflake_id
from ...models.tenant import Tenant
from ...models.user import User
from pydantic import BaseModel
import secrets

router = APIRouter()

class TenantCreate(BaseModel):
    group_binding_json: str = ""

class TenantResponse(BaseModel):
    app_key: str
    app_secret: str
    user_id: int
    group_binding_json: str

    class Config:
        from_attributes = True

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_key = secrets.token_urlsafe(32)
    app_secret = secrets.token_urlsafe(48)

    tenant = Tenant(
        app_key=app_key,
        app_secret=app_secret,
        user_id=current_user.id,
        group_binding_json=tenant_data.group_binding_json
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tenants = db.query(Tenant).filter(Tenant.user_id == current_user.id).all()
    return tenants

@router.get("/tenants/{app_key}", response_model=TenantResponse)
async def get_tenant(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant
