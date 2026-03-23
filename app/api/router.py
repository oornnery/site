from fastapi import APIRouter

from . import health, telemetry

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(telemetry.router)
