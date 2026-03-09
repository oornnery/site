# Security

## Security Model

The project applies security controls in two layers:

1. Edge layer (Traefik in production)
2. Application layer (FastAPI middleware + schema validation)

This provides defense-in-depth for forms and public routes.

## Application-Level Controls

### Middleware controls (`app/core/security.py`)

All custom middleware uses pure ASGI protocol (no `BaseHTTPMiddleware`) for lower
overhead and no request/response buffering.

- `RequestBodySizeLimitMiddleware`
  - Global body size cap via `MAX_REQUEST_BODY_BYTES`
  - Specific cap for `/contact`
  - Validates `Content-Length` header and enforces streaming body limit
- `RequestTracingMiddleware`
  - Request ID propagation (accepts external ID or generates UUID)
  - Trace ID response header when span exists
  - Request metrics lifecycle tracking
  - Skips `/health` to avoid noise
- `SecurityHeadersMiddleware`
  - `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
  - COOP/CORP and `Permissions-Policy`
  - HSTS and strict CSP in production (`DEBUG=false`)
  - Relaxed CSP in development when `DEV_CSP_ENABLED=true` (allows `unsafe-inline`
    for style/script and WebSocket connections for hot reload)
  - Dynamically extends `connect-src` with the configured frontend OTLP collector

### Framework-level controls (`app/main.py`)

- `TrustedHostMiddleware` with `TRUSTED_HOSTS`
- `CORSMiddleware` with explicit allowlists
- SlowAPI default rate limit for all routes (proxy-aware key via `extract_source_ip`)
- Route-specific limit for contact
- `/health` endpoint exempt from rate limiting
- Browser telemetry uses the same-origin proxy route `/otel/v1/traces`,
  which avoids collector-side CORS exposure in the browser

### Form controls

- HMAC-signed CSRF token with expiration
- User-agent bound CSRF validation
- Strict Pydantic validation (`extra="forbid"`)
- Allowed content-type check for form submits

### Content safety

- Markdown output sanitized with nh3 (Rust-based, maintained ammonia bindings)
- Strict tag and attribute allowlists
- URL scheme restriction (`http`, `https`, `mailto`)
- Links annotated with `rel="noopener noreferrer"` automatically

### Privacy controls

- Request/client identifiers hashed before logging
- Contact workflow emits only hashed client identifiers into trace attributes/events

## Edge Controls (Traefik)

From `docker/traefik/dynamic/routing.yml`:

- Global rate limit middleware
- Analytics-specific tighter rate limit
- In-flight request cap
- Body buffering limits
- Analytics IP allowlist

These controls reduce cost and load before requests reach FastAPI.

## OWASP/Pentest Coverage in Tests

Main test suites:

- `tests/test_security_owasp.py`
- `tests/test_security_csrf.py`

Covered scenarios include:

- Security headers presence and CSP restrictions
- CSRF replay/user-agent mismatch and token expiry
- Rate-limit behavior and brute-force pressure
- Oversized payload rejection (`413`)
- Invalid `Content-Length` rejection (`400`)
- Host header hardening (`TrustedHostMiddleware`)
- CORS preflight allowed/blocked behavior
- Removed legacy analytics endpoint returning `404`
- CSP allowing only the configured OTLP collector origin
- Browser OTLP proxy available only when frontend telemetry is enabled
- Injection strings handled as plain data in forms
- Path traversal attempts not exposing filesystem

## Operational Recommendations

- Keep `TRUST_FORWARDED_IP_HEADERS=false` unless behind trusted proxy.
- In production Docker, `--forwarded-allow-ips` is restricted to the internal
  Docker subnet (`172.28.0.0/16`) to prevent header spoofing.
- In production, set `PROD_TRUSTED_HOSTS` and `PROD_CORS_ALLOW_ORIGINS`
  to your public domain(s).
- If browser tracing is enabled, set `PROD_FRONTEND_TELEMETRY_OTLP_ENDPOINT`
  to an HTTPS OTLP HTTP collector and keep CSP strict in production.
- Keep CSP strict in production (`DEBUG=false`).
- Use `DEV_CSP_ENABLED=true` during development for hot reload compatibility.
- Rotate `SECRET_KEY` and keep it out of VCS.
- Maintain edge and app limits aligned to avoid bypass gaps.
