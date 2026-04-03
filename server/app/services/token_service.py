from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.token import TokenSummary, TokenDaily

async def update_token_stats(db: Session, app_key: str, token_count: int):
    """更新Token统计"""
    today = date.today()

    # 更新每日统计
    daily_record = db.query(TokenDaily).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date == today
    ).first()

    if daily_record:
        daily_record.token_count += token_count
    else:
        daily_record = TokenDaily(
            app_key=app_key,
            date=today,
            token_count=token_count
        )
        db.add(daily_record)

    # 更新总统计
    summary = db.query(TokenSummary).filter(TokenSummary.app_key == app_key).first()
    if summary:
        summary.total_tokens += token_count
    else:
        summary = TokenSummary(app_key=app_key, total_tokens=token_count)
        db.add(summary)

    db.commit()

async def get_token_stats(db: Session, app_key: str, days: int = 30):
    """获取Token统计数据"""
    daily_stats = db.query(TokenDaily).filter(
        TokenDaily.app_key == app_key
    ).order_by(TokenDaily.date.desc()).limit(days).all()

    summary = db.query(TokenSummary).filter(TokenSummary.app_key == app_key).first()

    return {
        "daily": [{"date": str(s.date), "count": s.token_count} for s in reversed(daily_stats)],
        "total": summary.total_tokens if summary else 0
    }
