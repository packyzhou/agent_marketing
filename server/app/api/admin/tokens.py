from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...models.user import User
from ...models.token import TokenSummary, TokenDaily
from ...models.tenant import Tenant
from pydantic import BaseModel

router = APIRouter()

class TokenStatsResponse(BaseModel):
    app_key: str
    tenant_name: Optional[str]
    total_tokens: int
    current_month_tokens: int
    last_month_tokens: int
    monthly_change_percent: Optional[float]

    class Config:
        from_attributes = True

class TokenDailyResponse(BaseModel):
    date: str
    token_count: int
    request_count: int

@router.get("/token-stats", response_model=List[TokenStatsResponse])
async def list_token_stats(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List token usage statistics for all tenants"""
    summaries = db.query(TokenSummary, Tenant).join(
        Tenant, TokenSummary.app_key == Tenant.app_key
    ).offset(skip).limit(limit).all()

    return [
        TokenStatsResponse(
            app_key=summary.app_key,
            tenant_name=tenant.tenant_name,
            total_tokens=summary.total_tokens,
            current_month_tokens=summary.current_month_tokens,
            last_month_tokens=summary.last_month_tokens,
            monthly_change_percent=(
                ((summary.current_month_tokens - summary.last_month_tokens) / summary.last_month_tokens) * 100
                if summary.last_month_tokens and summary.last_month_tokens > 0
                else None
            )
        )
        for summary, tenant in summaries
    ]

@router.get("/token-stats/{app_key}/daily", response_model=List[TokenDailyResponse])
async def get_daily_token_stats(
    app_key: str,
    days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get daily token usage for a specific tenant"""
    start_date = datetime.now() - timedelta(days=days)

    daily_stats = db.query(TokenDaily).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date >= start_date.date()
    ).order_by(TokenDaily.date).all()

    return [
        TokenDailyResponse(
            date=stat.date.isoformat(),
            token_count=stat.token_count,
            request_count=stat.request_count
        )
        for stat in daily_stats
    ]

@router.get("/token-stats/summary")
async def get_token_summary(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get overall token usage summary"""
    total_tokens = db.query(func.sum(TokenSummary.total_tokens)).scalar() or 0
    total_current_month = db.query(func.sum(TokenSummary.current_month_tokens)).scalar() or 0
    total_last_month = db.query(func.sum(TokenSummary.last_month_tokens)).scalar() or 0
    tenant_count = db.query(func.count(TokenSummary.app_key)).scalar() or 0

    monthly_change = None
    if total_last_month > 0:
        monthly_change = ((total_current_month - total_last_month) / total_last_month) * 100

    return {
        "total_tokens": total_tokens,
        "current_month_tokens": total_current_month,
        "last_month_tokens": total_last_month,
        "monthly_change_percent": monthly_change,
        "tenant_count": tenant_count
    }
