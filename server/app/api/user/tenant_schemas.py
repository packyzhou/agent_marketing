from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GroupUserBinding(BaseModel):
    user_id: int
    real_name: str
    phone: str

class TenantCreate(BaseModel):
    tenant_name: str
    bind_group_users: bool = False
    binding_user_ids: Optional[List[int]] = None

class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = None
    status: Optional[str] = None
    binding_user_ids: Optional[List[int]] = None

class TenantResponse(BaseModel):
    app_key: str
    app_secret: str
    user_id: int
    tenant_name: Optional[str]
    group_binding_json: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProviderKeyCreate(BaseModel):
    provider_id: int
    api_key: str
    model_name: Optional[str] = None

class ProviderKeyResponse(BaseModel):
    id: int
    app_key: str
    provider_id: int
    api_key: str
    model_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProviderResponse(BaseModel):
    id: int
    name: str
    code: str
    base_url: str
    config_guide: Optional[str]
    status: str

    class Config:
        from_attributes = True
