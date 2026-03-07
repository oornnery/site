from fastapi import APIRouter

from . import about, analytics, blog, contact, health, home, projects

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(home.router)
api_router.include_router(about.router)
api_router.include_router(projects.router)
api_router.include_router(blog.router)
api_router.include_router(contact.router)
api_router.include_router(analytics.router)
