from fastapi import APIRouter

from . import about, blog, contact, home, projects

views_router = APIRouter()
views_router.include_router(home.router)
views_router.include_router(about.router)
views_router.include_router(projects.router)
views_router.include_router(blog.router)
views_router.include_router(contact.router)
