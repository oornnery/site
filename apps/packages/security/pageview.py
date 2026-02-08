from __future__ import annotations

import asyncio

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from apps.packages.db.session import async_session_factory
from apps.packages.services import AnalyticsService


class PageviewMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_name: str):
        super().__init__(app)
        self.app_name = app_name

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.method != "GET":
            return response
        if request.url.path.startswith(("/static", "/api/healthz", "/healthz", "/status")):
            return response
        if response.status_code >= 400:
            return response

        client_ip = request.client.host if request.client else None
        referrer = request.headers.get("referer")
        user_agent = request.headers.get("user-agent")

        asyncio.create_task(
            self._store_pageview(
                path=request.url.path,
                referrer=referrer,
                user_agent=user_agent,
                ip=client_ip,
            )
        )
        return response

    async def _store_pageview(self, *, path: str, referrer: str | None, user_agent: str | None, ip: str | None) -> None:
        async with async_session_factory() as session:
            service = AnalyticsService(session)
            await service.track_pageview(
                app_name=self.app_name,
                path=path,
                referrer=referrer,
                user_agent=user_agent,
                ip=ip,
            )
