from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import secrets
import json
from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.tenant import Tenant
from ...models.user import User
from ...models.provider import Provider, ProviderKey
from .tenant_schemas import (
    TenantCreate, TenantResponse, TenantUpdate,
    ProviderKeyCreate, ProviderKeyResponse, ProviderResponse
)

router = APIRouter()

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建租户（AppKey）"""
    app_key = secrets.token_urlsafe(32)
    app_secret = secrets.token_urlsafe(48)

    # 如果需要绑定分组用户
    group_binding_json = None
    if tenant_data.bind_group_users and tenant_data.binding_user_ids:
        # 查询分组用户信息
        users = db.query(User).filter(
            User.id.in_(tenant_data.binding_user_ids),
            User.group_id == current_user.group_id
        ).all()

        binding_data = [
            {
                "user_id": user.id,
                "real_name": user.real_name or "",
                "phone": user.phone or ""
            }
            for user in users
        ]
        group_binding_json = json.dumps(binding_data, ensure_ascii=False)

    tenant = Tenant(
        app_key=app_key,
        app_secret=app_secret,
        user_id=current_user.id,
        tenant_name=tenant_data.tenant_name,
        group_binding_json=group_binding_json
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
    """获取当前用户的所有租户"""
    tenants = db.query(Tenant).filter(Tenant.user_id == current_user.id).all()
    return tenants

@router.get("/tenants/group", response_model=List[TenantResponse])
async def list_group_tenants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户分组下所有租户"""
    if not current_user.group_id:
        return []

    # 查询分组内所有用户
    group_users = db.query(User).filter(User.group_id == current_user.group_id).all()
    user_ids = [user.id for user in group_users]

    # 查询这些用户的所有租户
    tenants = db.query(Tenant).filter(Tenant.user_id.in_(user_ids)).all()
    return tenants

@router.get("/tenants/{app_key}", response_model=TenantResponse)
async def get_tenant(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取租户详情"""
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant

@router.put("/tenants/{app_key}", response_model=TenantResponse)
async def update_tenant(
    app_key: str,
    tenant_data: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新租户信息"""
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant_data.tenant_name:
        tenant.tenant_name = tenant_data.tenant_name

    if tenant_data.status:
        tenant.status = tenant_data.status

    if tenant_data.binding_user_ids is not None:
        users = db.query(User).filter(
            User.id.in_(tenant_data.binding_user_ids),
            User.group_id == current_user.group_id
        ).all()

        binding_data = [
            {
                "user_id": user.id,
                "real_name": user.real_name or "",
                "phone": user.phone or ""
            }
            for user in users
        ]
        tenant.group_binding_json = json.dumps(binding_data, ensure_ascii=False)

    db.commit()
    db.refresh(tenant)
    return tenant

# 供应商配置相关接口
@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有可用的供应商"""
    providers = db.query(Provider).filter(
        and_(
            Provider.status == "ACTIVE",
            Provider.name.isnot(None),
            Provider.code.isnot(None),
            Provider.base_url.isnot(None),
            Provider.name != "",
            Provider.code != "",
            Provider.base_url != ""
        )
    ).all()
    return providers

@router.post("/tenants/{app_key}/provider-keys", response_model=ProviderKeyResponse)
async def create_provider_key(
    app_key: str,
    key_data: ProviderKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """为租户配置供应商API Key"""
    # 验证租户所有权
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 检查是否已存在配置
    existing_key = db.query(ProviderKey).filter(
        ProviderKey.app_key == app_key,
        ProviderKey.provider_id == key_data.provider_id
    ).first()

    if existing_key:
        # 更新现有配置
        existing_key.api_key = key_data.api_key
        existing_key.model_name = key_data.model_name
        db.commit()
        db.refresh(existing_key)
        return existing_key
    else:
        # 创建新配置
        provider_key = ProviderKey(
            app_key=app_key,
            provider_id=key_data.provider_id,
            api_key=key_data.api_key,
            model_name=key_data.model_name
        )
        db.add(provider_key)
        db.commit()
        db.refresh(provider_key)
        return provider_key

@router.get("/tenants/{app_key}/provider-keys", response_model=List[ProviderKeyResponse])
async def list_provider_keys(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取租户的所有供应商配置"""
    # 验证租户所有权
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    keys = db.query(ProviderKey).filter(ProviderKey.app_key == app_key).all()
    return keys

@router.delete("/tenants/{app_key}/provider-keys/{key_id}")
async def delete_provider_key(
    app_key: str,
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除供应商配置"""
    # 验证租户所有权
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    key = db.query(ProviderKey).filter(
        ProviderKey.id == key_id,
        ProviderKey.app_key == app_key
    ).first()

    if not key:
        raise HTTPException(status_code=404, detail="Provider key not found")

    db.delete(key)
    db.commit()
    return {"message": "Provider key deleted successfully"}
