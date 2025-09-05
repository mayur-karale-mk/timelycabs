"""
API v1 package
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .health import router as health_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
