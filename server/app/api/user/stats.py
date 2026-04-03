from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...services.token_service import get_token_stats

router = APIRouter()

@router.get("/stats/{app_key}")
async def get_stats(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = await get_token_stats(db, app_key, days=30)
    return stats
