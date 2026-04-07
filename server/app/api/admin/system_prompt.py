from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.user import User
from ...models.system_prompt import SystemPrompt

router = APIRouter()


class SystemPromptCreate(BaseModel):
    prompt_type: str
    content: str


class SystemPromptUpdate(BaseModel):
    content: str


class SystemPromptResponse(BaseModel):
    id: int
    prompt_type: str
    content: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def _to_response(sp: SystemPrompt) -> SystemPromptResponse:
    return SystemPromptResponse(
        id=sp.id,
        prompt_type=sp.prompt_type,
        content=sp.content,
        created_at=sp.created_at.isoformat() if sp.created_at else "",
        updated_at=sp.updated_at.isoformat() if sp.updated_at else "",
    )


@router.get("/system-prompts", response_model=List[SystemPromptResponse])
async def list_system_prompts(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    items = db.query(SystemPrompt).order_by(SystemPrompt.id.asc()).all()
    return [_to_response(sp) for sp in items]


@router.post("/system-prompts", response_model=SystemPromptResponse)
async def create_system_prompt(
    data: SystemPromptCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if not data.prompt_type or not data.prompt_type.strip():
        raise HTTPException(status_code=400, detail="prompt_type cannot be empty")
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="content cannot be empty")

    existing = db.query(SystemPrompt).filter(
        SystemPrompt.prompt_type == data.prompt_type.strip()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="prompt_type already exists")

    sp = SystemPrompt(prompt_type=data.prompt_type.strip(), content=data.content)
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return _to_response(sp)


@router.put("/system-prompts/{prompt_id}", response_model=SystemPromptResponse)
async def update_system_prompt(
    prompt_id: int,
    data: SystemPromptUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    sp = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="System prompt not found")
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="content cannot be empty")

    sp.content = data.content
    db.commit()
    db.refresh(sp)
    return _to_response(sp)


@router.delete("/system-prompts/{prompt_id}")
async def delete_system_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    sp = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="System prompt not found")
    db.delete(sp)
    db.commit()
    return {"message": "Deleted"}
