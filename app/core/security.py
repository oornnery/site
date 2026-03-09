import hashlib
import hmac
import logging
import secrets
import time
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import Request
from opentelemetry.trace import get_current_span
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.logger import bind_request_context, event_message, reset_request_context
from app.observability.events import LogEvent
from app.observability.metrics import get_app_metrics

logger = logging.getLogger(__name__)

_TRACING_SKIP_PATHS = frozenset({"/health"})


def _csrf_user_agent_hash(user_agent: str) -> str:
    normalized = user_agent.strip().lower()
    if not normalized:
        return "na"
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _anonymize_identifier(value: str, *, namespace: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return "unknown"
    digest = hmac.new(
        settings.secret_key.encode(),
        f"{namespace}:{normalized}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return digest[:16]


def generate_csrf_token(*, user_agent: str = "") -> str:
    """Generate a timestamped CSRF token signed with HMAC-SHA256."""
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    user_agent_hash = _csrf_user_agent_hash(user_agent)
    payload = f"{timestamp}:{random_part}:{user_agent_hash}"
    signature = hmac.new(
        settings.secret_key.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def validate_csrf_token(token: str, *, user_agent: str = "") -> bool:
    """Validate CSRF token signature and expiry."""
    try:
        parts = token.rsplit(":", 3)
        if len(parts) != 4:
            logger.debug("CSRF token has an invalid format.")
            return False
        timestamp_str, random_part, user_agent_hash, signature = parts
        payload = f"{timestamp_str}:{random_part}:{user_agent_hash}"
        expected = hmac.new(
            settings.secret_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            logger.debug("CSRF token signature validation failed.")
            return False

        timestamp = int(timestamp_str)
        age = time.time() - timestamp
        if age < 0:
            logger.debug("CSRF token timestamp is in the future.")
            return False
        if age > settings.csrf_token_expiry:
            logger.debug(f"CSRF token expired (age={age:.2f}s).")
            return False
        expected_user_agent_hash = _csrf_user_agent_hash(user_agent)
        if not hmac.compare_digest(user_agent_hash, expected_user_agent_hash):
            logger.debug("CSRF token user-agent binding validation failed.")
            return False
    except (TypeError, ValueError):
        logger.debug("CSRF token parsing failed.")
        return False
    return True


def is_allowed_form_content_type(content_type: str) -> bool:
    normalized = content_type.strip().lower()
    if not normalized:
        return False
    return normalized.startswith(
        ("application/x-www-form-urlencoded", "multipart/form-data")
    )


def extract_source_ip(request: Request) -> str:
    if settings.trust_forwarded_ip_headers:
        x_forwarded_for = request.headers.get("x-forwarded-for", "").strip()
        if x_forwarded_for:
            return x_forwarded_for.split(",", 1)[0].strip()
        x_real_ip = request.headers.get("x-real-ip", "").strip()
        if x_real_ip:
            return x_real_ip
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _frontend_telemetry_connect_sources() -> tuple[str, ...]:
    if not settings.frontend_telemetry_is_enabled():
        return ()

    endpoint = settings.frontend_telemetry_browser_endpoint().strip()
    if not endpoint:
        return ()

    parsed = urlsplit(endpoint)
    if not parsed.scheme or not parsed.netloc:
        return ()
    if parsed.scheme not in {"http", "https"}:
        return ()
    return (f"{parsed.scheme}://{parsed.netloc}",)


def _content_security_policy(*, dev_mode: bool) -> str:
    connect_sources = ["'self'"]
    connect_sources.extend(_frontend_telemetry_connect_sources())
    if dev_mode:
        connect_sources.extend(["ws:", "wss:"])

    directives = [
        "default-src 'self'",
        "style-src 'self'" + (" 'unsafe-inline'" if dev_mode else ""),
        "script-src 'self'" + (" 'unsafe-inline'" if dev_mode else ""),
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        f"connect-src {' '.join(dict.fromkeys(connect_sources))}",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
        "frame-src 'none'",
    ]
    return "; ".join(directives)


def _body_size_limit_for_path(path: str) -> int:
    if path == "/contact":
        return settings.contact_max_body_bytes
    return settings.max_request_body_bytes


class _BodyTooLargeError(Exception):
    pass


class RequestBodySizeLimitMiddleware:
    """Reject requests with bodies larger than configured limits."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method", "GET") not in {
            "POST",
            "PUT",
            "PATCH",
        }:
            await self.app(scope, receive, send)
            return

        limit = _body_size_limit_for_path(scope["path"])
        headers = Headers(scope=scope)
        content_length_value = headers.get("content-length", "").strip()

        if content_length_value:
            try:
                content_length = int(content_length_value)
            except ValueError:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header."},
                )
                await response(scope, receive, send)
                return
            if content_length > limit:
                response = JSONResponse(
                    status_code=413,
                    content={"detail": "Request body is too large."},
                )
                await response(scope, receive, send)
                return

        body_size = 0

        async def receive_with_limit() -> Message:
            nonlocal body_size
            message = await receive()
            if message["type"] == "http.request":
                body_size += len(message.get("body", b""))
                if body_size > limit:
                    raise _BodyTooLargeError()
            return message

        try:
            await self.app(scope, receive_with_limit, send)
        except _BodyTooLargeError:
            response = JSONResponse(
                status_code=413,
                content={"detail": "Request body is too large."},
            )
            await response(scope, receive, send)


class RequestTracingMiddleware:
    """Attach trace context to each request and emit request lifecycle logs."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if scope["path"] in _TRACING_SKIP_PATHS:
            await self.app(scope, receive, send)
            return

        app_metrics = get_app_metrics()
        request = Request(scope)
        request_id = (
            request.headers.get(settings.request_id_header, "").strip() or uuid4().hex
        )
        raw_client_ip = request.client.host if request.client else "unknown"
        client_ip = _anonymize_identifier(raw_client_ip, namespace="ip")
        tokens = bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )
        scope.setdefault("state", {})["request_id"] = request_id

        started_at = time.perf_counter()
        route_path = request.url.path
        app_metrics.request_started(method=request.method, path=route_path)
        logger.info(event_message(LogEvent.REQUEST_STARTED, route=route_path))

        status_code = 500
        exception_class = ""
        exc_to_raise: BaseException | None = None

        async def send_with_tracing(message: Message) -> None:
            nonlocal status_code, route_path
            if message["type"] == "http.response.start":
                status_code = message["status"]
                route = scope.get("route")
                if route is not None:
                    route_path = getattr(route, "path", route_path)
                headers = MutableHeaders(scope=message)
                headers.append(settings.request_id_header, request_id)
                span_context = get_current_span().get_span_context()
                if span_context.is_valid:
                    headers.append("X-Trace-ID", f"{span_context.trace_id:032x}")
            await send(message)

        try:
            await self.app(scope, receive, send_with_tracing)
        except Exception as exc:
            exception_class = exc.__class__.__name__
            exc_to_raise = exc
        finally:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            if exc_to_raise is not None:
                logger.exception(
                    event_message(
                        LogEvent.REQUEST_FAILED,
                        route=route_path,
                        duration_ms=f"{elapsed_ms:.2f}",
                        error=exception_class,
                    )
                )
            else:
                logger.info(
                    event_message(
                        LogEvent.REQUEST_COMPLETED,
                        route=route_path,
                        status_code=status_code,
                        duration_ms=f"{elapsed_ms:.2f}",
                    )
                )
            app_metrics.request_finished(
                method=scope.get("method", "GET"),
                path=route_path,
                status_code=status_code,
                duration_ms=elapsed_ms,
                exception_class=exception_class,
            )
            reset_request_context(tokens)

        if exc_to_raise is not None:
            raise exc_to_raise


class SecurityHeadersMiddleware:
    """Add baseline security headers to every response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "DENY")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
                headers.append("Cross-Origin-Opener-Policy", "same-origin")
                headers.append("Cross-Origin-Resource-Policy", "same-origin")
                headers.append(
                    "Permissions-Policy",
                    "camera=(), microphone=(), geolocation=()",
                )
                if not settings.debug:
                    headers.append(
                        "Strict-Transport-Security",
                        "max-age=63072000; includeSubDomains; preload",
                    )
                    headers.append(
                        "Content-Security-Policy",
                        _content_security_policy(dev_mode=False),
                    )
                elif settings.dev_csp_enabled:
                    headers.append(
                        "Content-Security-Policy",
                        _content_security_policy(dev_mode=True),
                    )
            await send(message)

        await self.app(scope, receive, send_with_headers)
