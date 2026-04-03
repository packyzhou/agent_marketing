from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.tenant import Tenant
from ...services.token_service import get_token_stats, get_group_token_stats

router = APIRouter()

@router.get("/stats/{app_key}")
async def get_stats(
    app_key: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定租户的Token统计"""
    # 验证租户所有权
    tenant = db.query(Tenant).filter(
        Tenant.app_key == app_key,
        Tenant.user_id == current_user.id
    ).first()

    if not tenant:
        # 检查是否是分组内的租户
        if current_user.group_id:
            group_users = db.query(User).filter(User.group_id == current_user.group_id).all()
            user_ids = [u.id for u in group_users]
            tenant = db.query(Tenant).filter(
                Tenant.app_key == app_key,
                Tenant.user_id.in_(user_ids)
            ).first()

    if not tenant:
        return {"error": "Tenant not found or access denied"}

    stats = await get_token_stats(db, app_key, days)
    return stats

@router.get("/stats/group/all")
async def get_group_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户分组下所有租户的Token统计"""
    if not current_user.group_id:
        return []

    # 查询分组内所有用户
    group_users = db.query(User).filter(User.group_id == current_user.group_id).all()
    user_ids = [user.id for user in group_users]

    # 查询这些用户的所有租户
    tenants = db.query(Tenant).filter(Tenant.user_id.in_(user_ids)).all()
    app_keys = [t.app_key for t in tenants]

    # 获取统计数据
    stats = await get_group_token_stats(db, app_keys, days)

    # 添加租户名称
    tenant_map = {t.app_key: t.tenant_name for t in tenants}
    for stat in stats:
        stat["tenant_name"] = tenant_map.get(stat["app_key"], "未命名")

    return stats
