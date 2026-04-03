from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.token import TokenSummary, TokenDaily

async def update_token_stats(db: Session, app_key: str, token_count: int, request_count: int = 1):
    """更新Token统计"""
    today = date.today()
    current_month_start = date(today.year, today.month, 1)

    # 计算上月开始日期
    if today.month == 1:
        last_month_start = date(today.year - 1, 12, 1)
        last_month_end = date(today.year - 1, 12, 31)
    else:
        last_month_start = date(today.year, today.month - 1, 1)
        # 上月最后一天
        last_month_end = current_month_start - timedelta(days=1)

    # 更新每日统计
    daily_record = db.query(TokenDaily).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date == today
    ).first()

    if daily_record:
        daily_record.token_count += token_count
        daily_record.request_count += request_count
    else:
        daily_record = TokenDaily(
            app_key=app_key,
            date=today,
            token_count=token_count,
            request_count=request_count
        )
        db.add(daily_record)

    # 计算本月总量
    current_month_total = db.query(func.sum(TokenDaily.token_count)).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date >= current_month_start
    ).scalar() or 0

    # 计算上月总量
    last_month_total = db.query(func.sum(TokenDaily.token_count)).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date >= last_month_start,
        TokenDaily.date <= last_month_end
    ).scalar() or 0

    # 更新总统计
    summary = db.query(TokenSummary).filter(TokenSummary.app_key == app_key).first()
    if summary:
        summary.total_tokens += token_count
        summary.current_month_tokens = current_month_total
        summary.last_month_tokens = last_month_total
    else:
        summary = TokenSummary(
            app_key=app_key,
            total_tokens=token_count,
            current_month_tokens=current_month_total,
            last_month_tokens=last_month_total
        )
        db.add(summary)

    db.commit()

async def get_token_stats(db: Session, app_key: str, days: int = 30):
    """获取Token统计数据"""
    # 获取最近N天的统计
    start_date = date.today() - timedelta(days=days - 1)
    daily_stats = db.query(TokenDaily).filter(
        TokenDaily.app_key == app_key,
        TokenDaily.date >= start_date
    ).order_by(TokenDaily.date.asc()).all()

    # 获取总统计
    summary = db.query(TokenSummary).filter(TokenSummary.app_key == app_key).first()

    # 计算月同比
    month_comparison = 0
    if summary and summary.last_month_tokens > 0:
        month_comparison = ((summary.current_month_tokens - summary.last_month_tokens)
                          / summary.last_month_tokens * 100)

    return {
        "daily": [
            {
                "date": str(stat.date),
                "token_count": stat.token_count,
                "request_count": stat.request_count
            }
            for stat in daily_stats
        ],
        "total_tokens": summary.total_tokens if summary else 0,
        "current_month_tokens": summary.current_month_tokens if summary else 0,
        "last_month_tokens": summary.last_month_tokens if summary else 0,
        "month_comparison": round(month_comparison, 2)
    }

async def get_group_token_stats(db: Session, app_keys: list, days: int = 30):
    """获取分组内所有租户的Token统计"""
    all_stats = []
    for app_key in app_keys:
        stats = await get_token_stats(db, app_key, days)
        stats["app_key"] = app_key
        all_stats.append(stats)

    return all_stats
