from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...core.snowflake import generate_snowflake_id
from ...models.provider import Provider, ProviderKey, ProviderStatus
from ...models.tenant import Tenant
from ...models.user import User
from pydantic import BaseModel

router = APIRouter()


class ProviderCreate(BaseModel):
    name: str
    code: str
    base_url: str
    config_guide: Optional[str] = None


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    config_guide: Optional[str] = None
    status: Optional[str] = None


class ProviderResponse(BaseModel):
    id: int
    name: str
    code: str
    base_url: str
    config_guide: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ProviderKeyResponse(BaseModel):
    id: int
    app_key: str
    provider_id: int
    provider_name: str
    api_key: str
    model_name: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class ProviderKeyCreate(BaseModel):
    provider_id: int
    api_key: str
    model_name: Optional[str] = None


class ProviderPageResponse(BaseModel):
    total: int
    items: List[ProviderResponse]


def _validate_non_empty_provider_fields(name: str, code: str, base_url: str):
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Provider name cannot be empty")
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Provider code cannot be empty")
    if not base_url or not base_url.strip():
        raise HTTPException(status_code=400, detail="Provider base_url cannot be empty")


def _apply_provider_non_empty_filter(query):
    return query.filter(
        and_(
            Provider.name.isnot(None),
            Provider.code.isnot(None),
            Provider.base_url.isnot(None),
            Provider.name != "",
            Provider.code != "",
            Provider.base_url != "",
        )
    )


@router.get("/providers", response_model=ProviderPageResponse)
async def list_providers(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all AI providers"""
    query = _apply_provider_non_empty_filter(db.query(Provider))
    if status:
        query = query.filter(Provider.status == status)
    total = query.count()
    items = query.order_by(Provider.created_at.desc()).offset(skip).limit(limit).all()
    return ProviderPageResponse(total=total, items=items)


@router.post("/providers", response_model=ProviderResponse)
async def create_provider(
    provider_data: ProviderCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new AI provider"""
    _validate_non_empty_provider_fields(
        provider_data.name, provider_data.code, provider_data.base_url
    )
    existing = db.query(Provider).filter(Provider.code == provider_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Provider code already exists")

    payload = provider_data.model_dump()
    payload["name"] = payload["name"].strip()
    payload["code"] = payload["code"].strip()
    payload["base_url"] = payload["base_url"].strip()
    payload["id"] = generate_snowflake_id()
    provider = Provider(**payload)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.put("/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update an AI provider"""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    update_payload = provider_data.model_dump(exclude_unset=True)
    if "name" in update_payload:
        if not update_payload["name"] or not update_payload["name"].strip():
            raise HTTPException(status_code=400, detail="Provider name cannot be empty")
        update_payload["name"] = update_payload["name"].strip()
    if "base_url" in update_payload:
        if not update_payload["base_url"] or not update_payload["base_url"].strip():
            raise HTTPException(
                status_code=400, detail="Provider base_url cannot be empty"
            )
        update_payload["base_url"] = update_payload["base_url"].strip()
    if "status" in update_payload and update_payload["status"]:
        update_payload["status"] = str(update_payload["status"]).upper()

    for key, value in update_payload.items():
        setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/providers/{provider_id}")
async def delete_provider(
    provider_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.status = ProviderStatus.INACTIVE
    db.commit()
    return {"message": "Provider disabled"}


@router.get("/provider-keys", response_model=List[ProviderKeyResponse])
async def list_provider_keys(
    app_key: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all provider API keys, optionally filtered by app_key"""
    query = db.query(ProviderKey, Provider).join(
        Provider, Provider.id == ProviderKey.provider_id
    )
    if app_key:
        query = query.filter(ProviderKey.app_key == app_key)

    records = query.all()
    return [
        ProviderKeyResponse(
            id=key.id,
            app_key=key.app_key,
            provider_id=key.provider_id,
            provider_name=provider.name,
            api_key=key.api_key[:10] + "..." if len(key.api_key) > 10 else key.api_key,
            model_name=key.model_name,
            created_at=key.created_at.isoformat(),
        )
        for key, provider in records
    ]


@router.get(
    "/tenants/{app_key}/provider-keys", response_model=List[ProviderKeyResponse]
)
async def list_tenant_provider_keys(
    app_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    records = (
        db.query(ProviderKey, Provider)
        .join(Provider, Provider.id == ProviderKey.provider_id)
        .filter(ProviderKey.app_key == app_key)
        .order_by(ProviderKey.created_at.desc())
        .all()
    )
    return [
        ProviderKeyResponse(
            id=key.id,
            app_key=key.app_key,
            provider_id=key.provider_id,
            provider_name=provider.name,
            api_key=key.api_key[:10] + "..." if len(key.api_key) > 10 else key.api_key,
            model_name=key.model_name,
            created_at=key.created_at.isoformat(),
        )
        for key, provider in records
    ]


@router.post("/tenants/{app_key}/provider-keys", response_model=ProviderKeyResponse)
async def create_tenant_provider_key(
    app_key: str,
    key_data: ProviderKeyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if str(getattr(tenant.status, "value", tenant.status)).upper() != "ACTIVE":
        raise HTTPException(status_code=400, detail="Tenant is inactive")
    provider = db.query(Provider).filter(Provider.id == key_data.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if provider.status != ProviderStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Provider is inactive")
    if not key_data.api_key or not key_data.api_key.strip():
        raise HTTPException(status_code=400, detail="api_key is required")

    existed = db.query(ProviderKey).filter(ProviderKey.app_key == app_key).first()
    if existed:
        existed.provider_id = key_data.provider_id
        existed.api_key = key_data.api_key.strip()
        existed.model_name = (
            key_data.model_name.strip()
            if key_data.model_name and key_data.model_name.strip()
            else None
        )
        db.commit()
        db.refresh(existed)
        return ProviderKeyResponse(
            id=existed.id,
            app_key=existed.app_key,
            provider_id=existed.provider_id,
            provider_name=provider.name,
            api_key=(
                existed.api_key[:10] + "..."
                if len(existed.api_key) > 10
                else existed.api_key
            ),
            model_name=existed.model_name,
            created_at=existed.created_at.isoformat(),
        )

    key = ProviderKey(
        id=generate_snowflake_id(),
        app_key=app_key,
        provider_id=key_data.provider_id,
        api_key=key_data.api_key.strip(),
        model_name=(
            key_data.model_name.strip()
            if key_data.model_name and key_data.model_name.strip()
            else None
        ),
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return ProviderKeyResponse(
        id=key.id,
        app_key=key.app_key,
        provider_id=key.provider_id,
        provider_name=provider.name,
        api_key=key.api_key[:10] + "..." if len(key.api_key) > 10 else key.api_key,
        model_name=key.model_name,
        created_at=key.created_at.isoformat(),
    )


@router.delete("/tenants/{app_key}/provider-keys/{key_id}")
async def delete_tenant_provider_key(
    app_key: str,
    key_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    key = (
        db.query(ProviderKey)
        .filter(ProviderKey.id == key_id, ProviderKey.app_key == app_key)
        .first()
    )
    if not key:
        raise HTTPException(status_code=404, detail="Provider key not found")
    db.delete(key)
    db.commit()
    return {"message": "Deleted"}
