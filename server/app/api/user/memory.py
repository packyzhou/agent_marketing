from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.utils import dt_to_local_str
from ...models.user import User
from ...models.memory import MemoryMeta
from ...models.tenant import Tenant
from pydantic import BaseModel

router = APIRouter()


class UserMemoryListResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]
    has_kv_file: bool
    has_digest_file: bool


class UserMemoryDetailResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    kv_content: Optional[str]
    digest_content: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]


def _get_owned_tenant(db: Session, current_user: User, app_key: str) -> Tenant:
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/memory", response_model=List[UserMemoryListResponse])
async def list_user_memory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenants = (
        db.query(Tenant)
        .filter(Tenant.user_id == current_user.id)
        .order_by(Tenant.created_at.desc())
        .all()
    )
    if not tenants:
        return []

    app_keys = [tenant.app_key for tenant in tenants]
    memory_items = db.query(MemoryMeta).filter(MemoryMeta.app_key.in_(app_keys)).all()
    memory_map = {item.app_key: item for item in memory_items}

    return [
        UserMemoryListResponse(
            app_key=tenant.app_key,
            tenant_name=tenant.tenant_name,
            rounds_count=(
                memory_map[tenant.app_key].last_processed_round
                if tenant.app_key in memory_map
                else 0
            ),
            last_processed_at=(
                dt_to_local_str(memory_map[tenant.app_key].last_updated)
                if tenant.app_key in memory_map
                else None
            ),
            has_kv_file=bool(
                tenant.app_key in memory_map
                and memory_map[tenant.app_key].kv_file_path
                and os.path.exists(memory_map[tenant.app_key].kv_file_path)
            ),
            has_digest_file=bool(
                tenant.app_key in memory_map
                and memory_map[tenant.app_key].digest_file_path
                and os.path.exists(memory_map[tenant.app_key].digest_file_path)
            ),
        )
        for tenant in tenants
    ]


@router.get("/memory/{app_key}", response_model=UserMemoryDetailResponse)
async def get_user_memory(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant = _get_owned_tenant(db, current_user, app_key)
    memory_meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not memory_meta:
        raise HTTPException(status_code=404, detail="Memory not found")

    kv_content = None
    digest_content = None
    if memory_meta.kv_file_path and os.path.exists(memory_meta.kv_file_path):
        with open(memory_meta.kv_file_path, "r", encoding="utf-8") as file:
            kv_content = file.read()
    if memory_meta.digest_file_path and os.path.exists(memory_meta.digest_file_path):
        with open(memory_meta.digest_file_path, "r", encoding="utf-8") as file:
            digest_content = file.read()

    return UserMemoryDetailResponse(
        app_key=app_key,
        tenant_name=tenant.tenant_name,
        kv_content=kv_content,
        digest_content=digest_content,
        rounds_count=memory_meta.last_processed_round or 0,
        last_processed_at=dt_to_local_str(memory_meta.last_updated),
    )
