python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import org_routes, id_routes, file_routes
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="组织治理与文件管理系统", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(org_routes.router)
app.include_router(id_routes.router)
app.include_router(file_routes.router)

@app.get("/")
async def root():
    return {
        "message": "组织治理与文件管理系统 API",
        "docs": "/docs"
    }

@app.on_event("shutdown")
async def shutdown_db():
    dag_service.close()
