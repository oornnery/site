from __future__ import annotations

import asyncio
from datetime import datetime

import httpx
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response, StreamingResponse
from starlette.status import HTTP_404_NOT_FOUND


router = APIRouter()

SERVICES = [
    {"id": "portfolio", "name": "Portfolio", "url": "http://localhost:8000"},
    {"id": "blog", "name": "Blog", "url": "http://localhost:8001"},
    {"id": "admin", "name": "Admin", "url": "http://localhost:8002"},
]


async def fetch_health(client: httpx.AsyncClient, svc: dict) -> dict:
    try:
        r = await client.get(svc["url"] + "/api/healthz", timeout=2.5)
        try:
            data = r.json()
        except Exception:
            data = {}

        ok = (r.status_code == 200) and (data.get("status") == "OK")
        return {
            **svc,
            "ok": ok,
            "status_text": data.get("status") or "UNKNOWN",
            "code": data.get("code") or r.status_code,
            "datetime": data.get("datetime"),
        }
    except Exception:
        return {
            **svc,
            "ok": False,
            "status_text": "ERROR",
            "code": 0,
            "datetime": None,
        }


@router.get("/healthz/summary", response_class=HTMLResponse)
async def health_summary(request: Request) -> HTMLResponse:
    async with httpx.AsyncClient(headers={"user-agent": "healthz-aggregator"}) as client:
        services = await asyncio.gather(*[fetch_health(client, s) for s in SERVICES])

    catalog = request.app.state.catalog
    html = catalog.render("@ui/partials/HealthSummary.jinja", services=services)
    return HTMLResponse(html)


@router.get("/healthz/logs", response_class=PlainTextResponse)
async def health_logs(service_id: str) -> PlainTextResponse:
    svc = next((s for s in SERVICES if s["id"] == service_id), None)
    if not svc:
        return PlainTextResponse(f"Service '{service_id}' not found\n", status_code=404)

    async with httpx.AsyncClient() as client:
        result = await fetch_health(client, svc)

    now = datetime.now().isoformat(timespec="seconds")
    status = "OK" if result["ok"] else result["status_text"]
    text = f"[{now}] {service_id}: status={status} code={result['code']}\n"
    return PlainTextResponse(text)


@router.get("/healthz/logs/stream")
async def health_logs_stream(service_id: str) -> StreamingResponse:
    svc = next((s for s in SERVICES if s["id"] == service_id), None)

    async def event_stream():
        while True:
            if svc:
                async with httpx.AsyncClient() as client:
                    result = await fetch_health(client, svc)
                now = datetime.now().isoformat(timespec="seconds")
                status = "OK" if result["ok"] else result["status_text"]
                line = f'[{now}] {service_id}: {{"status": "{status}", "code": {result["code"]}, "datetime": "{result["datetime"] or now}"}}'
            else:
                now = datetime.now().isoformat(timespec="seconds")
                line = f"[{now}] {service_id}: service not found"
            yield f"data: {line}\n\n"
            await asyncio.sleep(3)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request) -> HTMLResponse:
    catalog = request.app.state.catalog
    html = catalog.render(
        "@ui/pages/Health.jinja",
        globals={"request": request},
        title="Service health",
        summary_url="/healthz/summary",
    )
    return HTMLResponse(html)


def register_not_found_handler(
    app: FastAPI,
    *,
    title: str = "Page Not Found",
    brand: str = "MyApp",
    message: str = "The page you are looking for does not exist.",
    home_route_name: str = "home",
    home_label: str = "Back to home",
) -> None:
    async def handler(request: Request, _exc: Exception) -> Response:
        accept = request.headers.get("accept", "")
        if request.url.path.startswith("/api") or "application/json" in accept:
            return JSONResponse({"detail": "Not Found"}, status_code=HTTP_404_NOT_FOUND)

        catalog = request.app.state.catalog
        html = catalog.render(
            "@ui/pages/Error.jinja",
            globals={"request": request},
            title=title,
            brand=brand,
            message=message,
            home_href=str(request.url_for(home_route_name)),
            home_label=home_label,
        )
        return HTMLResponse(html, status_code=HTTP_404_NOT_FOUND)

    app.add_exception_handler(HTTP_404_NOT_FOUND, handler)
