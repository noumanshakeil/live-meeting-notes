from fastapi import APIRouter
from backend.api import health, live, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(live.router, prefix="/api", tags=["live"])
api_router.include_router(ui.router, tags=["ui"])
