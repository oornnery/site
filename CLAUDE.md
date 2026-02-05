# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run task dev          # Start all 3 apps via honcho (portfolio:8000, blog:8001, admin:8002)
uv run task fmt          # Format with Ruff
uv run task lint         # Lint with Ruff
uv run task lint-fix     # Lint with autofix
uv run task test         # Run pytest with coverage (39 tests across all apps)
```

Single test: `uv run pytest tests/test_apps.py::TestHomePage::test_returns_200 -v`

Install/sync dependencies: `uv sync`

Dev server uses `honcho` to run all 3 apps from `Procfile.dev` with `taskipy`. Each app runs `uvicorn` with `--reload` and `WATCHFILES_FORCE_POLLING=1` for WSL2 compatibility.

## Architecture

Python 3.13 monorepo using **FastAPI** + **Jinja2** + **JX** (component catalog) + **Tailwind CSS** (CDN) + **HTMX** + **Alpine.js** + **Idiomorph**.

### Workspace Layout

Three independent FastAPI apps under `apps/` share code via `apps/packages/`:

- **`apps/portfolio/`** — Portfolio site (port 8000)
- **`apps/blog/`** — Blog (port 8001)
- **`apps/admin/`** — Admin panel (port 8002)
- **`apps/packages/`** — Shared catalog builder, API routes, and UI components
- **`tests/`** — Pytest suite using parametrized fixtures (runs against all 3 apps)

### App Structure Pattern

Every app follows the same layout:

```
apps/<app>/
├── app.py           # create_app() factory
├── api/router.py    # REST endpoints under /api
├── web/router.py    # HTML page routes returning HTMLResponse
├── components/      # App-specific Jinja templates (override shared @ui)
├── static/          # App-specific static files
└── pyproject.toml
```

### JX Component Catalog

Built in `apps/packages/catalog.py`. Shared components live in `apps/packages/components/` with `@ui` prefix. App-specific components in each app's `components/` folder take precedence over shared ones.

Render from Python: `catalog.render("@ui/pages/Home.jinja", title="My Title")`

Shared component tree:
- `layouts/` — Layout (base HTML), Navbar (sticky header), Footer, Content
- `pages/` — Home (hello world), Error (404 centered), Health (live status dashboard)
- `partials/` — Breadcrumb, ThemeToggle, Toast (OOB), HealthSummary, HealthAccordion, HealthAccordionItem
- `ui/` — Badge, Button (link/button), Card (with slots), Modal (Alpine), StatusDot

### Shared API Routes (`apps/packages/api/router.py`)

Endpoints available to all apps:
- `/api/healthz` — per-app health check (each app's own `api/router.py`)
- `/healthz/summary` — aggregated health across all 3 apps (HTMX partial, polls every 10s)
- `/healthz/logs?service_id=X` — single health check for a service
- `/healthz/logs/stream?service_id=X` — SSE stream with real healthz JSON per app
- `/status` — full health status page with live accordion + SSE log streaming
- `register_not_found_handler()` — custom 404 (JSON for `/api/*`, HTML otherwise)

### Key Patterns

- **Async throughout**: async routes, httpx.AsyncClient for inter-service calls, asyncio.gather for concurrent health checks
- **App factory**: `create_app()` mounts statics, builds JX catalog on `app.state.catalog`, registers GZip middleware and routers
- **Route naming**: `name="app.home"` convention (used by 404 handler for navigation links)
- **Dark mode**: Alpine.js `x-data` on body + localStorage persistence, ThemeToggle partial
- **HTMX + Alpine**: Layout re-initializes Alpine on `htmx:afterSwap` for injected content
- **SSE lifecycle**: HealthAccordionItem connects/disconnects EventSource on toggle, cleans up on `htmx:before-swap`
- **Toast OOB**: Toast component uses `hx-swap-oob="true"` targeting `#toast-portal` in Layout
- **Morph swaps**: Health summary uses `hx-swap="morph:innerHTML"` via Idiomorph for flicker-free updates

### Testing

Tests use `pytest` with a parametrized `client` fixture that runs each test against all 3 apps. Add new tests in `tests/test_apps.py`. Fixtures defined in `tests/conftest.py`.
