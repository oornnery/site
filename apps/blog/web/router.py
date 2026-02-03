from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.ui.api.router import build_health_router
from ..api.router import healthz as api_healthz

router = APIRouter()
router.include_router(
    build_health_router(
        api_healthz=api_healthz,
        title="Blog health",
        brand="Blog",
    )
)

@router.get("/", response_class=HTMLResponse, name="blog.home")
async def home(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "pages/home.jinja",
        globals={"request": request},
        title="Blog Home",
    )
