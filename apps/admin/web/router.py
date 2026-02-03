from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.ui.not_found import render_not_found_html

router = APIRouter()

@router.get("/", response_class=HTMLResponse, name="admin.home")
async def home(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "pages/home.jinja",
        globals={"request": request},
        title="Admin Home",
    )

@router.get(
    "/coming-soon",
    response_class=HTMLResponse,
    include_in_schema=False,
    name="admin.coming_soon",
)
async def coming_soon(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "pages/coming-soon.jinja",
        globals={"request": request},
        title="Admin - Coming soon",
        brand="admin.oornnery.com.br",
        message="This page is not implemented yet.",
    )


@router.get("/404", response_class=HTMLResponse, include_in_schema=False, name="admin.not_found")
async def not_found(request: Request):
    return render_not_found_html(
        request,
        brand="admin.oornnery.com.br",
        title="Admin - Page not found",
        home_href=str(request.url_for("admin.home")),
    )
