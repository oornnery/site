import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse

from app.core.deps import get_about_page_service
from app.core.rendering import get_lang, render_page
from app.services import AboutPageService

router = APIRouter(prefix="/about", tags=["about"])
logger = logging.getLogger(__name__)

AboutPageServiceDep = Annotated[AboutPageService, Depends(get_about_page_service)]

_RESUME_PATH = Path(__file__).resolve().parents[2] / "content" / "about.md"


@router.get("", response_class=HTMLResponse)
async def about(
    request: Request,
    page_service: AboutPageServiceDep,
) -> HTMLResponse:
    lang = get_lang(request)
    page = page_service.build_page(lang=lang)
    logger.debug("About page rendered.")
    return render_page(page, lang=lang)


@router.get("/resume.md", response_class=FileResponse)
async def download_resume() -> FileResponse:
    return FileResponse(
        path=_RESUME_PATH,
        media_type="text/markdown",
        filename="fabio-souza-resume.md",
    )
