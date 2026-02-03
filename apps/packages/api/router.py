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
        data = {}
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
async def health_summary(_: Request) -> HTMLResponse:
    async with httpx.AsyncClient(headers={"user-agent": "healthz-aggregator"}) as client:
        services = await asyncio.gather(*[fetch_health(client, s) for s in SERVICES])

    catalog = _.app.state.catalog
    html = catalog.render("@ui/partials/HealthSummary.jinja", services=services)
    return HTMLResponse(html)


@router.get("/healthz/modal", response_class=HTMLResponse)
async def health_modal(service_id: str) -> HTMLResponse:
    svc = next((s for s in SERVICES if s["id"] == service_id), None)
    if not svc:
        return HTMLResponse("Service not found", status_code=404)

    # reaproveita o fetch para renderizar status atual no modal
    async with httpx.AsyncClient() as client:
        service = await fetch_health(client, svc)

    catalog = request.app.state.catalog
    html = catalog.render("@ui/partials/HealthModal.jinja", service=service)
    return HTMLResponse(html)


@router.get("/healthz/logs", response_class=PlainTextResponse)
async def health_logs(service_id: str) -> PlainTextResponse:
    # aqui você decide de onde vem log:
    # - arquivo / tail / redis / api do serviço / etc
    # Vou simular:
    now = datetime.now().isoformat(timespec="seconds")
    text = f"[{now}] {service_id}: sample log line...\n"
    return PlainTextResponse(text)


@router.get("/healthz/logs/stream")
async def health_logs_stream(service_id: str) -> StreamingResponse:
    async def event_stream():
        while True:
            now = datetime.now().isoformat(timespec="seconds")
            line = f"[{now}] {service_id}: sample log line..."
            yield f"data: {line}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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


@router.get("/partials/confirm-modal", response_class=HTMLResponse)
async def confirm_modal(_: Request) -> HTMLResponse:
    catalog = _.app.state.catalog
    html = catalog.render("@ui/partials/ConfirmModal.jinja")
    return HTMLResponse(html)


@router.post("/actions/confirm", response_class=HTMLResponse)
async def confirm_action(_: Request) -> HTMLResponse:
    catalog = _.app.state.catalog
    toast = catalog.render("@ui/partials/Toast.jinja", message="Ação confirmada com sucesso.")
    html = (
        "<div id=\"modal-portal\" hx-swap-oob=\"true\"></div>"
        + toast
        + "<span id=\"result\" hx-swap-oob=\"true\" class=\"font-medium\">confirmado</span>"
    )
    return HTMLResponse(html)


@router.get("/error", response_class=HTMLResponse)
async def error_page(request: Request) -> HTMLResponse:
    catalog = request.app.state.catalog
    html = catalog.render(
        "@ui/pages/Error.jinja",
        globals={"request": request},
        title="Erro",
        error_title="Erro",
        error_message="Página de erro padrão",
        back_href="/",
    )
    return HTMLResponse(html, status_code=400)


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