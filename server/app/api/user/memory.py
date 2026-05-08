from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.utils import dt_to_local_str
from ...models.user import User
from ...models.memory import MemoryMeta
from ...models.tenant import Tenant
from ...services.memory_service import get_domain_file, resolve_memory_file_path
from pydantic import BaseModel

router = APIRouter()


class UserMemoryListResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]
    has_kv_file: bool
    has_digest_file: bool
    has_domain_file: bool


class UserMemoryDetailResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    kv_content: Optional[str]
    digest_content: Optional[str]
    domain_content: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]


def _resolve_domain_path(memory_meta: Optional[MemoryMeta], app_key: str) -> str:
    resolved_path = resolve_memory_file_path(
        memory_meta.domain_file_path if memory_meta else None,
        get_domain_file(app_key)
    )
    return str(resolved_path) if resolved_path else ""


def _memory_file_exists(path: Optional[str]) -> bool:
    resolved_path = resolve_memory_file_path(path)
    return bool(resolved_path and resolved_path.exists())


def _read_memory_file(path: Optional[str]) -> Optional[str]:
    resolved_path = resolve_memory_file_path(path)
    if not resolved_path or not resolved_path.exists():
        return None
    with open(resolved_path, "r", encoding="utf-8") as file:
        return file.read()


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

    result = []
    for tenant in tenants:
        mem = memory_map.get(tenant.app_key)
        domain_path = _resolve_domain_path(mem, tenant.app_key)
        result.append(
            UserMemoryListResponse(
                app_key=tenant.app_key,
                tenant_name=tenant.tenant_name,
                rounds_count=(mem.last_processed_round if mem else 0),
                last_processed_at=(
                    dt_to_local_str(mem.last_updated) if mem else None
                ),
                has_kv_file=bool(mem and _memory_file_exists(mem.kv_file_path)),
                has_digest_file=bool(mem and _memory_file_exists(mem.digest_file_path)),
                has_domain_file=bool(domain_path and _memory_file_exists(domain_path)),
            )
        )
    return result


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
    domain_content = None
    kv_content = _read_memory_file(memory_meta.kv_file_path)
    digest_content = _read_memory_file(memory_meta.digest_file_path)
    domain_path = _resolve_domain_path(memory_meta, app_key)
    domain_content = _read_memory_file(domain_path)

    return UserMemoryDetailResponse(
        app_key=app_key,
        tenant_name=tenant.tenant_name,
        kv_content=kv_content,
        digest_content=digest_content,
        domain_content=domain_content,
        rounds_count=memory_meta.last_processed_round or 0,
        last_processed_at=dt_to_local_str(memory_meta.last_updated),
    )
