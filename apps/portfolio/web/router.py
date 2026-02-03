from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.ui.coming_soon import render_coming_soon_html
from apps.ui.not_found import render_not_found_html

router = APIRouter()

@router.get("/", response_class=HTMLResponse, name="portfolio.home")
async def home(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "pages/home.jinja",
        globals={"request": request},
        title="Portfolio Home",
    )

@router.get(
    "/coming-soon",
    response_class=HTMLResponse,
    include_in_schema=False,
    name="portfolio.coming_soon",
)
async def coming_soon(request: Request):
    return render_coming_soon_html(
        request,
        brand="portfolio.oornnery.com.br",
        title="Portfolio - Coming soon",
        home_href=str(request.url_for("portfolio.home")),
    )


@router.get("/404", response_class=HTMLResponse, include_in_schema=False, name="portfolio.not_found")
async def not_found(request: Request):
    return render_not_found_html(
        request,
        brand="portfolio.oornnery.com.br",
        title="Portfolio - Page not found",
        home_href=str(request.url_for("portfolio.home")),
    )
