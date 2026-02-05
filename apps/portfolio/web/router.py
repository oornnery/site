from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="portfolio.home")
async def home(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "@ui/pages/Home.jinja",
        globals={"request": request},
        title="Portfolio",
        brand="Portfolio",
        heading="Portfolio",
        description="Welcome to the portfolio. Start building your projects showcase here.",
    )
