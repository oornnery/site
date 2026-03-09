import logging

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

router = APIRouter(prefix="/otel", tags=["telemetry"])
logger = logging.getLogger(__name__)


def _forward_headers(request: Request) -> dict[str, str]:
    forwarded: dict[str, str] = {}
    for header_name in ("content-type", "content-encoding", "user-agent"):
        value = request.headers.get(header_name, "").strip()
        if value:
            forwarded[header_name] = value
    return forwarded


@router.post("/v1/traces")
async def forward_frontend_traces(request: Request) -> Response:
    collector_endpoint = settings.frontend_telemetry_collector_endpoint()
    if not settings.frontend_telemetry_is_enabled() or not collector_endpoint:
        return Response(status_code=404)

    payload = await request.body()
    headers = _forward_headers(request)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.post(
                collector_endpoint,
                content=payload,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        logger.warning(
            "Frontend telemetry forward failed endpoint=%s error=%s",
            collector_endpoint,
            exc.__class__.__name__,
        )
        return Response(status_code=502)

    response_headers: dict[str, str] = {}
    content_type = upstream.headers.get("content-type", "").strip()
    if content_type:
        response_headers["content-type"] = content_type

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
