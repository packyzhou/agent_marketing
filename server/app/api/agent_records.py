"""Public data interface for agent plugins (app_key-authenticated).

Plugins run as separate stdio subprocesses, so they authenticate with the
tenant app_key (like the chat proxy) rather than a JWT. The scan-and-save
example plugin POSTs its directory listing here to persist it.
"""

import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.utils import dt_to_local_str
from ..models.file_scan import FileScanRecord
from ..models.tenant import Tenant

router = APIRouter()


class FileEntry(BaseModel):
    name: str
    is_dir: bool = False
    size: Optional[int] = None


class FileRecordCreate(BaseModel):
    app_key: str
    path: str
    files: List[FileEntry] = []


class FileRecordResponse(BaseModel):
    id: int
    app_key: str
    scan_path: str
    file_count: int
    files: List[Any]
    created_at: Optional[str]


def _require_tenant(db: Session, app_key: str) -> None:
    app_key = (app_key or "").strip()
    if not app_key:
        raise HTTPException(status_code=401, detail="Missing app_key")
    tenant = db.query(Tenant).filter(Tenant.app_key == app_key).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid app_key")


def _to_response(record: FileScanRecord) -> FileRecordResponse:
    try:
        files = json.loads(record.files) if record.files else []
        if not isinstance(files, list):
            files = []
    except (json.JSONDecodeError, TypeError):
        files = []
    return FileRecordResponse(
        id=record.id,
        app_key=record.app_key,
        scan_path=record.scan_path,
        file_count=record.file_count,
        files=files,
        created_at=dt_to_local_str(record.created_at),
    )


@router.post("/file-records", response_model=FileRecordResponse)
def create_file_record(data: FileRecordCreate, db: Session = Depends(get_db)):
    _require_tenant(db, data.app_key)
    files = [f.model_dump() for f in data.files]
    record = FileScanRecord(
        app_key=data.app_key.strip(),
        scan_path=(data.path or "")[:1024],
        file_count=len(files),
        files=json.dumps(files, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_response(record)


@router.get("/file-records", response_model=List[FileRecordResponse])
def list_file_records(app_key: str, limit: int = 20, db: Session = Depends(get_db)):
    _require_tenant(db, app_key)
    limit = max(1, min(int(limit or 20), 100))
    records = (
        db.query(FileScanRecord)
        .filter(FileScanRecord.app_key == app_key.strip())
        .order_by(desc(FileScanRecord.id))
        .limit(limit)
        .all()
    )
    return [_to_response(r) for r in records]
