from __future__ import annotations

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from apps.packages.config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    SKIP_HTMX_VALIDATION = {"/static/", "/favicon.ico", "/health", "/api/healthz"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        if not self._should_skip_htmx_validation(request):
            if not self._validate_htmx_request(request):
                return Response(
                    content="Invalid HTMX request origin",
                    status_code=403,
                    headers={"X-Request-ID": request_id},
                )

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        csp = self._get_production_csp() if settings.is_production else self._get_development_csp()
        response.headers["Content-Security-Policy"] = csp

        return response

    def _should_skip_htmx_validation(self, request: Request) -> bool:
        path = request.url.path
        return any(path.startswith(skip) for skip in self.SKIP_HTMX_VALIDATION)

    def _validate_htmx_request(self, request: Request) -> bool:
        hx_request = request.headers.get("HX-Request")
        if not hx_request:
            return True

        origin = request.headers.get("Origin", "")
        referer = request.headers.get("Referer", "")
        host = request.headers.get("Host", "")

        if origin:
            origin_host = origin.split("://")[-1].split("/")[0]
            if origin_host == host:
                return True
        if referer:
            referer_host = referer.split("://")[-1].split("/")[0]
            if referer_host == host:
                return True

        if settings.is_development and ("localhost" in host or "127.0.0.1" in host):
            return True

        return False

    def _get_production_csp(self) -> str:
        return (
            "default-src 'self'; "
            "script-src 'self' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

    def _get_development_csp(self) -> str:
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws://localhost:* http://localhost:*; "
            "frame-ancestors 'none';"
        )
