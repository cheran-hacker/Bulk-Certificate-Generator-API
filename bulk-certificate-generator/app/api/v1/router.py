from fastapi import APIRouter
from app.api.v1 import health, jobs, certificates

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(certificates.router, tags=["certificates"])
