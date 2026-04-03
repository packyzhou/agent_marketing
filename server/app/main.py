from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .api.user.auth import router as auth_router
from .api.user.tenant import router as tenant_router
from .api.user.stats import router as stats_router
from .api.admin import router as admin_router
from .api.proxy.chat import router as proxy_router
from .core.database import engine, Base

Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS tb_group_member_app_binding (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            owner_user_id BIGINT NOT NULL,
            member_id BIGINT NOT NULL,
            app_key VARCHAR(64) NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_owner_user_id (owner_user_id),
            INDEX idx_member_id (member_id),
            INDEX idx_binding_app_key (app_key),
            UNIQUE KEY uk_owner_member (owner_user_id, member_id)
        )
    """))
    conn.execute(text("""
        DELETE p1 FROM tb_provider_key p1
        INNER JOIN tb_provider_key p2
        ON p1.app_key = p2.app_key AND p1.id < p2.id
    """))
    index_exists = conn.execute(text("""
        SELECT COUNT(1)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'tb_provider_key'
          AND index_name = 'uk_app_key'
    """)).scalar()
    if not index_exists:
        conn.execute(text("""
            ALTER TABLE tb_provider_key
            ADD UNIQUE KEY uk_app_key (app_key)
        """))

app = FastAPI(title="AI Agent Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tenant_router, prefix="/api/user", tags=["tenant"])
app.include_router(stats_router, prefix="/api/user", tags=["stats"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(proxy_router, prefix="/api/proxy", tags=["proxy"])

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
