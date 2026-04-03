from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.provider import Provider, ProviderKey
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


@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)
):
    """List all AI providers"""
    providers = _apply_provider_non_empty_filter(db.query(Provider)).all()
    return providers


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

    for key, value in update_payload.items():
        setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    return provider


@router.get("/provider-keys", response_model=List[ProviderKeyResponse])
async def list_provider_keys(
    app_key: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all provider API keys, optionally filtered by app_key"""
    query = db.query(ProviderKey).join(Provider)
    if app_key:
        query = query.filter(ProviderKey.app_key == app_key)

    keys = query.all()
    return [
        ProviderKeyResponse(
            id=key.id,
            app_key=key.app_key,
            provider_id=key.provider_id,
            provider_name=key.provider.name,
            api_key=key.api_key[:10] + "..." if len(key.api_key) > 10 else key.api_key,
            model_name=key.model_name,
            created_at=key.created_at.isoformat(),
        )
        for key in keys
    ]
