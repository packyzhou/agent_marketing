from fastapi import APIRouter
from .provider import router as provider_router
from .users import router as users_router
from .tenants import router as tenants_router
from .tokens import router as tokens_router
from .memory import router as memory_router
from .groups import router as groups_router
from .roles import router as roles_router
from .system_prompt import router as system_prompt_router

router = APIRouter()

router.include_router(provider_router, tags=["admin-providers"])
router.include_router(users_router, tags=["admin-users"])
router.include_router(roles_router, tags=["admin-roles"])
router.include_router(groups_router, tags=["admin-groups"])
router.include_router(tenants_router, tags=["admin-tenants"])
router.include_router(tokens_router, tags=["admin-tokens"])
router.include_router(memory_router, tags=["admin-memory"])
router.include_router(system_prompt_router, tags=["admin-system-prompts"])
