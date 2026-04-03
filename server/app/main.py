from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.user.auth import router as auth_router
from .api.user.tenant import router as tenant_router
from .api.user.stats import router as stats_router
from .api.admin.provider import router as provider_router
from .api.proxy.chat import router as proxy_router
from .core.database import engine, Base

Base.metadata.create_all(bind=engine)

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
app.include_router(provider_router, prefix="/api/admin", tags=["admin"])
app.include_router(proxy_router, prefix="/api/proxy", tags=["proxy"])

@app.get("/")
async def root():
    return {"message": "AI Agent Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
