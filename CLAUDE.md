# CLAUDE.md

Self-contained guide for coding agents in this repository.
This file includes the operational guidance that also exists in `CLAUDE.md`, so agents can work without opening it.

## Commands

```bash
uv sync                  # Install/sync dependencies
uv run task dev          # Start all 3 apps via honcho (portfolio:8000, blog:8001, admin:8002)
uv run task fmt          # Format with Ruff
uv run task lint         # Lint with Ruff
uv run task lint-fix     # Lint with autofix
uv run task test         # Run pytest with coverage (currently 43 tests across all apps)
```

Single test example:
`uv run pytest tests/test_apps.py::TestHomePage::test_returns_200 -v`

Dev runtime notes:

- `uv run task dev` uses `honcho` + `Procfile.dev` via `taskipy`.
- Each app runs `uvicorn --reload`.
- `WATCHFILES_FORCE_POLLING=1` is used for WSL2 compatibility.

## Architecture Overview

- Python `3.13` monorepo.
- Stack: FastAPI + Jinja2 + JX + Tailwind CSS (CDN) + HTMX + Alpine.js + Idiomorph.
- Three independent FastAPI apps in `apps/` share code through `apps/packages/`.

Workspace layout:

- `apps/portfolio/` -> Portfolio site (port `8000`)
- `apps/blog/` -> Blog site (port `8001`)
- `apps/admin/` -> Admin panel (port `8002`)
- `apps/packages/` -> Shared catalog, shared API routes, and shared components
- `tests/` -> Pytest suite parametrized across all 3 apps

## App Structure Pattern

Each app follows this layout:

```bash
apps/<app>/
├── app.py           # create_app() factory
├── api/router.py    # REST endpoints under /api
├── web/router.py    # HTML routes returning HTMLResponse
├── components/      # App-specific JX templates for that app
├── static/          # App-specific static files
└── pyproject.toml
```

Factory behavior expectations:

- Create app through `create_app()`.
- Mount static files if present.
- Build catalog and attach to `app.state.catalog`.
- Register `GZipMiddleware`.
- Include app API router, app web router, and shared package router.
- Register custom not-found handler with app-specific home route name.

## JX Catalog and Components

- Catalog builder: `apps/packages/catalog.py`.
- Shared components: `apps/packages/components/` with `@ui` prefix.
- App-level templates: `apps/<app>/components/` (routes render local pages for each app).
- Rendering from Python:
  `catalog.render("pages/Home.jinja", title="My Title")` for app-local pages, or `@ui/...` for shared components.

Shared component tree:

- `layouts/` -> `Layout`, `Navbar`, `Footer`, `Content`
- `pages/` -> `Error`, `Health`
- `partials/` -> `Breadcrumb`, `ThemeToggle`, `Toast`, `HealthSummary`, `HealthAccordion`, `HealthAccordionItem`
- `ui/` -> `Badge`, `Button`, `Card`, `Chip`, `Icon`, `Modal`, `StatusDot`

## Shared API Routes (`apps/packages/api/router.py`)

Routes available to all apps:

- `/api/healthz` -> per-app health check JSON (implemented in each app router)
- `/healthz/summary` -> aggregated health across all 3 apps (HTMX partial polling)
- `/healthz/logs?service_id=X` -> single health check log line
- `/healthz/logs/stream?service_id=X` -> SSE health stream
- `/status` -> health dashboard page with live updates
- `register_not_found_handler()` -> custom 404 (JSON for `/api/*`, HTML otherwise)

## Configuration (pydantic-settings)

Central config lives in `apps/packages/config.py` using `pydantic-settings`.

```python
from apps.packages.config import settings

settings.ENV              # "development" | "production"
settings.SECRET_KEY       # auto-generated in dev, MUST set in prod
settings.DATABASE_URL     # default: sqlite+aiosqlite:///./portfolio.db
settings.PORTFOLIO_URL    # default: http://localhost:8000
settings.BLOG_URL         # default: http://localhost:8001
settings.ADMIN_URL        # default: http://localhost:8002
settings.services         # property: list of {"id", "name", "url"} from the URLs above
settings.is_production    # property shortcut
settings.is_development   # property shortcut
```

Key conventions:

- Single `Settings(BaseSettings)` class with `env_file = ".env"`.
- Sensitive values (`SECRET_KEY`, OAuth secrets) load from env vars — never hardcoded.
- `SECRET_KEY` validator auto-generates a random key in dev with a warning.
- `ALLOWED_HOSTS` validator strips wildcard `"*"` entries.
- App URLs (`PORTFOLIO_URL`, `BLOG_URL`, `ADMIN_URL`) are used by health checks and inter-service calls. Override via env vars for non-default ports or remote deploys.
- `settings.services` property returns the service registry list derived from the URL fields.
- Access the singleton via `from apps.packages.config import settings`.
- Do NOT import `Settings` class directly unless creating test overrides.

Adding new settings:

1. Add field to `Settings` in `apps/packages/config.py` with a sensible default.
2. For secrets, use `str = ""` and add a `@field_validator` that warns in dev.
3. Document the env var in `.env.example` if one exists.
4. Access via `settings.NEW_FIELD` — no need to rebuild; it's a module-level singleton.

## Key Patterns to Preserve

- Async-first:
  async routes, `httpx.AsyncClient`, `asyncio.gather` for concurrent checks.
- App factory:
  build everything in `create_app()`, avoid side effects at import level.
- Route naming:
  keep `name="<app>.home"` convention for 404 navigation.
- Dark mode:
  Alpine `x-data` + localStorage persistence through shared layout/partials.
- HTMX + Alpine integration:
  re-init Alpine after HTMX swaps where needed.
- SSE lifecycle:
  connect/disconnect cleanly and avoid stale EventSource handles.
- OOB updates:
  toast/partial UX uses `hx-swap-oob` patterns.
- Morph swaps:
  use Idiomorph (`morph:innerHTML`) for flicker-free partial refresh.

## Testing

- Framework: `pytest`.
- Pattern: parametrized `client` fixture runs tests against all 3 apps.
- Main test file: `tests/test_apps.py`.
- Shared fixtures: `tests/conftest.py`.
- Run full suite: `uv run task test`.

## Local Skills (`.claude/skills`)

Use these as domain-specific playbooks:

- `jx.md` -> JX fundamentals.
- `jx-components.md` -> project-specific component catalog and conventions.
- `jx-htmx.md` -> HTMX interaction patterns.
- `jx-alpine.md` -> Alpine state and interaction patterns.
- `jx-sse.md` -> SSE implementation patterns.
- `jx-init-project.md` -> JX project scaffolding reference.
- `fastapi.md` -> FastAPI best practices.
- `fastapi-security.md` -> FastAPI security patterns.
- `design-system.md` -> design tokens and UI consistency conventions.

How to pick skills by task:

- Layout/component work -> `jx-components.md` + `design-system.md`
- Dynamic UI flows without heavy custom JS -> `jx-htmx.md` + `jx-alpine.md`
- Real-time updates/log streams -> `jx-sse.md`
- New API/backend work -> `fastapi.md`
- Auth/security hardening -> `fastapi-security.md`
- Core component syntax/usage -> `jx.md`

## Project Conventions

- Keep app-specific pages/layouts inside each app's own `components/`.
- Keep only truly shared primitives/partials/layout shell in `apps/packages/components`.
- Keep web routes in `apps/<app>/web/router.py`.
- Keep API routes in `apps/<app>/api/router.py`.
- Keep handlers/endpoints asynchronous.
- Keep public behavior and docs aligned (`README.md`, `docs/`).

## Pre-Delivery Checklist

- Run lint and tests relevant to your scope.
- Confirm JX rendering still works via `app.state.catalog`.
- Validate cross-app impact when editing `apps/packages/`.
- Update docs if public behavior changes.
