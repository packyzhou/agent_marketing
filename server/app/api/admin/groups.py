from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.deps import get_current_admin_user
from ...core.utils import dt_to_local_str
from ...models.user import User, Group, GroupMemberAppBinding
from ...models.tenant import Tenant
from pydantic import BaseModel, Field

router = APIRouter()


class GroupResponse(BaseModel):
    id: str
    group_name: str
    owner_id: str
    owner_username: str
    owner_phone: Optional[str]
    member_count: int
    created_at: str


class GroupPageResponse(BaseModel):
    total: int
    items: List[GroupResponse]


class MemberTenantResponse(BaseModel):
    tenant_name: Optional[str]
    app_key: str
    status: str


class GroupMemberResponse(BaseModel):
    member_id: str
    username: str
    member_name: str
    phone: Optional[str]
    referral_id: Optional[str]
    app_key: Optional[str]
    app_key_status: Optional[str]
    owned_tenants: List[MemberTenantResponse] = Field(default_factory=list)
    created_at: str


class GroupMemberPageResponse(BaseModel):
    total: int
    items: List[GroupMemberResponse]


def _build_group_member_items(
    db: Session,
    members: List[User],
    binding_owner_id: int,
) -> List[GroupMemberResponse]:
    member_ids = [member.id for member in members]
    binding_map = {}
    tenant_map = {}
    owned_tenant_map = {}

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
        owned_tenants = (
            db.query(Tenant)
            .filter(Tenant.user_id.in_(member_ids))
            .order_by(Tenant.created_at.desc())
            .all()
        )
        for tenant in owned_tenants:
            owned_tenant_map.setdefault(tenant.user_id, []).append(
                MemberTenantResponse(
                    tenant_name=tenant.tenant_name,
                    app_key=tenant.app_key,
                    status=str(getattr(tenant.status, "value", tenant.status)),
                )
            )

    return [
        GroupMemberResponse(
            member_id=str(member.id),
            username=member.username,
            member_name=member.real_name or member.username,
            phone=member.phone,
            referral_id=str(member.referral_id) if member.referral_id is not None else None,
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
            owned_tenants=owned_tenant_map.get(member.id, []),
            created_at=dt_to_local_str(member.created_at),
        )
        for member in members
    ]


@router.get("/groups", response_model=GroupPageResponse)
async def list_groups(
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Group, User).join(User, Group.owner_id == User.id)
    if keyword:
        text = keyword.strip()
        if text:
            query = query.filter(
                (Group.group_name.like(f"%{text}%"))
                | (User.username.like(f"%{text}%"))
                | (User.phone.like(f"%{text}%"))
            )

    total = query.count()
    rows = (
        query.order_by(Group.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []
    for group, owner in rows:
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
                owner_username=owner.username,
                owner_phone=owner.phone,
                member_count=member_count,
                created_at=dt_to_local_str(group.created_at),
            )
        )

    return GroupPageResponse(total=total, items=items)


@router.get("/groups/{group_id}/members", response_model=GroupMemberPageResponse)
async def list_group_members(
    group_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    query = (
        db.query(User)
        .filter(User.group_id == group.id, User.id != group.owner_id)
        .order_by(User.created_at.desc())
    )
    total = query.count()
    members = query.offset(skip).limit(limit).all()
    items = _build_group_member_items(db, members, group.owner_id)
    return GroupMemberPageResponse(total=total, items=items)


@router.delete("/groups/{group_id}/members/{member_id}")
async def remove_group_member(
    group_id: int,
    member_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

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
            GroupMemberAppBinding.member_id == member.id,
            GroupMemberAppBinding.owner_user_id == group.owner_id,
        )
        .delete(synchronize_session=False)
    )

    member.referral_id = None
    member.group_id = owned_group.id
    db.commit()
    return {"message": "Member removed successfully"}
