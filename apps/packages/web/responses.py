from __future__ import annotations

from fastapi.responses import HTMLResponse


def html(content: str, status_code: int = 200) -> HTMLResponse:
    return HTMLResponse(content=content, status_code=status_code)
