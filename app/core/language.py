from __future__ import annotations

import logging
from typing import Any, Callable

from app.core.config import settings

logger = logging.getLogger(__name__)

Scope = dict[str, Any]
Receive = Callable[..., Any]
Send = Callable[..., Any]
ASGIApp = Callable[..., Any]

_SKIP_PREFIXES = ("/static/", "/health", "/otel/", "/docs", "/openapi.json")


class LanguageMiddleware:
    """Pure ASGI middleware that extracts language from URL prefix.

    Routes like ``/{lang}/about`` get the ``lang`` segment extracted and
    stored in ``scope["state"]["lang"]``.  The URL is rewritten to strip the
    language prefix so downstream routing doesn't need to know about it.

    Requests to ``/`` are redirected to ``/{default_language}/``.
    Paths that don't start with a known language prefix fall through with
    the default language set.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._default_lang = settings.default_language
        self._supported = set(settings.supported_languages)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "/")

        if any(path.startswith(prefix) for prefix in _SKIP_PREFIXES):
            scope.setdefault("state", {})["lang"] = self._default_lang
            await self.app(scope, receive, send)
            return

        if path == "/":
            await self._redirect(scope, send, f"/{self._default_lang}/")
            return

        lang, remaining = self._extract_lang(path)
        if lang:
            scope.setdefault("state", {})["lang"] = lang
            scope["path"] = remaining or "/"
            if scope.get("raw_path"):
                scope["raw_path"] = (remaining or "/").encode("utf-8")
        else:
            scope.setdefault("state", {})["lang"] = self._default_lang

        await self.app(scope, receive, send)

    def _extract_lang(self, path: str) -> tuple[str | None, str]:
        parts = path.strip("/").split("/", 1)
        if not parts:
            return None, path

        candidate = parts[0].lower()
        if candidate in self._supported:
            remaining = "/" + parts[1] if len(parts) > 1 else "/"
            return candidate, remaining

        return None, path

    @staticmethod
    async def _redirect(scope: Scope, send: Send, location: str) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": 302,
                "headers": [
                    [b"location", location.encode("utf-8")],
                    [b"content-length", b"0"],
                ],
            }
        )
        await send({"type": "http.response.body", "body": b""})
