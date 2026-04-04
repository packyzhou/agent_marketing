from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
import secrets
import json
from ...core.database import get_db
from ...core.deps import get_current_user
from ...core.snowflake import generate_snowflake_id
from ...models.tenant import Tenant, TenantStatus
from ...models.user import User, Group, GroupMemberAppBinding
from ...models.provider import Provider, ProviderKey
from .tenant_schemas import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
    ProviderKeyCreate,
    ProviderKeyResponse,
    ProviderResponse,
    GroupResponse,
    GroupPageResponse,
    GroupMemberResponse,
    GroupMemberPageResponse,
    GroupMemberBindRequest,
)

router = APIRouter()


def _get_accessible_group(db: Session, current_user: User, group_id: int) -> Group:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.owner_id != current_user.id and group.id != current_user.group_id:
        raise HTTPException(status_code=403, detail="No permission to access group")

    return group


def _build_group_member_responses(
    db: Session,
    members: List[User],
    binding_owner_id: int,
) -> List[GroupMemberResponse]:
    member_ids = [member.id for member in members]
    binding_map = {}
    tenant_map = {}

    if member_ids:
        bindings = (
            db.query(GroupMemberAppBinding)
            .filter(
                GroupMemberAppBinding.owner_user_id == binding_owner_id,
                GroupMemberAppBinding.member_id.in_(member_ids),
            )
            .all()
        )
        binding_map = {binding.member_id: binding for binding in bindings}
        app_keys = [binding.app_key for binding in bindings if binding.app_key]
        if app_keys:
            tenants = db.query(Tenant).filter(Tenant.app_key.in_(app_keys)).all()
            tenant_map = {tenant.app_key: tenant for tenant in tenants}

    return [
        GroupMemberResponse(
            member_id=str(member.id),
            username=member.username,
            member_name=member.real_name or member.username,
            phone=member.phone,
            app_key=(
                binding_map.get(member.id).app_key
                if binding_map.get(member.id)
                else None
            ),
            app_key_status=(
                str(tenant_map[binding_map[member.id].app_key].status.value)
                if binding_map.get(member.id)
                and binding_map[member.id].app_key in tenant_map
                else None
            ),
            created_at=member.created_at,
        )
        for member in members
    ]


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建租户（AppKey）"""
    app_key = secrets.token_urlsafe(32)
    app_secret = secrets.token_urlsafe(48)

    # 如果需要绑定分组用户
    group_binding_json = None
    if tenant_data.bind_group_users and tenant_data.binding_user_ids:
        # 查询分组用户信息
        users = (
            db.query(User)
            .filter(
                User.id.in_(tenant_data.binding_user_ids),
                User.group_id == current_user.group_id,
            )
            .all()
        )

        binding_data = [
            {
                "user_id": user.id,
                "real_name": user.real_name or "",
                "phone": user.phone or "",
            }
            for user in users
        ]
        group_binding_json = json.dumps(binding_data, ensure_ascii=False)

    tenant = Tenant(
        app_key=app_key,
        app_secret=app_secret,
        user_id=current_user.id,
        tenant_name=tenant_data.tenant_name,
        group_binding_json=group_binding_json,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取当前用户的所有租户"""
    tenants = db.query(Tenant).filter(Tenant.user_id == current_user.id).all()
    return tenants


@router.get("/tenants/group", response_model=List[TenantResponse])
async def list_group_tenants(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取当前用户分组下所有租户"""
    if not current_user.group_id:
        return []

    # 查询分组内所有用户
    group_users = db.query(User).filter(User.group_id == current_user.group_id).all()
    user_ids = [user.id for user in group_users]

    # 查询这些用户的所有租户
    tenants = db.query(Tenant).filter(Tenant.user_id.in_(user_ids)).all()
    return tenants


@router.get("/groups", response_model=GroupPageResponse)
async def list_groups(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据登录用户ID分页查询分组列表"""
    if current_user.group_id:
        query = db.query(Group).filter(
            or_(Group.owner_id == current_user.id, Group.id == current_user.group_id)
        )
    else:
        query = db.query(Group).filter(Group.owner_id == current_user.id)
    total = query.count()
    groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for group in groups:
        member_count = (
            db.query(User)
            .filter(User.group_id == group.id, User.id != group.owner_id)
            .count()
        )
        items.append(
            GroupResponse(
                id=str(group.id),
                group_name=group.group_name,
                owner_id=str(group.owner_id),
                member_count=member_count,
                can_manage=group.owner_id == current_user.id,
                created_at=group.created_at,
            )
        )

    return GroupPageResponse(total=total, items=items)


@router.get("/groups/{group_id}/members", response_model=GroupMemberPageResponse)
async def list_group_members_by_group(
    group_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = _get_accessible_group(db, current_user, group_id)
    query = (
        db.query(User)
        .filter(User.group_id == group.id, User.id != group.owner_id)
        .order_by(User.created_at.desc())
    )
    total = query.count()
    members = query.offset(skip).limit(limit).all()
    items = _build_group_member_responses(db, members, group.owner_id)
    return GroupMemberPageResponse(total=total, items=items)


@router.get("/tenants/{app_key}", response_model=TenantResponse)
async def get_tenant(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取租户详情"""
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.put("/tenants/{app_key}", response_model=TenantResponse)
async def update_tenant(
    app_key: str,
    tenant_data: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新租户信息"""
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if str(getattr(tenant.status, "value", tenant.status)).upper() != "ACTIVE":
        raise HTTPException(status_code=400, detail="Tenant is inactive")

    if tenant_data.tenant_name:
        tenant.tenant_name = tenant_data.tenant_name

    if tenant_data.status:
        status_value = str(tenant_data.status).upper()
        if status_value not in [TenantStatus.ACTIVE.value, TenantStatus.INACTIVE.value]:
            raise HTTPException(status_code=400, detail="Invalid tenant status")
        tenant.status = TenantStatus(status_value)

    if tenant_data.binding_user_ids is not None:
        users = (
            db.query(User)
            .filter(
                User.id.in_(tenant_data.binding_user_ids),
                User.group_id == current_user.group_id,
            )
            .all()
        )

        binding_data = [
            {
                "user_id": user.id,
                "real_name": user.real_name or "",
                "phone": user.phone or "",
            }
            for user in users
        ]
        tenant.group_binding_json = json.dumps(binding_data, ensure_ascii=False)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/group-members", response_model=List[GroupMemberResponse])
async def list_group_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    members = (
        db.query(User)
        .filter(User.referral_id == current_user.id)
        .order_by(User.created_at.desc())
        .all()
    )
    return _build_group_member_responses(db, members, current_user.id)


@router.get("/active-app-keys", response_model=List[TenantResponse])
async def list_owned_active_tenants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenants = (
        db.query(Tenant)
        .filter(Tenant.user_id == current_user.id, Tenant.status == TenantStatus.ACTIVE)
        .order_by(Tenant.created_at.desc())
        .all()
    )
    return tenants


@router.post("/group-members/{member_id}/bind-app-key")
async def bind_member_app_key(
    member_id: int,
    data: GroupMemberBindRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = (
        db.query(User)
        .filter(User.id == member_id, User.referral_id == current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    app_key = (data.app_key or "").strip() or None
    if app_key:
        tenant = (
            db.query(Tenant)
            .filter(
                Tenant.app_key == app_key,
                Tenant.user_id == current_user.id,
                Tenant.status == TenantStatus.ACTIVE,
            )
            .first()
        )
        if not tenant:
            raise HTTPException(
                status_code=400, detail="AppKey not found or not active"
            )

    binding = (
        db.query(GroupMemberAppBinding)
        .filter(
            GroupMemberAppBinding.owner_user_id == current_user.id,
            GroupMemberAppBinding.member_id == member_id,
        )
        .first()
    )
    if binding:
        binding.app_key = app_key
    else:
        binding = GroupMemberAppBinding(
            owner_user_id=current_user.id,
            member_id=member_id,
            app_key=app_key,
        )
        db.add(binding)
    db.commit()
    return {"message": "Bind success"}


@router.delete("/groups/{group_id}/members/{member_id}")
async def delete_group_member(
    group_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = _get_accessible_group(db, current_user, group_id)
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only group owner can delete members")

    member = (
        db.query(User)
        .filter(
            User.id == member_id,
            User.group_id == group.id,
            User.id != group.owner_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    owned_group = db.query(Group).filter(Group.owner_id == member.id).first()
    if not owned_group:
        raise HTTPException(status_code=400, detail="Member personal group not found")

    (
        db.query(GroupMemberAppBinding)
        .filter(
            or_(
                GroupMemberAppBinding.member_id == member.id,
                and_(
                    GroupMemberAppBinding.owner_user_id == current_user.id,
                    GroupMemberAppBinding.member_id == member.id,
                ),
            )
        )
        .delete(synchronize_session=False)
    )

    member.referral_id = None
    member.group_id = owned_group.id
    db.commit()
    return {"message": "Member removed successfully"}


# 供应商配置相关接口
@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取所有可用的供应商"""
    providers = (
        db.query(Provider)
        .filter(
            and_(
                Provider.status == "ACTIVE",
                Provider.name.isnot(None),
                Provider.code.isnot(None),
                Provider.base_url.isnot(None),
                Provider.name != "",
                Provider.code != "",
                Provider.base_url != "",
            )
        )
        .all()
    )
    return providers


@router.post("/tenants/{app_key}/provider-keys", response_model=ProviderKeyResponse)
async def create_provider_key(
    app_key: str,
    key_data: ProviderKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """为租户配置供应商API Key"""
    # 验证租户所有权
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if str(getattr(tenant.status, "value", tenant.status)).upper() != "ACTIVE":
        raise HTTPException(status_code=400, detail="Tenant is inactive")

    existing_key = (
        db.query(ProviderKey)
        .filter(ProviderKey.app_key == app_key)
        .order_by(ProviderKey.updated_at.desc(), ProviderKey.created_at.desc())
        .first()
    )
    if existing_key:
        existing_key.provider_id = key_data.provider_id
        existing_key.api_key = key_data.api_key
        existing_key.model_name = key_data.model_name
        duplicate_keys = (
            db.query(ProviderKey)
            .filter(ProviderKey.app_key == app_key, ProviderKey.id != existing_key.id)
            .all()
        )
        for duplicate in duplicate_keys:
            db.delete(duplicate)
        db.commit()
        db.refresh(existing_key)
        return existing_key

    provider_key = ProviderKey(
        id=generate_snowflake_id(),
        app_key=app_key,
        provider_id=key_data.provider_id,
        api_key=key_data.api_key,
        model_name=key_data.model_name,
    )
    db.add(provider_key)
    db.commit()
    db.refresh(provider_key)
    return provider_key


@router.get(
    "/tenants/{app_key}/provider-keys", response_model=List[ProviderKeyResponse]
)
async def list_provider_keys(
    app_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取租户的所有供应商配置"""
    # 验证租户所有权
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    keys = (
        db.query(ProviderKey)
        .filter(ProviderKey.app_key == app_key)
        .order_by(ProviderKey.updated_at.desc(), ProviderKey.created_at.desc())
        .limit(1)
        .all()
    )
    return keys


@router.delete("/tenants/{app_key}/provider-keys/{key_id}")
async def delete_provider_key(
    app_key: str,
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除供应商配置"""
    # 验证租户所有权
    tenant = (
        db.query(Tenant)
        .filter(Tenant.app_key == app_key, Tenant.user_id == current_user.id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    key = (
        db.query(ProviderKey)
        .filter(ProviderKey.id == key_id, ProviderKey.app_key == app_key)
        .first()
    )

    if not key:
        raise HTTPException(status_code=404, detail="Provider key not found")

    db.delete(key)
    db.commit()
    return {"message": "Provider key deleted successfully"}
