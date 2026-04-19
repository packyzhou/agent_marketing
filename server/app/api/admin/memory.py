from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
from ...core.database import get_db
from ...core.deps import get_current_user, is_admin
from ...core.utils import dt_to_local_str
from ...models.user import User
from ...models.memory import MemoryMeta
from ...models.tenant import Tenant
from pydantic import BaseModel

router = APIRouter()

class MemoryListResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    username: Optional[str]
    total_duration_seconds: int
    memory_size: int
    last_processed_at: Optional[str]
    has_kv_file: bool
    has_digest_file: bool

class MemoryResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    kv_content: Optional[str]
    digest_content: Optional[str]
    total_duration_seconds: int
    memory_size: int
    last_processed_at: Optional[str]


def _read_text_file(path: Optional[str]) -> str:
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _calc_memory_size(kv_content: str, digest_content: str) -> int:
    """记忆库容量 = 事实记忆层 + 行为摘要层 的字符数"""
    return len(kv_content or "") + len(digest_content or "")

@router.get("/memory/{app_key}", response_model=MemoryResponse)
async def get_memory(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get memory files for a specific tenant"""
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # USER role: can only view memory for their own tenants
    if not is_admin(db, current_user) and tenant.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    memory_meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    kv_content = _read_text_file(memory_meta.kv_file_path) if memory_meta else ""
    digest_content = _read_text_file(memory_meta.digest_file_path) if memory_meta else ""

    return MemoryResponse(
        app_key=app_key,
        tenant_name=tenant.tenant_name,
        kv_content=kv_content or None,
        digest_content=digest_content or None,
        total_duration_seconds=(memory_meta.total_duration_seconds if memory_meta else 0) or 0,
        memory_size=_calc_memory_size(kv_content, digest_content),
        last_processed_at=dt_to_local_str(memory_meta.last_updated) if memory_meta else None
    )

@router.get("/memory", response_model=list[MemoryListResponse])
async def list_all_memory(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tenants with their memory info (admin: all; user: only own tenants)"""
    tenant_query = db.query(Tenant)
    if not is_admin(db, current_user):
        tenant_query = tenant_query.filter(Tenant.user_id == current_user.id)
    tenants = (
        tenant_query
        .order_by(Tenant.created_at.desc())
        .offset(skip).limit(limit)
        .all()
    )
    if not tenants:
        return []

    app_keys = [t.app_key for t in tenants]
    memory_items = db.query(MemoryMeta).filter(MemoryMeta.app_key.in_(app_keys)).all()
    memory_map = {m.app_key: m for m in memory_items}

    owner_ids = {t.user_id for t in tenants if t.user_id is not None}
    user_map = {}
    if owner_ids:
        users = db.query(User).filter(User.id.in_(owner_ids)).all()
        user_map = {u.id: u.username for u in users}

    result = []
    for tenant in tenants:
        mem = memory_map.get(tenant.app_key)
        kv_content = _read_text_file(mem.kv_file_path) if mem else ""
        digest_content = _read_text_file(mem.digest_file_path) if mem else ""
        result.append(
            MemoryListResponse(
                app_key=tenant.app_key,
                tenant_name=tenant.tenant_name,
                username=user_map.get(tenant.user_id),
                total_duration_seconds=(mem.total_duration_seconds if mem else 0) or 0,
                memory_size=_calc_memory_size(kv_content, digest_content),
                last_processed_at=dt_to_local_str(mem.last_updated) if mem else None,
                has_kv_file=bool(mem and mem.kv_file_path and os.path.exists(mem.kv_file_path)),
                has_digest_file=bool(mem and mem.digest_file_path and os.path.exists(mem.digest_file_path))
            )
        )
    return result

@router.post("/memory/{app_key}/clear")
async def clear_memory_files(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    memory_meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not memory_meta:
        raise HTTPException(status_code=404, detail="Memory not found")

    # USER role: can only clear memory for their own tenants
    if not is_admin(db, current_user):
        tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
        if not tenant or tenant.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    cleared_kv = False
    cleared_digest = False

    if memory_meta.kv_file_path and os.path.exists(memory_meta.kv_file_path):
        with open(memory_meta.kv_file_path, "w", encoding="utf-8") as f:
            f.write("")
        cleared_kv = True

    if memory_meta.digest_file_path and os.path.exists(memory_meta.digest_file_path):
        with open(memory_meta.digest_file_path, "w", encoding="utf-8") as f:
            f.write("")
        cleared_digest = True

    memory_meta.last_processed_round = 0
    memory_meta.total_duration_seconds = 0
    db.commit()

    return {
        "app_key": app_key,
        "cleared_kv": cleared_kv,
        "cleared_digest": cleared_digest
    }
