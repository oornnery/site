from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="admin.home")
async def home(request: Request):
    catalog = request.app.state.catalog
    return catalog.render(
        "@ui/pages/Home.jinja",
        globals={"request": request},
        title="Admin",
        brand="Admin",
        heading="Admin",
        description="Welcome to the admin panel. Manage your site from here.",
    )
