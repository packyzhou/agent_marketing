from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...core.utils import dt_to_local_str
from ...models.user import User
from ...models.memory import MemoryMeta
from ...models.tenant import Tenant
from pydantic import BaseModel

router = APIRouter()

class MemoryListResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]
    has_kv_file: bool
    has_digest_file: bool

class MemoryResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    kv_content: Optional[str]
    digest_content: Optional[str]
    rounds_count: int
    last_processed_at: Optional[str]

@router.get("/memory/{app_key}", response_model=MemoryResponse)
async def get_memory(
    app_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get memory files for a specific tenant"""
    memory_meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not memory_meta:
        raise HTTPException(status_code=404, detail="Memory not found")
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()

    kv_content = None
    digest_content = None

    if memory_meta.kv_file_path and os.path.exists(memory_meta.kv_file_path):
        with open(memory_meta.kv_file_path, 'r', encoding='utf-8') as f:
            kv_content = f.read()

    if memory_meta.digest_file_path and os.path.exists(memory_meta.digest_file_path):
        with open(memory_meta.digest_file_path, 'r', encoding='utf-8') as f:
            digest_content = f.read()

    return MemoryResponse(
        app_key=app_key,
        tenant_name=tenant.tenant_name if tenant else None,
        kv_content=kv_content,
        digest_content=digest_content,
        rounds_count=memory_meta.last_processed_round or 0,
        last_processed_at=dt_to_local_str(memory_meta.last_updated)
    )

@router.get("/memory", response_model=list[MemoryListResponse])
async def list_all_memory(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all memory metadata"""
    memories = db.query(MemoryMeta).offset(skip).limit(limit).all()
    app_keys = [mem.app_key for mem in memories]
    tenant_map = {}
    if app_keys:
        tenants = db.query(Tenant).filter(Tenant.app_key.in_(app_keys)).all()
        tenant_map = {tenant.app_key: tenant for tenant in tenants}

    return [
        MemoryListResponse(
            app_key=mem.app_key,
            tenant_name=tenant_map[mem.app_key].tenant_name if mem.app_key in tenant_map else None,
            rounds_count=mem.last_processed_round or 0,
            last_processed_at=dt_to_local_str(mem.last_updated),
            has_kv_file=bool(mem.kv_file_path and os.path.exists(mem.kv_file_path)),
            has_digest_file=bool(mem.digest_file_path and os.path.exists(mem.digest_file_path))
        )
        for mem in memories
    ]

@router.post("/memory/{app_key}/clear")
async def clear_memory_files(
    app_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    memory_meta = db.query(MemoryMeta).filter(MemoryMeta.app_key == app_key).first()
    if not memory_meta:
        raise HTTPException(status_code=404, detail="Memory not found")

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
    db.commit()

    return {
        "app_key": app_key,
        "cleared_kv": cleared_kv,
        "cleared_digest": cleared_digest
    }
