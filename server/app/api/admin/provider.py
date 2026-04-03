from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.provider import Provider, ProviderKey
from ...models.user import User
from pydantic import BaseModel

router = APIRouter()

class ProviderCreate(BaseModel):
    name: str
    base_url: str

class ProviderResponse(BaseModel):
    id: int
    name: str
    base_url: str
    status: str

    class Config:
        from_attributes = True

@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    providers = db.query(Provider).all()
    return providers

@router.post("/providers", response_model=ProviderResponse)
async def create_provider(
    provider_data: ProviderCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    provider = Provider(**provider_data.dict())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider
